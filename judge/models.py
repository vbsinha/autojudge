from django.db import models

from functools import partial


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
    start_code = models.FileField(upload_to='content/{}/start_code.zip'.format(self.code))

    # Max score [PositiveInt]
    max_score = models.PositiveSmallIntegerField()

    # Compilation script [File]
    comp_script = models.FileField(upload_to='content/{}/comp_script.sh'.format(self.code))

    # Test script [File]
    test_script = models.FileField(upload_to='content/{}/test_script.sh'.format(self.code))

    # Setter solution script [File, Nullable]
    setter_solution = models.FileField(upload_to='content/{}/setter_soln'.format(self.code), null=True)
