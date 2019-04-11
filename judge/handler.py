import django
import traceback

from . import models


def process_problem(code: str, name: str, statement: str, input_format: str, output_format: str,
                    difficulty: int, time_limit: int, memory_limit: int, file_format: str,
                    start_code, max_score, compilation_script, test_script, setter_solution):
    """ Nullable Fields: start_code, compilation_script, test_script, file_format"""
    try:
        models.Problem.objects.get(pk=code)
        raise Exception('{} already a used Question code.'.format(code))
    except models.Problem.DoesNotExist:
        pass

    if compilation_script is None:
        compilation_script = './default/compilation_script.sh'
    if test_script is None:
        test_script = './default/test_script.sh'
    if file_format is None:
        file_format = '.py,.cpp,.c'
    try:
        p = models.Problem(code=code, name=name, statement=statement, input_format=input_format,
                           output_format=output_format, difficulty=difficulty,
                           time_limit=time_limit, memory_limit=memory_limit,
                           file_format=file_format, start_code=start_code, max_score=max_score,
                           compilation_script=compilation_script,
                           test_script=test_script, setter_solution=setter_solution)
        p.save()
        return True
    except Exception as e:
        print(e)
        traceback.print_exc()
        return False


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
    """ Nullable Fields: rank"""
    if rank is None:
        rank = 10
    try:
        p = models.Person(email=email, rank=rank)
        p.save()
        return True
    except Exception as e:
        print(e)
        traceback.print_exc()
        return False


def process_contest(name, start_datetime, end_datetime, penalty):
    """ None able Fields: penalty"""
    if penalty is None:
        penalty = 0.0
    try:
        c = models.Contest(name=name, start_datetime=start_datetime,
                           end_datetime=end_datetime, penalty=penalty)
        c.save()
        return True
    except Exception as e:
        print(e)
        return False


def process_testcase(problem, ispublic, inputfile, outputfile):
    try:
        problem = models.Problem.get(pk=problem)
        t = problem.testcase_set.create(
            public=ispublic, inputfile=inputfile, outputfile=outputfile)
        t.save()
        return True
    except Exception as e:
        print(e)
        traceback.print_exc()
        return False


def process_solution(problem, participant, file_type, submission_file, timestamp):
    # TODO Handle Exceptions here
    problem = models.Problem.objects.get(pk=problem)
    participant = models.Person.objects.get(pk=participant)
    s = problem.submission_set.create(participant=participant, file_type=file_type,
                                      submission_file=submission_file, timestamp=timestamp)
    s.save()

    testcases = models.TestCase.objects.get(problem=problem)
    sub_id = s.pk
    prob_id = problem.id
    testcase_ids = []
    for testcase in testcases:
        testcase_ids.append(testcase.pk)

    # Call Docker here with the prob_id, sub_id, testcase_id
    # Store Docker's reply in verdict, memory and time lists

    # Based on the result populate SubmsissionTestCase table and return the result

    for i in range(len(testcase_ids)):
        st = models.SubmissionTestCase(submission=s, testcase=testcases[i], verdict=verdict[i],
                                       memory_taken=memory[i], timetaken=time[i])
        st.save()

    return verdict, memory, time
