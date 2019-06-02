# To use these settings during development, run with
# python manage.py runserver --settings=autojudge.settings_production

import os
from typing import List
from .settings import *  # noqa: F401, F403

SECRET_KEY = os.environ.get('AUTOJUDGE_SECRET_KEY')
DEBUG = False

# Edit/Add the settings during deployment
ALLOWED_HOSTS: List[str] = ['autojudge.iith.ac.in']

# Confiure Postgresql as database
# https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-DATABASES

# Configure static root and static url
# https://docs.djangoproject.com/en/2.2/howto/static-files/deployment/#serving-static-files-in-production
