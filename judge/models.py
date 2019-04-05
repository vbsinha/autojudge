from django.db import models

from functools import partial


def upload_file_to_problem(instance, filename, extension):
    """
    This is a callable to upload a file based on the problem ID
    """
    return '/'.join(['content', instance.code, filename + extension])

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

    # Difficulty [PositiveInt, Nullable]
    difficulty = models.PositiveSmallIntegerField(null=True)

    # Time Limit [Duration]
    time_limit = models.DurationField()

    # Memory Limit [Int]
    # Currently this is specified in bytes
    memory_limit = models.PositiveIntegerField()

    # File format [Char]
    # Support upto 30 file formats
    file_format = models.CharField(max_length=100)

    # Start code [File]
    start_code = models.FileField(upload_to=partial(upload_file_to_problem, filename='start_code.zip'))

    # Max score [PositiveInt]
    max_score = models.PositiveSmallIntegerField()

    # Compilation script [File]
    comp_script = models.FileField(upload_to=partial(upload_file_to_problem, filename='comp_script'))

    # Test script [File]
    test_script = models.FileField(upload_to=partial(upload_file_to_problem, filename='test_script'))

    # Setter solution script [File, Nullable]
    setter_solution = models.FileField(upload_to=partial(upload_file_to_problem, filename='setter_soln'), null=True)
