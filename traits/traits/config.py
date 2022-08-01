
from pathlib import Path
import logging
import sys
import toml
import yaml
import os
from dotenv import load_dotenv
from pint import UnitRegistry
import http.client

http.client.HTTPConnection.debuglevel = 1

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(ROOT_DIR / 'data')
RAW_DATA_DIR = Path(DATA_DIR / 'raw')
PROCESSED_DATA_DIR = Path(DATA_DIR / 'processed')

CACHE_DIR = Path(ROOT_DIR / '.cache')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = Path(ROOT_DIR / '.log')
LOG_DIR.mkdir(parents=True, exist_ok=True)

ADEPT_DIR = Path(ROOT_DIR / 'adept')


ASSETS_DIR = Path(ADEPT_DIR / 'assets')
CORPUS_DIR = Path(ADEPT_DIR / 'corpus')

spacy_config = yaml.safe_load((ADEPT_DIR / 'project.yml').open()).get('vars', {})
app_config = toml.load(ROOT_DIR / 'pyproject.toml')



# BHL_API_KEY = os.getenv('BHL_API_KEY')

# MONGO_CONNECTION_STRING = "mongodb://root:pass@localhost:27017"

unit_registry = UnitRegistry()

measurement_units = ['cm', 'mm', 'm']


DEBUG = os.getenv('DEBUG')

# Set up logging
logging.root.handlers = []

logger = logging.getLogger()

# Capture all log levels, but handler below set their own levels
logger.setLevel(logging.DEBUG)

# Set up file logging for errors and warnings
file_handler = logging.FileHandler(LOG_DIR / 'error.log')
file_handler.setFormatter(
    logging.Formatter("[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s")
)
# Log errors to files
file_handler.setLevel(logging.WARNING)
logger.addHandler(file_handler)

# set up logging to console
console_handler = logging.StreamHandler()
# Simpler console utput
console_handler.setFormatter(
    logging.Formatter('%(levelname)-8s %(message)s')
)
# Log debug+ to console
console_handler.setLevel(logging.DEBUG if DEBUG else logging.INFO)
logger.addHandler(console_handler)


# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True






