from django.db import models

from uuid import uuid4


# Create your models here.
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
    inputfile = models.FileField(upload_to="/".join(['content', problem.code, 'testcase', 'inputfile'+_id + '.txt']))

    # Store the outputfile for the testcase
    # ./content/APPLE/testcase/outputfile_UUID.txt
    outputfile = models.FileField(upload_to="/".join(['content', problem.code, 'testcase', 'outputfile'+_id + '.txt']))


class SubmissionTestCase(models.Model):
    """
    Model for SubmissionTestCase. Maintains mapping between TestCase and Submission. 
    """

    # Possible Verdicts
    Verdict = (('P', 'Pass'), ('F', 'Fail'), ('TE', 'TLE'), ('CE', 'COMPILATIONERROR'), ('RE', 'RUNTIMEERROR'), ('NA', 'NOTAVAILABLE'))

    # (FK) Submission ID of the Submission.
    submission = models.ForeignKey(Submission)

    # (FK) testCase ID of the TestCase.   
    testcase = models.ForeignKey(TestCase)

    # Verdict by the judge
    verdict = models.CharField(max_length=2, choices=Verdict, default='NA')

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
    # Sample path: ./content/PROBLEMCODE/comment/person.txt
    comment = models.FileField(upload_to="/".join(['content', problem.code, 'comment', person.id + '.yml']))
