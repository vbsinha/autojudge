from django.contrib import admin

# Register your models here.
from .models import Contest, Problem, Person
from .models import Submission, ContestPerson, TestCase, SubmissionTestCase, Comment


class ContestAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(Contest, ContestAdmin)
admin.site.register(Problem)
admin.site.register(Person)
admin.site.register(Submission)
admin.site.register(ContestPerson)
admin.site.register(TestCase)
admin.site.register(SubmissionTestCase)
admin.site.register(Comment)
