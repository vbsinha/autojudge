import os
import pickle

from re import compile
from io import StringIO
from shutil import rmtree
from logging import error
from subprocess import run
from datetime import timedelta, datetime
from traceback import print_exc
from csv import writer as csvwriter
from typing import Tuple, Optional, Dict, Any, List
from django.utils import timezone

from . import models


def process_contest(name: str, start_datetime: datetime, soft_end_datetime: datetime,
                    hard_end_datetime: datetime, penalty: float, public: bool,
                    enable_linter_score: bool, enable_poster_score: bool) -> Tuple[bool, str]:
    """
    Process a New Contest
    Only penalty can be None in which case Penalty will be set to 0

    Returns:
        (True, None) or (False, Exception string)
    """
    try:
        c = models.Contest(name=name, start_datetime=start_datetime,
                           soft_end_datetime=soft_end_datetime,
                           hard_end_datetime=hard_end_datetime,
                           penalty=penalty, public=public,
                           enable_linter_score=enable_linter_score,
                           enable_poster_score=enable_poster_score)
        c.save()
        # Successfully added to Database
        return (True, str(c.pk))
    except Exception as e:
        # Exception Case
        print_exc()
        error(e.__str__())
        return (False, 'Contest could not be created')


def delete_contest(contest_id: int) -> Tuple[bool, Optional[str]]:
    """
    Delete the contest.
    This will cascade delete in all the tables that have contest as FK.
    It calls delete_problem for each problem in the contest.

    Retuns:
        (True, None)
    """
    try:
        c = models.Contest.objects.get(pk=contest_id)
        problems = models.Problem.objects.filter(contest=c)
        for problem in problems:
            delete_problem(problem.pk)
        if os.path.exists(os.path.join('content', 'contests', str(contest_id))):
            rmtree(os.path.join('content', 'contests', str(contest_id)))

        models.Contest.objects.filter(pk=contest_id).delete()
        return (True, None)
    except Exception as e:
        print_exc()
        error(e.__str__())
        return (False, 'Contest could not be deleted')


def process_problem(code: str, contest: int, name: str, statement: str, input_format: str,
                    output_format: str, difficulty: int, time_limit: int, memory_limit: int,
                    file_format: str, start_code, max_score: int, compilation_script, test_script,
                    setter_solution) -> Tuple[bool, Optional[str]]:
    """
    Process a new Problem
    Nullable [None-able] Fields: start_code, compilation_script, test_script, file_format

    Returns:
        (True, None) or (False, Exception string)
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

    statement = 'The problem statement is empty.' if statement is None else statement
    input_format = 'No input format specified.' if input_format is None else input_format
    output_format = 'No output format specified.' if output_format is None else output_format

    try:
        c = models.Contest.objects.get(pk=contest)
        p = models.Problem.objects.create(
            code=code, contest=c, name=name, statement=statement,
            input_format=input_format, output_format=output_format,
            difficulty=difficulty, time_limit=time_limit, memory_limit=memory_limit,
            file_format=file_format, start_code=start_code, max_score=max_score,
            compilation_script=compilation_script,
            test_script=test_script, setter_solution=setter_solution)

        if not os.path.exists(os.path.join('content', 'problems', p.code)):
            # Create the problem directory explictly if not yet created
            # This will happen when both compilation_script and test_script were None
            os.makedirs(os.path.join('content', 'problems', p.code))

        if cp_comp_script:
            # Copy the default comp_script if the user did not upload custom
            run(['cp', os.path.join('judge', compilation_script),
                 os.path.join('content', 'problems', p.code, 'compilation_script.sh')])
            p.compilation_script = os.path.join('content', 'problems',
                                                p.code, 'compilation_script.sh')

        if cp_test_script:
            # Copy the default test_script if the user did not upload custom
            run(['cp', os.path.join('judge', test_script),
                 os.path.join('content', 'problems', p.code, 'test_script.sh')])
            p.test_script = os.path.join('content', 'problems', p.code, 'test_script.sh')

        if cp_comp_script or cp_test_script:
            p.save()

        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def update_problem(code: str, name: str, statement: str, input_format: str,
                   output_format: str, difficulty: str) -> Tuple[bool, Optional[str]]:
    """
    Update the fields in problem
    Pass the code as pk of problem

    Returns:
        (True, None)
    """
    try:
        p = models.Problem.objects.get(pk=code)
        p.name = name
        p.statement = statement
        p.input_format = input_format
        p.output_format = output_format
        p.difficulty = difficulty
        p.save()
        return (True, None)
    except models.Problem.DoesNotExist:
        return (False, '{} code does not exist.'.format(code))
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def delete_problem(problem_id: str) -> Tuple[bool, Optional[str]]:
    """
    Delete the problem.
    This will cascade delete in all the tables that have problem as FK.
    It will also delete all the submissions, testcases and the directory
    (in problems directory) corresponding to the problem .

    Returns:
        (True, None)
    """
    try:
        problem = models.Problem.objects.get(pk=problem_id)
        # First delete all the files stored corresponding to this problem
        testcases = models.TestCase.objects.filter(problem=problem)
        for testcase in testcases:
            inputfile_path = os.path.join(
                'content', 'testcase', 'inputfile_{}.txt'.format(testcase.pk))
            outputfile_path = os.path.join(
                'content', 'testcase', 'outputfile_{}.txt'.format(testcase.pk))
            if os.path.exists(inputfile_path):
                os.remove(inputfile_path)
            if os.path.exists(outputfile_path):
                os.remove(outputfile_path)
        submissions = models.Submission.objects.filter(problem=problem)
        for submission in submissions:
            submission_path = os.path.join(
                'content', 'submissions',
                'submission_{}{}'.format(submission.pk, submission.file_type))
            if os.path.exists(submission_path):
                os.remove(submission_path)
        rmtree(os.path.join('content', 'problems', problem_id))

        models.Problem.objects.filter(pk=problem_id).delete()
        return (True, None)
    except Exception as e:
        print_exc()
        error(e.__str__())
        return (False, 'Contest could not be deleted')


def process_person(email, rank=0) -> Tuple[bool, Optional[str]]:
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
        print_exc()
        return (False, e.__str__())


def process_testcase(problem_id: str, ispublic: bool,
                     inputfile, outputfile) -> Tuple[bool, Optional[str]]:
    """
    Process a new Testcase
    problem is the 'code' (pk) of the problem.

    .. warning::
        This function does not rescore all the submissions and so score will not
        change in response to the new testcase. DO NOT CALL THIS FUNCTION ONCE THE
        CONTEST HAS STARTED, IT WILL LEAD TO ERRONEOUS SCORES.
    """
    try:
        problem = models.Problem.objects.get(pk=problem_id)
        t = problem.testcase_set.create(
            public=ispublic, inputfile=inputfile, outputfile=outputfile)
        t.save()
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def delete_testcase(testcase_id: str) -> Tuple[bool, Optional[str]]:
    """
    This function deletes the testcase and cascade deletes in
    all the tables the Fk appears.

    .. warning::
        This function does not rescore all the submissions and so score will not
        change in response to the deleted testcase. DO NOT CALL THIS FUNCTION ONCE THE
        CONTEST HAS STARTED, IT WILL LEAD TO ERRONEOUS SCORES.

    Returns:
        (True, None)
    """
    try:
        inputfile_path = os.path.join(
            'content', 'testcase', 'inputfile_{}.txt'.format(testcase_id))
        outputfile_path = os.path.join(
            'content', 'testcase', 'outputfile_{}.txt'.format(testcase_id))
        if os.path.exists(inputfile_path):
            os.remove(inputfile_path)
        if os.path.exists(outputfile_path):
            os.remove(outputfile_path)
        models.TestCase.objects.filter(pk=testcase_id).delete()
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def process_solution(problem_id: str, participant: str, file_type,
                     submission_file, timestamp: str) -> Tuple[bool, Optional[str]]:
    """
    Process a new Solution
    problem is the 'code' (pk) of the problem. participant is email(pk) of the participant
    """
    try:
        problem = models.Problem.objects.get(pk=problem_id)
        if file_type not in problem.file_format.split(','):
            return (False, 'Accepted file types: \"{}\"'
                           .format(', '.join(problem.file_format.split(','))))
        participant = models.Person.objects.get(email=participant)
        s = problem.submission_set.create(participant=participant, file_type=file_type,
                                          submission_file=submission_file, timestamp=timestamp)
        s.save()
    except Exception as e:
        print_exc()
        return (False, e.__str__())

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
        f.write('{}\n'.format(int(problem.time_limit.total_seconds())))
        f.write('{}\n'.format(problem.memory_limit))
        for testcase in testcases:
            f.write('{}\n'.format(testcase.pk))

    try:
        for testcase in testcases:
            models.SubmissionTestCase.objects.create(submission=s, testcase=testcase,
                                                     verdict='R', memory_taken=0,
                                                     time_taken=timedelta(seconds=0))
    except Exception as e:
        print_exc()
        return (False, e.__str__())

    return (True, None)


def update_poster_score(submission_id: str, new_score: int):
    try:
        submission = models.Submission.objects.get(pk=submission_id)
        submission.final_score -= submission.ta_score
        submission.ta_score = new_score
        submission.final_score += submission.ta_score
        submission.save()

        ppf, _ = models.PersonProblemFinalScore.objects.get_or_create(
            person=submission.participant.pk, problem=submission.problem.pk)
        # TODO Find the maximum score and update leaderboard
        if ppf.score <= submission.final_score:
            # <= because otherwise when someone submits for the first time and scores 0
            # (s)he will not show up in leaderboard
            ppf.score = submission.final_score
            update_lb = True
            ppf.save()

        if update_lb and submission.problem.contest.soft_end_datetime >= submission.timestamp:
            # Update the leaderboard only if not a late submission
            # and the submission imporved the final score
            update_leaderboard(submission.problem.contest.pk,
                               submission.participant.email)
        return (True, None)
    except Exception as e:
        return (False, e.__str__())


def add_person_to_contest(person: str, contest: str,
                          permission: bool) -> Tuple[bool, Optional[str]]:
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
            cp = models.ContestPerson.objects.get(person=p, contest=c)
            if cp.role == permission:
                return (False, '{} is already a {}'.format(
                    p.email, 'Poster' if permission else 'Participant'))
            else:
                return (False, '{} already exists with other permission'.format(p.email))
        except models.ContestPerson.DoesNotExist:
            cp = p.contestperson_set.create(contest=c, role=permission)
            cp.save()
            return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def add_person_rgx_to_contest(rgx: str, contest: str,
                              permission: bool) -> Tuple[bool, Optional[str]]:
    """
    Accepts a regex and adds all the participants matching the rgx in the database to the contest
    with the passed permission
    Note that unlike add_person_to_contest this function does not create any new perons
    In case no persons match the rgx,
    (False, 'Regex {} did not match any person registered'.format(rgx)) is returned
    Use regex like cs15btech* to add all persons having emails like cs15btech...

    Returns:
        (True, None)
    """
    pattern = compile(rgx)
    try:
        person_emails = [p.email for p in models.Person.objects.all()]
        emails_matches = [email for email in person_emails if bool(pattern.match(email))]
        c = models.Contest.objects.get(pk=contest)
        if c.public is True and permission is False:
            # Do not store participants for public contests
            return (True, None)
        if len(emails_matches) == 0:
            return (False, 'Regex {} did not match any person registered'.format(rgx))
        for email in emails_matches:
            add_person_to_contest(email, contest, permission)
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def add_persons_to_contest(persons: List[str], contest: str,
                           permission: bool) -> Tuple[bool, Optional[str]]:
    """
    Add the relation between Person and Contest for all the Person in persons list
    persons is the list of email of persons
    contest is the pk of the contest
    permission is False if participant and True is poster

    .. note::
        First check if any of the person exists with an opposing role.
        If so, do not add anyone. Instead return a tuple with False and
        and an appropriate message.
        Otherwise if person doesn't have conflicting permission,
        add all the persons and return (True, None).

    This function would create records for all the persons who do not already have one irrespective
    of whether anyone has conflict or not.
    """
    try:
        for person in persons:
            models.Person.objects.get_or_create(email=person)

        c = models.Contest.objects.get(pk=contest)
        if c.public is True and permission is False:
            # Do not store participants for public contests
            return (True, None)

        person_list = [models.Person.objects.get(email=person) for person in persons]
        for p in person_list:
            try:
                # Check that person is not already registered in the contest with other permission
                cp = models.ContestPerson.objects.get(person=p, contest=c)
                if cp.role == (not permission):
                    return (False, '{} already exists with other permission'.format(p.email))
            except models.ContestPerson.DoesNotExist:
                continue

        for p in person_list:
            models.ContestPerson.objects.get_or_create(contest=c, person=p, role=permission)
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_personcontest_permission(person: Optional[str], contest: int) -> Optional[bool]:
    """
    Determine the relation between Person and Contest
    person is the email of the person
    contest is the pk of the contest

    Returns:
        False if participant and True is poster None if neither
    """
    curr = timezone.now()
    if person is None:
        try:
            c = models.Contest.objects.get(pk=contest)
            if c.public and curr >= c.start_datetime:
                return False
            else:
                return None
        except Exception:
            return None
    p = models.Person.objects.get(email=person)
    c = models.Contest.objects.get(pk=contest)
    # partcipant and Current datetime < C.date_time -> None
    try:
        cp = models.ContestPerson.objects.get(person=p, contest=c)
        if cp.role is False and curr < c.start_datetime:
            return None
        return cp.role
    except models.ContestPerson.DoesNotExist:
        if c.public and curr >= c.start_datetime:
            return False
    except Exception:
        return None
    return None


def delete_personcontest(person: str, contest: str) -> Tuple[bool, Optional[str]]:
    """
    Delete the record of person and contest in ContestPerson table
    Passed person is email and contest is the pk

    Returns:
        (True, None)
    """
    try:
        p = models.Person.objects.get(email=person)
        c = models.Contest.objects.get(pk=contest)
        cpset = models.ContestPerson.objects.filter(person=p, contest=c)
        if cpset.exists():
            cp = cpset[0]
            if (cp.role is False) or \
               (models.ContestPerson.objects.filter(contest=c, role=True).count() > 1):
                # If the person to be deleted is a participant or there are more than 1 posters
                # then we can delete the record from db.
                cpset.delete()
            else:
                return (False, 'This contest cannot be orphaned!')
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_personproblem_permission(person: Optional[str], problem: str) -> Optional[bool]:
    """
    Determine the relation between Person and Problem
    person is the email of the person
    problem is the code(pk) of the problem

    Returns:
        False if participant and True is poster None if neither
    """
    p = models.Problem.objects.get(pk=problem)
    if p.contest is None:
        return False
    return get_personcontest_permission(person, p.contest.pk)


def get_posters(contest) -> Tuple[bool, Optional[str]]:
    """
    Return the posters for the contest.
    contest is the pk of the Contest

    Returns:
        (True, List of the email of the posters)
    """
    try:
        c = models.Contest.objects.get(pk=contest)
        cps = models.ContestPerson.objects.filter(contest=c, role=True)
        cps = [cp.person.email for cp in cps]
        return (True, cps)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_participants(contest) -> Tuple[bool, Any]:
    """
    Return the participants for the contest.
    contest is the pk of the Contest

    Returns:
        (True, List of the email of the participants)

    Returns:
        (True, []) if contest is public
    """
    try:
        c = models.Contest.objects.get(pk=contest)
        if c.public is True:
            return (True, [])
        cps = models.ContestPerson.objects.filter(contest=c, role=False)
        cps = [cp.person.email for cp in cps]
        return (True, cps)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_personcontest_score(person: str, contest: int) -> Tuple[bool, Any]:
    """
    Get the final score which is the sum of individual final scores of all problems in the contest.
    Pass email in person and contest's pk
    """
    try:
        p = models.Person.objects.get(email=person)
        c = models.Contest.objects.get(pk=contest)
        problems = models.Problem.objects.filter(contest=c)
        score = 0
        for problem in problems:
            score += models.PersonProblemFinalScore.objects.get(
                person=p, problem=problem).score
        return (True, score)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_submission_status(person: str, problem: str, submission):
    """
    Get the current status of the submission.
    Pass email as person and problem code as problem to get a tuple
    In case the submission is None, returns (True, (dict1, dict2))
    The tuple consists of 2 dictionaries:

    First dictionary:
        Key: Submission ID

        Value: list of (TestcaseID, Verdict, Time_taken, Memory_taken, ispublic, message)

    Second dictionary:
        Key: Submission ID

        Value: tuple: (judge_score, ta_score, linter_score, final_score, timestamp, file_type)

    In case submission ID is provided:
    The passed parameters person and problem are ignored and so None is accepted.

    Returns:
        The same dictionaries in a tuple but having only 1 key in both
    """
    try:
        if submission is None:
            p = models.Person.objects.get(email=person)
            q = models.Problem.objects.get(code=problem)
            sub_list = models.Submission.objects.filter(
                participant=p, problem=q).order_by('-timestamp')
            t = models.TestCase.objects.filter(problem=p)
        else:
            submission = models.Submission.objects.get(pk=submission)
            t = models.TestCase.objects.filter(problem=submission.problem)
            sub_list = [submission]
    except Exception as e:
        print_exc()
        return (False, e.__str__())

    verdict_dict: Dict[Any, Any] = dict()
    score_dict = dict()

    for submission in sub_list:
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
        except Exception:
            # In case Exception occurs for any submission, then
            # that submission's verdict_dict is left empty.
            # This is done to allow the other submissions to give output.
            print_exc()
    return (True, (verdict_dict, score_dict))


def get_submissions(problem_id: str, person_id: Optional[str]) -> Tuple[bool, Any]:
    """
    Get all the submissions for this problem by this (or all) persons who attempted.
    problem is the pk of the Problem.
    person is the email of the Person or None if you want to retrieve solutions by all participants

    Returns:
        when person_id is None:
            (True, {emailofperson: [SubmissionObject1, SubmissionObject2, ...], \
                    emailofperson: [SubmissionObjecti, SubmissionObjectj, ...], \
                    ...})

        when person_id is not None:
            (True, {emailofperson: [SubmissionObject1, SubmissionObject2, ...]})
    """
    try:
        p = models.Problem.objects.get(code=problem_id)
        if person_id is None:
            submission_set = models.Submission.objects.filter(
                problem=p).order_by('participant')
        else:
            person = models.Person.objects.get(email=person_id)
            submission_set = models.Submission.objects.filter(
                problem=p, participant=person).order_by('participant')
        result = {}
        if submission_set.count() == 0:
            if person_id is None:
                return (True, {})
            else:
                return (True, {person.pk: []})
        curr_person = submission_set[0].participant.pk
        result[curr_person] = [submission_set[0]]
        for i in range(1, len(submission_set)):
            if submission_set[i].participant.pk == curr_person:
                result[curr_person].append(submission_set[i])
            else:
                curr_person = submission_set[i].participant.pk
                result[curr_person] = [submission_set[i]]
        return (True, result)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_submission_status_mini(submission: str) -> Tuple[bool, Any]:
    """
    Get the current status of the submission.

    Returns:
        (True, (dict1, tuple1))

    The tuple consists of a dictionary and a tuple:
        Dictionary:
            Key: TestcaseID

            Value: (Verdict, Time_taken, Memory_taken, ispublic, message)
        Tuple:
            (judge_score, ta_score, linter_score, final_score, timestamp, file_type)
    """
    try:
        s = models.Submission.objects.get(pk=submission)
        testcases = models.TestCase.objects.filter(problem=s.problem)

        verdict_dict: Dict[Any, Any] = dict()

        for testcase in testcases:
            st = models.SubmissionTestCase.objects.get(
                submission=s, testcase=testcase)
            verdict_dict[testcase.pk] = (st.get_verdict_display, st.time_taken,
                                         st.memory_taken, testcase.public, st.message)
        score_tuple = (s.judge_score, s.ta_score, s.linter_score, s.final_score,
                       s.timestamp, s.file_type)
        return (True, (verdict_dict, score_tuple))
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_leaderboard(contest: int) -> Tuple[bool, Any]:
    """
    Returns the current leaderboard for the passed contest
    Pass contest's pk

    Returns:
        (True, [[Rank1Email, ScoreofRank1], [Rank2Email, ScoreofRank2] ... ])
    """
    leaderboard_path = os.path.join('content', 'contests', str(contest)+'.lb')
    if not os.path.exists(leaderboard_path):
        return (False, 'Leaderboard not yet initialized for this contest.')
    try:
        with open(leaderboard_path, 'rb') as f:
            data = pickle.load(f)
        return (True, data)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def update_leaderboard(contest: int, person: str):
    """
    Updates the leaderboard for the passed contest for the rank of the person
    Pass pk for contest and email for person
    Only call this function when some submission for some problem of the contest
     has scored more than its previous submission.
    Remember to call this function whenever PersonProblemFinalScore is updated.
    Returns True if update was successfull else returns False
    """

    os.makedirs(os.path.join('content', 'contests'), exist_ok=True)
    pickle_path = os.path.join('content', 'contests', str(contest) + '.lb')

    status, score = get_personcontest_score(person, contest)

    if status:
        if not os.path.exists(pickle_path):
            with open(pickle_path, 'wb') as f:
                data = [[person, score]]
                pickle.dump(data, f)
            return True
        else:
            with open(pickle_path, 'rb') as f:
                data = pickle.load(f)
            with open(pickle_path, 'wb') as f:
                for i in range(len(data)):
                    if data[i][0] == person:
                        data[i][1] = score
                        pos = i
                        break
                else:
                    data.append([person, score])
                    pos = len(data) - 1
                for i in range(pos, 0, -1):
                    if data[i][1] > data[i-1][1]:
                        data[i], data[i-1] = data[i-1], data[i]
                    else:
                        break
                pickle.dump(data, f)
            return True
    else:
        return False


def process_comment(problem: str, person: str, commenter: str,
                    timestamp, comment: str) -> Tuple[bool, Optional[str]]:
    """
    Privately comment 'comment' on the problem for person by commenter.
    problem is the pk of the Problem.
    person and commenter are emails of Person.

    Returns:
        (True, None)
    """
    try:
        problem = models.Problem.objects.get(pk=problem)
        person = models.Person.objects.get(email=person)
        commenter = models.Person.objects.get(email=commenter)
        models.Comment.objects.create(problem=problem, person=person,
                                      commenter=commenter, timestamp=timestamp, comment=comment)
        return (True, None)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_comments(problem: str, person: str) -> Tuple[bool, Any]:
    """
    Get the private comments on the problem for the person.

    Returns:
        (True, [(Commeter, Timestamp, Comment) ... (Sorted in chronological order)])
    """
    try:
        comments = models.Comment.objects.filter(
            problem=problem, person=person).order_by('timestamp')
        result = [(comment.commenter, comment.timestamp, comment.comment)
                  for comment in comments]
        return (True, result)
    except Exception as e:
        print_exc()
        return (False, e.__str__())


def get_csv(contest: str) -> Tuple[bool, Any]:
    """
    Get the csv (in string form) of the current scores of all participants in the contest.
    Pass pk of the contest

    Returns:
        (True, csvstring)
    """
    try:
        c = models.Contest.objects.get(pk=contest)
        problems = models.Problem.objects.filter(contest=c)

        csvstring = StringIO()
        writer = csvwriter(csvstring)
        writer.writerow(['Email', 'Score'])

        if problems.exists():
            # Get the final scores for each problem for any participant who has attempted.
            submissions = models.PersonProblemFinalScore.objects.filter(problem=problems[0])
            for problem in problems[1:]:
                submissions |= models.PersonProblemFinalScore.objects.filter(problem=problem)

            if submissions.exists():
                # Now sort all the person-problem-scores by 'person' and 'problem'
                # This will create scores like:
                # [('p1', 3(Say score corresponding to problem2)),
                #  ('p1', 2(score corresponding to problem4)),
                #  ('p2', 5(score corresponding to problem3)),
                #  ('p2', 0(score corresponding to problem1)) ... ]
                # We do not need to save exactly which problem the score correspondes to
                # we only need to know scores on all problems by a participant
                submissions.order_by('person', 'problem')
                scores = [(submission.person, submission.score)
                          for submission in submissions]

                # Here we aggregate the previous list.
                # We simply iterate over scores and for each participant,
                # we sum up how much has he scored in all the problems.
                # To do this we exploit the fact that list is already sorted.
                # In the above case after aggregating we'll write
                # 'p1', 5
                # 'p2', 5 etc. in csvstring
                curr_person = scores[0][0]
                sum_scores = 0
                for score in scores:
                    if curr_person == score[0]:
                        sum_scores += score[1]
                    else:
                        writer.writerow([curr_person, sum_scores])
                        curr_person = score[0]
                        sum_scores = score[1]
                writer.writerow([curr_person, sum_scores])

        csvstring.seek(0)
        return (True, csvstring)
    except Exception as e:
        print_exc()
        return (False, e.__str__())
