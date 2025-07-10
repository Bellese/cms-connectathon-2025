"""
Configuration for FHIR server interactions.
Defines and returns the base URL for posting testcases.
"""
from typing import Dict


def load_config() -> Dict[str, str]:
    """
    Return configuration mapping for FHIR interactions.

    Returns:
        dict: Contains 'server_url'.
    """
    return {
        'server_url': 'https://connectathon.fhir-sandbox.bellese.dev/fhir'
    }
    