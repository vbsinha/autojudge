from django.db import models

from uuid import uuid4
from os.path import splitext
from datetime import timedelta


def setter_sol_name(instance, filename):
    return 'content/problems/{}/setter_soln{}'.format(instance.code, splitext(filename)[1])


def start_code_name(instance, filename):
    return 'content/problems/{}/start_code{}'.format(instance.code, splitext(filename)[1])


def compilation_script_name(instance, filename):
    return 'content/problems/{}/compilation_script.sh'.format(instance.code)


def test_script_name(instance, filename):
    return 'content/problems/{}/test_script.sh'.format(instance.code)


class Problem(models.Model):
    """
    Model for a Problem.
    """
    # Problem code [Char, PrimaryKey]
    # UNSET is a special problem code which other problems must not use.
    code = models.CharField(max_length=10, primary_key=True, default='UNSET')

    # Problem name [Char]
    name = models.CharField(max_length=50, default='Name not set')

    # Problem statement [Char]
    statement = models.TextField(max_length=2500,
                                 default='The problem statement is empty.')

    # Input format [Char]
    input_format = models.CharField(max_length=1000,
                                    default='No input format specified.')

    # Output format [Char]
    output_format = models.CharField(max_length=500,
                                     default='No output format specified.')

    # Difficulty [PositiveInt]
    difficulty = models.PositiveSmallIntegerField(default=0)

    # Time Limit [Duration]
    time_limit = models.DurationField(default=timedelta(seconds=10))

    # Memory Limit [Int]
    # Currently this is specified in bytes
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
        upload_to=compilation_script_name, default='./default/compilation_script.sh')

    # Test script [File]
    test_script = models.FileField(
        upload_to=test_script_name, default='./default/test_script.sh')

    # Setter solution script [File, Nullable]
    setter_solution = models.FileField(upload_to=setter_sol_name, null=True)

    def __str__(self):
        return self.code


class Contest(models.Model):
    """
    Model for Contest.
    """

    # Contest name [Char]
    name = models.CharField(max_length=50, default='Unnamed Contest', unique=True)

    # Start Date and Time for Contest
    start_datetime = models.DateTimeField()

    # End Date and Time for Contest
    end_datetime = models.DateTimeField()

    # Penalty for late-submission
    penalty = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)

    def __str__(self):
        return self.name


class Person(models.Model):
    """
    Model for Person.
    """

    # Email ID of the Person
    email = models.EmailField(unique=True)

    # Rank of the Person
    rank = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.email


class Submission(models.Model):
    """
    Model for a Submission.
    """
    # ID of Submission [Char]
    id = uuid4().hex

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
    submission_file = models.FileField(upload_to='content/submissions/submission_{}{}'
                                                 .format(id, file_type))

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


class ContestProblem(models.Model):
    """
    Model for ContestProblem.
    This maps which problems are a part of which contests.
    """

    # (FK) Contest ID of the Contest.
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)

    # (FK) Problem ID of the Problem.
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)


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
    _id = uuid4().hex
    testcase_id = models.CharField(
        max_length=32, primary_key=True, default=_id)

    # Store the inputfile for the testcase.
    # Sample: ./content/testcase/inputfile_UUID.txt
    inputfile = models.FileField(upload_to="/".join(['content', 'testcase',
                                                     'inputfile_' + _id + '.txt']),
                                 default='./default/inputfile.txt')

    # Store the outputfile for the testcase
    # ./content/testcase/outputfile_UUID.txt
    outputfile = models.FileField(upload_to="/".join(['content', 'testcase',
                                                      'outputfile_' + _id + '.txt']),
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


class Comment(models.Model):
    """
    Model for Person.
    """

    # (FK) Problem ID of the Problem.
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    # (FK) Person ID of the Person.
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    # Self Generated PrimaryKey
    _id = uuid4().hex
    comment_id = models.CharField(max_length=32, primary_key=True, default=_id)

    # Store a comment file for each Problem Student pair.
    # Sample path: ./content/comment/UUID.yml
    comment = models.FileField(upload_to="/".join(['content', 'comment', _id + '.yml']),
                               default='./default/comment.yml')
