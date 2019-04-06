from django.db import models

from uuid import uuid4
from os.path import splitext


class Problem(models.Model):
    """
    Model for a Problem.
    """
    # Problem code [Char, PrimaryKey]
    code = models.CharField(max_length=10, primary_key=True)

    # Problem name [Char]
    name = models.CharField(max_length=50)

    # Problem statement [Char]
    statement = models.TextField(max_length=2500)

    # Input format [Char]
    input_format = models.CharField(max_length=1000)

    # Output format [Char]
    output_format = models.CharField(max_length=500)

    # Difficulty [PositiveInt]
    difficulty = models.PositiveSmallIntegerField(default=0)

    # Time Limit [Duration]
    time_limit = models.DurationField()

    # Memory Limit [Int]
    # Currently this is specified in bytes
    memory_limit = models.PositiveIntegerField()

    # File format [Char]
    # Support upto 30 file formats
    file_format = models.CharField(max_length=100)

    # Start code [File]
    start_code = models.FileField(upload_to='content/{}/start_code.zip'.format(code))

    # Max score [PositiveInt]
    max_score = models.PositiveSmallIntegerField()

    # Compilation script [File]
    comp_script = models.FileField(upload_to='content/{}/comp_script.sh'.format(code))

    # Test script [File]
    test_script = models.FileField(upload_to='content/{}/test_script.sh'.format(code))

    # Setter solution script [File, Nullable]
    setter_solution = models.FileField(upload_to=(
                                       lambda instance, filename: 'content/{}/setter_soln.{}'
                                                                  .format(instance.code,
                                                                          splitext(filename)[1])),
                                       null=True)


class Submission(models.Model):
    """
    Model for a Submission.
    """
    # ID of Submission [Char]
    id = uuid4().hex

    # ForeignKey to Problem
    problem = models.ForeignKey(Problem)

    # ForeignKey to Person
    participant = models.ForeignKey(Person)

    # This has to be updated periodically
    PERMISSIBLE_FILE_TYPES = (
                                ('.none', 'NOT_SELECTED'),
                                ('.py', 'PYTHON'),
                                ('.c', 'C'),
                                ('.cpp', 'CPP'),
                             )

    # File Type [Char]
    file_type = models.CharField(max_length=5, choices=PERMISSIBLE_FILE_TYPES, default='.none')

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


class Contest(models.Model):
    """
    Model for Contest.
    """

    # Start Date and Time for Contest
    start_datetime = models.DateTimeField()

    # End Date and Time for Contest
    end_datetime = models.DateTimeField()

    # Penalty for late-submission
    penalty = models.DecimalField(max_digits=3, decimal_places=2)


class Person(models.Model):
    """
    Model for Person.
    """

    # Email ID of the Person
    email = models.EmailField()

    # Rank of the Person
    rank = models.PositiveIntegerField()


class ContestProblem(models.Model):
    """
    Model for ContestProblem. This maps which problems are a part of which contests.
    """

    # (FK) Contest ID of the Contest. 
    contest = models.ForeignKey(Contest)

    # (FK) Problem ID of the Problem.
    problem = models.ForeignKey(Problem)


class ContestPerson(models.Model):
    """
    Model for ContestPerson. This maps how (either as a Participant or Poster) persons have access to the contests.
    """

    # (FK) Contest ID of the Contest.    
    contest = models.ForeignKey(Contest)

    # (FK) Person ID of the Person.
    person = models.ForeignKey(Person)

    # Boolean to determine whether the Person is a Particpant or Poster
    # true for Poster and false for Participant
    role = models.BooleanField()


class TestCase(models.Model):
    """
    Model for TestCase. Maintains testcases and mapping between TestCase and Problem.
    """

    # (FK) Problem ID of the Problem.
    problem = models.ForeignKey(Problem)
    
    # Boolean to determine whether the TestCase is Private or Public
    # true for Public and false for Private
    public = models.BooleanField()

    # Self Generated PrimaryKey
    _id = uuid4().hex
    testcase_id = models.CharField(primary_key=True, default=_id)

    # Store the inputfile for the testcase.
    # Sample: ./content/PROBLEMCODE/testcase/inputfile_UUID.txt
    inputfile = models.FileField(upload_to="/".join(['content', problem.code, 'testcase', 'inputfile_' + _id + '.txt']))

    # Store the outputfile for the testcase
    # ./content/APPLE/testcase/outputfile_UUID.txt
    outputfile = models.FileField(upload_to="/".join(['content', problem.code, 'testcase', 'outputfile_' + _id + '.txt']))


class SubmissionTestCase(models.Model):
    """
    Model for SubmissionTestCase. Maintains mapping between TestCase and Submission. 
    """

    # Possible Verdicts
    VERDICT = (
        ('P', 'Pass'), 
        ('F', 'Fail'), 
        ('TE', 'TLE'), 
        ('ME', 'OOM'), 
        ('CE', 'COMPILATION_ERROR'), 
        ('RE', 'RUNTIME_ERROR'), 
        ('NA', 'NOT_AVAILABLE'))

    # (FK) Submission ID of the Submission.
    submission = models.ForeignKey(Submission)

    # (FK) testCase ID of the TestCase.   
    testcase = models.ForeignKey(TestCase)

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
    problem = models.ForeignKey(Problem)

    # (FK) Person ID of the Person.
    person = models.ForeignKey(Person)

    # Store a comment file for each Problem Student pair.
    # Sample path: ./content/PROBLEMCODE/comment/person.yml
    comment = models.FileField(upload_to="/".join(['content', problem.code, 'comment', person.id + '.yml']))
