import os
import django

from subprocess import call

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdpjudge.settings")
django.setup()

from judge import models

MONITOR_DIRECTORY = os.path.join('content', 'tmp')
DOCKER_IMAGE_NAME = 'pdp_docker'

LS = []
REFRESH_LS_TRIGGER = 10

while True:
    if len(LS) < REFRESH_LS_TRIGGER:
        LS = [os.path.join(MONITOR_DIRECTORY, sub_file) for sub_file in os.listdir(MONITOR_DIRECTORY)]
        LS.sort(key=os.path.getctime)
    sub_file = LS[0]  # The first file submission-wise
    sub_id = os.path.basename(sub_file)[8:-4]  # This is the submission ID

    # Move to content
    os.chdir('content')

    # Run docker image
    call(['docker', 'run', '--rm',
          '-v', '$(pwd):/app', '-e', 'SUB_ID={}'.format(sub_id), DOCKER_IMAGE_NAME])

    saver(sub_id)
    LS.remove(sub_file)
