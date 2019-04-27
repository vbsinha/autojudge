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

    # Contest name [Char]
    name = models.CharField(
        max_length=50, default='Unnamed Contest', unique=True)

    # Start Date and Time for Contest
    start_datetime = models.DateTimeField()

    # "Soft" End Date and Time for Contest
    soft_end_datetime = models.DateTimeField()

    # "Hard" End Date and Time for Contest
    hard_end_datetime = models.DateTimeField()

    # Penalty for late-submission
    penalty = models.FloatField(default=0.0)

    # Is the contest public
    # In public Contests everyone except posters can participate
    public = models.BooleanField()

    def __str__(self):
        return self.name


class Problem(models.Model):
    """
    Model for a Problem.
    """
    # Problem code [Char, PrimaryKey]
    # UNSET is a special problem code which other problems must not use.
    code = models.CharField(max_length=10, primary_key=True, default='UNSET')

    # Contest for the problem [Contest]
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)

    # Problem name [Char]
    name = models.CharField(max_length=50, default='Name not set')

    # Problem statement [Char]
    statement = models.TextField(default='The problem statement is empty.')

    # Input format [Char]
    input_format = models.TextField(default='No input format specified.')

    # Output format [Char]
    output_format = models.TextField(default='No output format specified.')

    # Difficulty [PositiveInt]
    difficulty = models.PositiveSmallIntegerField(default=0)

    # Time Limit [Duration]
    time_limit = models.DurationField(default=timedelta(seconds=10))

    # Memory Limit [Int]
    # Currently this is specified in mega-bytes
    memory_limit = models.PositiveIntegerField(default=200000)

    # File format [Char]
    # Support upto 30 file formats
    file_format = models.CharField(max_length=100, default='.py,.cpp,.c')

    # Start code [File]
    start_code = models.FileField(upload_to=start_code_name, null=True)

    # Max score [PositiveInt]
    max_score = models.PositiveSmallIntegerField(default=0)

    # Compilation script [File]
    compilation_script = models.FileField(
        upload_to=partial(compilation_test_upload_location,
                          is_compilation=True),
        default='./default/compilation_script.sh')

    # Test script [File]
    test_script = models.FileField(
        upload_to=partial(compilation_test_upload_location,
                          is_compilation=False),
        default='./default/test_script.sh')

    # Setter solution script [File, Nullable]
    setter_solution = models.FileField(upload_to=setter_sol_name, null=True)

    def __str__(self):
        return self.code


class Person(models.Model):
    """
    Model for Person.
    """

    # Email ID of the Person
    email = models.EmailField(primary_key=True)

    # Rank of the Person
    rank = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.email


class Submission(models.Model):
    """
    Model for a Submission.
    """
    # Self Generated PrimaryKey
    id = models.CharField(max_length=32, primary_key=True, default=uuid4)

    # ForeignKey to Problem
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    # ForeignKey to Person
    participant = models.ForeignKey(Person, on_delete=models.CASCADE)

    # This has to be updated periodically
    PERMISSIBLE_FILE_TYPES = (
        ('.none', 'NOT_SELECTED'),
        ('.py', 'PYTHON'),
        ('.c', 'C'),
        ('.cpp', 'CPP'),
    )

    # File Type [Char]
    file_type = models.CharField(
        max_length=5, choices=PERMISSIBLE_FILE_TYPES, default='.none')

    # Submission file [File]
    submission_file = models.FileField(upload_to=submission_upload_location)

    # Timestamp of submission [Time]
    timestamp = models.DateTimeField()

    # Judge score [Int]
    judge_score = models.PositiveSmallIntegerField(default=0)

    # TA score [Int]
    ta_score = models.PositiveSmallIntegerField(default=0)

    # Final score [Int]
    final_score = models.FloatField(default=0.0)

    # Linter score [Int]
    linter_score = models.FloatField(default=0.0)


class ContestPerson(models.Model):
    """
    Model for ContestPerson.
    This maps how (either as a Participant or Poster) persons have access to the contests.
    """

    # (FK) Contest ID of the Contest.
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)

    # (FK) Person ID of the Person.
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    # Boolean to determine whether the Person is a Particpant or Poster
    # true for Poster and false for Participant
    role = models.BooleanField()

    class Meta:
        unique_together = (('contest', 'person'),)


class TestCase(models.Model):
    """
    Model for TestCase.
    Maintains testcases and mapping between TestCase and Problem.
    """

    # (FK) Problem ID of the Problem.
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    # Boolean to determine whether the TestCase is Private or Public
    # true for Public and false for Private
    public = models.BooleanField()

    # Self Generated PrimaryKey
    id = models.CharField(max_length=32, primary_key=True, default=uuid4)

    # Store the inputfile for the testcase.
    # Sample: ./content/testcase/inputfile_UUID.txt
    inputfile = models.FileField(upload_to=partial(testcase_upload_location, is_input=True),
                                 default='./default/inputfile.txt')

    # Store the outputfile for the testcase
    # ./content/testcase/outputfile_UUID.txt
    outputfile = models.FileField(upload_to=partial(testcase_upload_location, is_input=False),
                                  default='./default/outputfile.txt')


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

    # (FK) Submission ID of the Submission.
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    # (FK) testCase ID of the TestCase.
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)

    # Verdict by the judge
    verdict = models.CharField(max_length=2, choices=VERDICT, default='NA')

    # Memory taken by the Submission on this TestCase
    memory_taken = models.PositiveIntegerField()

    # Time taken by the Submission on this TestCase
    time_taken = models.DurationField()

    # Message placeholder, used for erroneous submissions
    message = models.TextField(default='')

    class Meta:
        unique_together = (('submission', 'testcase'),)


class Comment(models.Model):
    """
    Model for Comment.
    """

    # (FK) Problem ID of the Problem.
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    # (FK) Person ID of the Person.
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name='person')

    # Self Generated PrimaryKey
    id = models.CharField(max_length=32, primary_key=True, default=uuid4)

    # (FK) Person ID for the commenter
    commenter = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name='commenter')

    # Timestamp of the comment
    timestamp = models.DateTimeField(default=timezone.now)

    # Content of the Comment
    comment = models.TextField()


class PersonProblemFinalScore(models.Model):
    """
    Model to store the final score assigned to a person for a problem.
    """
    # (FK) Problem ID of the Problem.
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    # (FK) Person ID of the Person.
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    # Final Score [Int]
    score = models.FloatField(default=0.0)

    class Meta:
        unique_together = (('problem', 'person'),)
