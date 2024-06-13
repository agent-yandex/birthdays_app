"""This module is responsible for loading environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.environ.get("PG_HOST")
PG_PORT = os.environ.get("PG_PORT")
PG_USER = os.environ.get("PG_USER")
PG_PASSWORD = os.environ.get("PG_PASSWORD")
PG_DBNAME = os.environ.get("PG_DBNAME")

PG_HOST_TEST = os.environ.get("PG_HOST_TEST")
PG_PORT_TEST = os.environ.get("PG_PORT_TEST")
PG_USER_TEST = os.environ.get("PG_USER_TEST")
PG_PASSWORD_TEST = os.environ.get("PG_PASSWORD_TEST")
PG_DBNAME_TEST = os.environ.get("PG_DBNAME_TEST")

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
