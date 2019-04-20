import subprocess
import traceback
import os

from datetime import timedelta

from . import models


def process_contest(name: str, start_datetime, end_datetime, penalty: float, public: bool):
    """
    Process a New Contest
    Only penalty can be None in which case Penalty will be set to 0
    Returns: (True, None) or (False, Exception string)
    """
    name = 'Unnamed Contest' if name is None else name
    penalty = 0. if penalty is None else penalty
    public = False if public is None else public

    try:
        c = models.Contest(name=name, start_datetime=start_datetime,
                           end_datetime=end_datetime, penalty=penalty, public=public)
        c.save()
        # Successfully added to Database
        return (True, None)
    except Exception as e:
        # Exception Case
        traceback.print_exc()
        return (False, e.__str__)


def process_problem(code: str, contest: str, name: str, statement: str, input_format: str,
                    output_format: str, difficulty: int, time_limit: int, memory_limit: int,
                    file_format: str, start_code, max_score: int, compilation_script, test_script,
                    setter_solution):
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

    name = 'Name not set' if name is None else name
    statement = 'The problem statement is empty.' if statement is None else statement
    input_format = 'No input format specified.' if input_format is None else input_format
    output_format = 'No output format specified.' if output_format is None else output_format
    difficulty = 0 if difficulty is None else difficulty
    memory_limit = 200000 if memory_limit is None else memory_limit
    file_format = '.py,.cpp,.c' if file_format is None else file_format
    max_score = 0 if max_score is None else max_score

    try:
        c = models.Contest.objects.get(pk=contest)
        p = models.Problem(code=code, contest=c, name=name, statement=statement,
                           input_format=input_format, output_format=output_format,
                           difficulty=difficulty, time_limit=time_limit, memory_limit=memory_limit,
                           file_format=file_format, start_code=start_code, max_score=max_score,
                           compilation_script=compilation_script,
                           test_script=test_script, setter_solution=setter_solution)
        p.save()

        if not os.path.exists(os.path.join('content', 'problems', p.code)):
            # Create the problem directory explictly if not yet created
            # This will happen when both compilation_script and test_script were None
            os.makedirs(os.path.join('content', 'problems', p.code))

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


def process_person(email, rank=0):
    """
    Process a new Person
    Nullable Fields: rank
    """
    if email is None:
        return (False, 'Email passed is None.')
    try:
        (p, status) = models.Person.objects.get_or_create(email=email)
        if status:
            p.rank = 0 if rank is None else rank
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
    problem is the 'code' (pk) of the problem. participant is email(pk) of the participant
    """
    try:
        file_type = '.py'  # TODO file_type
        problem = models.Problem.objects.get(pk=problem)
        participant = models.Person.objects.get(email=participant)
        s = problem.submission_set.create(participant=participant, file_type=file_type,
                                          submission_file=submission_file, timestamp=timestamp)
        s.save()
    except Exception as e:
        traceback.print_exc()
        return (False, e.__str__)

    testcases = models.TestCase.objects.filter(problem=problem)

    if not os.path.exists(os.path.join('content', 'tmp')):
        os.makedirs(os.path.join('content', 'tmp'))
    # NB: File structure here
    # PROBLEM_ID
    # SUBMISSION_ID
    # FILE_FORMAT
    # TIME_LIMIT
    # MEMORY_LIMIT
    # TESTCASE_1
    # TESTCASE_2
    # ....
    with open(os.path.join('content', 'tmp', 'sub_run_' + str(s.pk) + '.txt'), 'w') as f:
        f.write('{}\n'.format(problem.pk))
        f.write('{}\n'.format(s.pk))
        f.write('{}\n'.format(file_type))
        f.write('{}\n'.format(problem.time_limit.seconds()))
        f.write('{}\n'.format(problem.memory_limit))
        for testcase in testcases:
            f.write('{}\n'.format(testcase.pk))

    try:
        for i in range(len(testcases)):
            st = models.SubmissionTestCase(submission=s, testcase=testcases[i], verdict='R',
                                           memory_taken=0, time_taken=timedelta(seconds=0))
            st.save()
    except Exception as e:
        traceback.print_exc()
        return (False, e.__str__)

    return (True, None)


def add_person_to_contest(person: str, contest: str, permission: bool):
    """
    Add the relation between Person and Contest
    person is the email of the person
    contest is the pk of the contest
    permission is False if participant and True is poster
    """
    try:
        (p, _) = models.Person.objects.get_or_create(email=person)
        c = models.Contest.objects.get(pk=contest)
        if c.public is True and permission is False:
            # Do not store participants for public contests
            return (True, None)
        try:
            # Check that the person is not already registered in the contest with other permission
            cp = models.ContestPerson.objects.get(
                person=p, contest=c, permission=(not permission))
            return (False, '{} Already exists with other permission'.format(p.email))
        except models.ContestProblem.DoesNotExist:
            cp = p.contestperson_set.create(contest=c, role=permission)
            cp.save()
            return (True, None)
    except Exception as e:
        traceback.print_exc()
        return (False, e.__str__)


def get_personcontest_permission(person: str, contest: str):
    """
    Determine the relation between Person and Contest
    person is the email of the person
    contest is the pk of the contest
    returns False if participant and True is poster None if neither
    """
    try:
        p = models.Person.objects.get(email=person)
        c = models.Contest.objects.get(pk=contest)
        cp = models.ContestPerson.objects.get(person=p, contest=c)
        return cp.role
    except models.ContestPerson.DoesNotExist:
        q_set = models.ContestPerson.filter(name=contest, role=False)
        return (False if len(q_set) == 0 else None)


def get_personproblem_permission(person: str, problem: str):
    """
    Determine the relation between Person and Problem
    person is the email of the person
    problem is the code(pk) of the problem
    returns False if participant and True is poster None if neither
    """
    p = models.Problem.objects.get(pk=problem)
    if p.contest is None:
        return False
    return get_personcontest_permission(person, p.contest)


def get_posters(contest: str):
    """
    Return the posters for the contest.
    contest is the pk of the Contest
    Return (True, List of the email of the posters)
    """
    try:
        c = models.Contest.objects.get(pk=contest)
        cps = models.ContestPerson.objects.filter(contest=c, role=True)
        cps = [cp.email for cp in cps]
        return (True, cps)
    except Exception as e:
        traceback.print_exc()
        return (False, e.__str__)


def get_participants(contest: str):
    """
    Return the participants for the contest.
    contest is the pk of the Contest
    Returns (True, List of the email of the participants)
    Returns (True, []) if contest is public
    """
    try:
        c = models.Contest.objects.get(pk=contest)
        if c.public is True:
            return (True, [])
        cps = models.ContestPerson.objects.filter(contest=c, role=False)
        cps = [cp.email for cp in cps]
        return (True, cps)
    except Exception as e:
        traceback.print_exc()
        return (False, e.__str__)


def get_submission_status(person: str, problem: str, submission: str):
    """
    Get the current status of the submission.
    Pass email as person and problem code as problem to get a tuple
    In case the submission is None, returns:
    (True, ({SubmissionID: [(TestcaseID, Verdict, Time_taken, Memory_taken, ispublic, message)]},
     {SubmissionID: (judge_score, ta_score, linter_score, final_score, timestamp, file_type)}))
    The tuple consists of 2 dictionaries:
        First dictionary: Key: Submission ID
                          Value: list of (TestcaseID, Verdict, Time_taken,
                                          Memory_taken, ispublic, message)
        Second dictionary: Key: Submission ID
                           Value: tuple: (judge_score, ta_score, linter_score,
                                          final_score, timestamp, file_type)
    In case submission ID is provided:
    The passed parameters person and problem are ignored and so None is accepted.
    Returns: The same dictionaries in a tuple but having only 1 key in both
    """
    try:
        if submission is None:
            p = models.Person.objects.get(email=person)
            q = models.Problem.objects.get(code=problem)
            s = models.Submission.objects.filter(
                participant=p, problem=q).order_by('-timestamp')
            t = models.TestCase.objects.filter(problem=p)
        else:
            submission = models.Submission.objects.get(pk=submission)
            t = models.TestCase.objects.filter(problem=submission.problem)
            s = [submission]
    except Exception as e:
        traceback.print_exc()
        return (False, e.__str__)

    verdict_dict = dict()
    score_dict = dict()

    for submission in s:
        score_dict[submission.pk] = (submission.judge_score, submission.ta_score,
                                     submission.linter_score, submission.final_score,
                                     submission.timestamp, submission.file_type)
        verdict_dict[submission.pk] = []
        try:
            for testcase in t:
                st = models.SubmissionTestCase.objects.get(
                    submission=submission, testcase=testcase)
                verdict_dict[submission.pk].append((testcase.pk, st.verdict, st.time_taken,
                                                    st.memory_taken, testcase.public, st.message))
        except Exception as _:
            # In case Exception occurs for any submission, then
            # that submission's verdict_dict is left empty.
            # This is done to allow the other submissions to give output.
            traceback.print_exc()
    return (True, (verdict_dict, score_dict))
