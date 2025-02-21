import logging
from pathlib import Path

from demisto_sdk.commands.common.constants import TESTS_DIR
from demisto_sdk.commands.common.tools import get_content_path

logger = logging.getLogger("demisto-sdk")

CONTENT_PATH = Path(get_content_path())  # type: ignore

ALL_PACKS_DEPENDENCIES_DEFAULT_PATH = CONTENT_PATH / "all_packs_dependencies.json"

CONF_PATH = CONTENT_PATH / TESTS_DIR / "conf.json"

DEFAULT_ID_SET_PATH = CONTENT_PATH / TESTS_DIR / "id_set.json"
MP_V2_ID_SET_PATH = CONTENT_PATH / TESTS_DIR / "id_set_mp_v2.json"
XPANSE_ID_SET_PATH = CONTENT_PATH / TESTS_DIR / "id_set_xpanse.json"
LANDING_PAGE_SECTIONS_PATH = (
    CONTENT_PATH / TESTS_DIR / "Marketplace" / "landingPage_sections.json"
)


PYTHONPATH = [
    Path(CONTENT_PATH),
    Path(CONTENT_PATH / "Packs" / "Base" / "Scripts" / "CommonServerPython"),
    Path(CONTENT_PATH / TESTS_DIR / "demistomock"),
    Path(__file__).parent.parent / "lint" / "resources" / "pylint_plugins",
]
try:
    PYTHONPATH.extend(Path(CONTENT_PATH / "Packs" / "ApiModules" / "Scripts").iterdir())
except FileNotFoundError:
    logger.info("ApiModules not found, skipping adding to PYTHONPATH")
    pass
