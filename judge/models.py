from django.db import models

from uuid import uuid4
from os.path import splitext
from functools import partial
from datetime import timedelta
from django.utils import timezone


def setter_sol_name(instance, filename):
    return 'content/problems/{}/setter_soln{}'.format(instance.code, splitext(filename)[1])


def start_code_name(instance, filename):
    return 'content/problems/{}/start_code{}'.format(instance.code, splitext(filename)[1])


def compilation_test_upload_location(instance, filename, is_compilation):
    # We disregard the filename argument
    file_prefix = 'compilation' if is_compilation else 'test'
    file_name = '{}_script.sh'.format(file_prefix)
    return 'content/problems/{}/{}'.format(instance.code, file_name)


def testcase_upload_location(instance, filename, is_input):
    # We disregard the filename argument
    file_prefix = 'input' if is_input else 'output'
    file_name = '{}file_{}.txt'.format(file_prefix, instance.id)
    return 'content/testcase/{}'.format(file_name)


def submission_upload_location(instance, filename):
    # We disregard the filename argument
    file_name = 'submission_{}{}'.format(instance.id, instance.file_type)
    return 'content/submissions/{}'.format(file_name)


def comment_upload_location(instance, filename):
    # We disregard the filename argument
    return 'content/comment/{}.yml'.format(instance.id)


class Contest(models.Model):
    """
    Model for Contest.
    """

    name = models.CharField(
        max_length=50, default='Unnamed Contest', unique=True)
    """Contest name"""

    start_datetime = models.DateTimeField()
    """Start Date and Time for Contest"""

    soft_end_datetime = models.DateTimeField()
    """"Soft" End Date and Time for Contest"""

    hard_end_datetime = models.DateTimeField()
    """"Hard" End Date and Time for Contest"""

    penalty = models.FloatField(default=0.0)
    """Penalty for late-submission"""

    public = models.BooleanField()
    """Is the contest public?"""

    def __str__(self):
        return self.name


class Problem(models.Model):
    """
    Model for a Problem.
    """
    # UNSET is a special problem code which other problems must not use.
    code = models.CharField(max_length=10, primary_key=True, default='UNSET')
    """Problem code"""

    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)
    """Foreign key to contest for the problem"""

    name = models.CharField(max_length=50, default='Name not set')
    """Problem name"""

    statement = models.TextField(default='The problem statement is empty.')
    """Problem statement"""

    input_format = models.TextField(default='No input format specified.')
    """Problem input format"""

    output_format = models.TextField(default='No output format specified.')
    """Problem output format"""

    difficulty = models.PositiveSmallIntegerField(default=0)
    """Problem difficulty"""

    time_limit = models.DurationField(default=timedelta(seconds=10))
    """Problem time limit"""

    # Currently this is specified in mega-bytes
    memory_limit = models.PositiveIntegerField(default=200000)
    """Problem memory limit"""

    # Support upto 30 file formats
    file_format = models.CharField(max_length=100, default='.py,.cpp')
    """Accepted file formats for submissions to problem"""

    start_code = models.FileField(upload_to=start_code_name, null=True)
    """Problem starting code"""

    max_score = models.PositiveSmallIntegerField(default=0)
    """Maximum score for a test case for the problem"""

    compilation_script = models.FileField(
        upload_to=partial(compilation_test_upload_location,
                          is_compilation=True),
        default='./default/compilation_script.sh')
    """Problem compilation script"""

    test_script = models.FileField(
        upload_to=partial(compilation_test_upload_location,
                          is_compilation=False),
        default='./default/test_script.sh')
    """Problem test script"""

    # Setter solution script [File, Nullable]
    setter_solution = models.FileField(upload_to=setter_sol_name, null=True)

    def __str__(self):
        return self.code


class Person(models.Model):
    """
    Model for Person.
    """

    email = models.EmailField(primary_key=True)
    """Email ID of the Person"""

    rank = models.PositiveIntegerField(default=0)
    """Rank of the Person"""

    def __str__(self):
        return self.email


class Submission(models.Model):
    """
    Model for a Submission.
    """
    # Self Generated PrimaryKey
    id = models.CharField(max_length=32, primary_key=True, default=uuid4)

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    """Foreign key to problem for which this is a submission"""

    participant = models.ForeignKey(Person, on_delete=models.CASCADE)
    """Foreign key to person who submitted the solution"""

    # This has to be updated periodically
    PERMISSIBLE_FILE_TYPES = (
        ('.none', 'NOT_SELECTED'),
        ('.py', 'PYTHON'),
        ('.c', 'C'),
        ('.cpp', 'CPP'),
    )

    file_type = models.CharField(
        max_length=5, choices=PERMISSIBLE_FILE_TYPES, default='.none')
    """File type of submission"""

    submission_file = models.FileField(upload_to=submission_upload_location)
    """Submission file"""

    timestamp = models.DateTimeField()
    """Timestamp of submission"""

    judge_score = models.PositiveSmallIntegerField(default=0)
    """Judge score"""

    ta_score = models.PositiveSmallIntegerField(default=0)
    """TA score"""

    linter_score = models.FloatField(default=0.0)
    """Linter score"""

    final_score = models.FloatField(default=0.0)
    """Final score"""


class ContestPerson(models.Model):
    """
    Model for ContestPerson.
    This maps how (either as a Participant or Poster) persons have access to the contests.
    """

    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    """Foreign key to contest in which this person is taking part"""

    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    """Foreign key to the actual person"""

    # True for Poster and False for Participant
    role = models.BooleanField()
    """Determines if Person is a Poster or a Participant"""

    class Meta:
        unique_together = (('contest', 'person'),)


class TestCase(models.Model):
    """
    Model for TestCase.
    Maintains testcases and mapping between TestCase and Problem.
    """

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    """Foreign key to problem for which this is a test case"""

    # True for Public and False for Private
    public = models.BooleanField()
    """Determines if the test case is a public test case or a private test case"""

    # Self Generated PrimaryKey
    id = models.CharField(max_length=32, primary_key=True, default=uuid4)

    # Sample: ./content/testcase/inputfile_UUID.txt
    inputfile = models.FileField(upload_to=partial(testcase_upload_location, is_input=True),
                                 default='./default/inputfile.txt')
    """Input file for the test case"""

    # ./content/testcase/outputfile_UUID.txt
    outputfile = models.FileField(upload_to=partial(testcase_upload_location, is_input=False),
                                  default='./default/outputfile.txt')
    """Output file for the test case"""


class SubmissionTestCase(models.Model):
    """
    Model for SubmissionTestCase.
    Maintains mapping between TestCase and Submission.
    """

    # Possible Verdicts
    VERDICT = (
        ('F', 'Fail'),
        ('P', 'Pass'),
        ('R', 'Running'),
        ('TE', 'TLE'),
        ('ME', 'OOM'),
        ('CE', 'COMPILATION_ERROR'),
        ('RE', 'RUNTIME_ERROR'),
        ('NA', 'NOT_AVAILABLE'))

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    """Foreign key to submission"""

    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    """Foreign key to test case"""

    verdict = models.CharField(max_length=2, choices=VERDICT, default='NA')
    """Verdict by the judge"""

    memory_taken = models.PositiveIntegerField()
    """Virtual memory consumed by the submission"""

    time_taken = models.DurationField()
    """Time taken by the submission"""

    message = models.TextField(default='')
    """Message placeholder, used for erroneous submissions"""

    class Meta:
        unique_together = (('submission', 'testcase'),)


class Comment(models.Model):
    """
    Model for Comment.
    """

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    """Foreign key to problem relating to the comment"""

    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name='person')
    """Foreign key to person"""

    # Self Generated PrimaryKey
    id = models.CharField(max_length=32, primary_key=True, default=uuid4)

    commenter = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name='commenter')
    """Foreign key to person who commented"""

    timestamp = models.DateTimeField(default=timezone.now)
    """Timestamp of the comment"""

    comment = models.TextField()
    """Content of the comment"""


class PersonProblemFinalScore(models.Model):
    """
    Model to store the final score assigned to a person for a problem.
    """

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    """Foreign key to problem for which the score is saved"""

    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    """Foreign key to person whose submission's score is saved"""

    score = models.FloatField(default=0.0)
    """Final score saved"""

    class Meta:
        unique_together = (('problem', 'person'),)
