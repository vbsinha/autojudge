import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdpjudge.settings")
django.setup()

from judge import models


def f():
    print('Hi')
    p = models.Person(email='blal')
    p.save()
    print(models.Person.objects.all())


f()
