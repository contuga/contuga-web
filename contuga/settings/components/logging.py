import os

import rollbar

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_PATH)

ROLLBAR = {
    "access_token": "5887794445d748cb98df0cbed080c9df",
    "environment": "production",
    "root": BASE_DIR,
    "hostSafeList": "www.contuga.eu",
}

rollbar.init(**ROLLBAR)
