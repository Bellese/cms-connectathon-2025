#!/usr/bin/env python3
"""
Fetch and validate FHIR MeasureReport resources for each uploaded testcase.
"""
import argparse
import logging
import re
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
    parser = argparse.ArgumentParser(
        description="Evaluate FHIR MeasureReports against expected populations encoded in filenames"
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
    return [p for p in sorted(root.iterdir()) if p.is_dir()]


def evaluate_testcases(measure_dir: Path, session: requests.Session, base_url: str):
    """
    For each JSON test file in measure_dir:
      - Parse expected population code from filename (e.g. 'denom', 'denomexcept').
      - Fetch corresponding MeasureReport by resource id (stem of filename).
      - Compare the report.population count for expected code > 0.
    Returns:
      Tuple[int, int]: (pass_count, fail_count)
    """
    pass_count = fail_count = 0
    for file_path in sorted(measure_dir.glob('*.json')):
        # Extract expected code from filename
        m = re.search(r"-(?P<exp>[A-Za-z0-9_]+)\.json$", file_path.name)
        if not m:
            logger.error("Cannot parse expected result from %s", file_path.name)
            fail_count += 1
            continue
        expected_code = m.group('exp').lower()
        report_id = file_path.stem

        # GET MeasureReport/{id}
        resp = session.get(f"{base_url}/MeasureReport/{report_id}")
        if not resp.ok:
            logger.error("Failed to fetch report %s: %s", report_id, resp.status_code)
            fail_count += 1
            continue

        report = resp.json()
        # Inspect first group populations
        groups = report.get('group', [])
        if not groups:
            logger.error("No groups in report %s", report_id)
            fail_count += 1
            continue
        populations = groups[0].get('population', [])

        # Find matching population entry by code
        match = next(
            (p for p in populations
             if p.get('code',{}).get('coding',[{}])[0].get('code','').lower() == expected_code),
            None
        )
        if match and match.get('count', 0) > 0:
            logger.info("%s: expected %s, count=%s", file_path.name, expected_code, match.get('count'))
            pass_count += 1
        else:
            logger.warning(
                "%s: expected %s but no count>0", file_path.name, expected_code
            )
            fail_count += 1
    return pass_count, fail_count


def main():
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    root = args.root_dir
    if not root.is_dir():
        logger.error("'%s' is not a directory", root)
        sys.exit(1)

    config = load_config()
    base_url = config['server_url']
    session = requests.Session()
    session.headers.update({'Accept': 'application/fhir+json'})

    total_pass = total_fail = 0
    for measure_dir in find_measure_dirs(root):
        logger.info("Evaluating measure: %s", measure_dir.name)
        p, f = evaluate_testcases(measure_dir, session, base_url)
        total_pass += p
        total_fail += f

    logger.info("Evaluation completed: %d passed, %d failed", total_pass, total_fail)
    sys.exit(0 if total_fail == 0 else 2)

if __name__ == '__main__':
    main()