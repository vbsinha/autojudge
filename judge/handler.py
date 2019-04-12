import subprocess
import traceback
import os
from uuid import uuid4

from . import models


def process_contest(name, start_datetime, end_datetime, penalty):
    """
    Process a New Contest
    Only penalty can be None in which case Penalty will be set to 0
    Returns: (True, None) or (False, Exception string)
    """

    # Set penalty to defualt value 0
    if penalty is None:
        penalty = 0.0

    try:
        c = models.Contest(name=name, start_datetime=start_datetime,
                           end_datetime=end_datetime, penalty=penalty)
        c.save()
        # Successfully added to Database
        return (True, None)
    except Exception as e:
        # Exception Case
        traceback.print_exc()
        return (False, e.__str__)


def process_problem(code: str, name: str, statement: str, input_format: str, output_format: str,
                    difficulty: int, time_limit: int, memory_limit: int, file_format: str,
                    start_code, max_score: int, compilation_script, test_script, setter_solution):
    """
    Process a new Problem
    Nullable [None-able] Fields: start_code, compilation_script, test_script, file_format
    Returns: (True, None) or (False, Exception string)
    """

    # Check if the Problem Code has already been taken
    try:
        models.Problem.objects.get(pk=code)
        return (False, '{} already a used Question code.'.format(code))
    except models.Problem.DoesNotExist:
        pass

    # Set up default values
    cp_comp_script, cp_test_script = False, False
    if compilation_script is None:
        compilation_script = './default/compilation_script.sh'
        cp_comp_script = True
    if test_script is None:
        test_script = './default/test_script.sh'
        cp_test_script = True
    file_format = '.py,.cpp,.c' if file_format is None else file_format

    try:
        p = models.Problem(code=code, name=name, statement=statement, input_format=input_format,
                           output_format=output_format, difficulty=difficulty,
                           time_limit=time_limit, memory_limit=memory_limit,
                           file_format=file_format, start_code=start_code, max_score=max_score,
                           compilation_script=compilation_script,
                           test_script=test_script, setter_solution=setter_solution)
        p.save()

        if not os.path.exists(os.path.join('content', 'problems', p.code)):
            # Create the problem directory explictly if not yet created
            # This will happen when both compilation_script and test_script were None
            os.mkdir(os.path.join('content', 'problems', p.code))

        if cp_comp_script is True:
            # Copy the default comp_script if the user did not upload custom
            subprocess.run(['cp', os.path.join('judge', compilation_script),
                            os.path.join('content', 'problems', p.code, 'compilation_script.sh')])
        if cp_test_script is True:
            # Copy the default test_script if the user did not upload custom
            subprocess.run(['cp', os.path.join('judge', test_script),
                            os.path.join('content', 'problems', p.code, 'test_script.sh')])

        return (True, None)
    except Exception as e:
        traceback.print_exc()
        return (False, e.__str__)


def update_problem(code, name=None, statement=None, input_format=None,
                   output_format=None, difficulty=None):

    try:
        p = models.Problem.objects.get(pk=code)
        if name is not None:
            p.name = name
        if statement is not None:
            p.statement = statement
        if input_format is not None:
            p.input_format = input_format
        if output_format is not None:
            p.output_format = output_format
        if difficulty is not None:
            p.difficulty = difficulty
        p.save()
        return True
    except models.Problem.DoesNotExist:
        raise Exception('{} code does not exist.'.format(code))


def process_person(email, rank):
    """
    Process a new Person
    Nullable Fields: rank
    """
    if rank is None:
        rank = 10
    try:
        p = models.Person(email=email, rank=rank)
        p.save()
        return (True, None)
    except Exception as e:
        traceback.print_exc()
        return (False, e.__str__)


def process_testcase(problem: str, ispublic: bool, inputfile, outputfile):
    """
    Process a new Testcase
    problem is the 'code' (pk) of the problem.
    """
    try:
        problem = models.Problem.objects.get(pk=problem)
        t = problem.testcase_set.create(
            public=ispublic, inputfile=inputfile, outputfile=outputfile)
        t.save()
        return (True, None)
    except Exception as e:
        traceback.print_exc()
        return (False, e.__str__)


def process_solution(problem: str, participant: str, file_type, submission_file, timestamp: str):
    """
    Process a new Solution
    problem is the 'code' (pk) of the problem. participant is email of the participant
    """
    try:
        problem = models.Problem.objects.get(pk=problem)
        participant = models.Person.objects.get(email=participant)
        s = problem.submission_set.create(participant=participant, file_type=file_type,
                                          submission_file=submission_file, timestamp=timestamp)
        s.save()
    except Exception as e:
        traceback.print_exc()
        return (False, e.__str__)

    testcases = models.TestCase.objects.get(problem=problem)

    id = uuid4().hex
    with open(os.path.join('content', 'tmp', 'sub_run_'+id+'.txt'), 'w') as f:
        f.write(problem.pk)
        f.write(s.pk)
        f.write(file_type)
        for testcase in testcases:
            f.write(testcase.pk)

    for i in range(len(testcases)):
        st = models.SubmissionTestCase(submission=s, testcase=testcases[i], verdict='R',
                                       memory_taken=0, timetaken=0)
        st.save()

    return (True, None)
