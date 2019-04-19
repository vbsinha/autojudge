from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Contest)
admin.site.register(Problem)
admin.site.register(Person)
admin.site.register(TestCase)
admin.site.register(Submission)
admin.site.register(SubmissionTestCase)
