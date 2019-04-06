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
