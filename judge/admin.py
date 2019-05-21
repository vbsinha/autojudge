from django.contrib import admin

# Register your models here.
from .models import Contest, Problem, Person, Submission, TestCase, Comment
from .models import ContestPerson, SubmissionTestCase, PersonProblemFinalScore


class ContestAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(Contest, ContestAdmin)
admin.site.register(Problem)
admin.site.register(Person)
admin.site.register(Submission)
admin.site.register(TestCase)
admin.site.register(Comment)
admin.site.register(ContestPerson)
admin.site.register(SubmissionTestCase)
admin.site.register(PersonProblemFinalScore)
