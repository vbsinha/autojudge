import os
from typing import List
from .settings import *

SECRET_KEY = os.environ.get('AUTOJUDGE_SECRET_KEY')
DEBUG = False

# Edit this in production
ALLOWED_HOSTS: List[str] = ['autojudge.iith.ac.in']

# TODO Confiure Postgreql as database
