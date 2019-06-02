# To use these settings during development, run with
# python manage.py runserver --settings=autojudge.settings_production

import os
from typing import List
from .settings import *

SECRET_KEY = os.environ.get('AUTOJUDGE_SECRET_KEY')
DEBUG = False

# TODO Edit the url
ALLOWED_HOSTS: List[str] = ['autojudge.iith.ac.in']

# TODO Confiure Postgrsql as database

# TODO Configure static root and static url
