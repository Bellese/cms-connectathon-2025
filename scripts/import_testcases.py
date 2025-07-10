"""
Import FHIR JSON testcases to a FHIR server.
Walk through a directory of measure folders and POST each JSON file.
"""
import argparse
import json
import logging
import sys
from pathlib import Path

import requests
from config.config import load_config

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def parse_args():
    """
    Parse command-line arguments.
    Returns:
        Namespace with 'root_dir' (Path) and 'verbose' (bool).
    """
    parser = argparse.ArgumentParser(
        description="Import FHIR JSON testcases to a FHIR server (default folder: test/)"
    )
    parser.add_argument(
        'root_dir', type=Path, nargs='?', default=Path('test'),
        help='Directory containing measure subfolders'
    )
    parser.add_argument(
        '--verbose', action='store_true', help='Enable debug logging'
    )
    return parser.parse_args()


def find_measure_dirs(root: Path):
    """
    Return all measure subdirectory Paths under the test root.
    """
    return [p for p in sorted(root.iterdir()) if p.is_dir()]


def upload_testcases(measure_dir: Path, session: requests.Session, url: str):
    """
    POST each JSON file in measure_dir using the provided session.

    Returns:
        Tuple[int, int]: counts of (successes, failures)
    """
    succ = fail = 0
    for file_path in sorted(measure_dir.glob('*.json')):
        try:
            payload = json.loads(file_path.read_text())
            resp = session.post(url, json=payload)
            if resp.ok:
                logger.info("Uploaded %s: %s", file_path.name, resp.status_code)
                succ += 1
            else:
                logger.warning("Failed %s: %s", file_path.name, resp.status_code)
                fail += 1
        except Exception as err:
            logger.error("Error %s: %s", file_path.name, err)
            fail += 1
    return succ, fail


def main():
    """
    Main entry point: parse args, configure session, and upload testcases.
    """
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    root = args.root_dir
    if not root.is_dir():
        logger.error("'%s' is not a directory", root)
        sys.exit(1)

    config = load_config()
    url = config['server_url']
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/fhir+json'})

    total_success = total_failure = 0
    for measure_dir in find_measure_dirs(root):
        logger.info("Processing measure: %s", measure_dir.name)
        succ, fail = upload_testcases(measure_dir, session, url)
        total_success += succ
        total_failure += fail

    logger.info("Completed: %d succeeded, %d failed", total_success, total_failure)
    sys.exit(0 if total_failure == 0 else 2)


if __name__ == '__main__':
    main()
