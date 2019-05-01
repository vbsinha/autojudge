from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.files import File
from django.http import HttpResponse
import logging
import os

from .models import Contest, Problem, TestCase, Submission
from .forms import NewContestForm, AddPersonToContestForm, DeletePersonFromContest
from .forms import NewProblemForm, EditProblemForm, NewSubmissionForm, AddTestCaseForm
from .forms import NewCommentForm, AddPosterScoreForm
from . import handler


def _get_user(request) -> User:
    if request.user.is_authenticated:
        return request.user
    else:
        return None


def _return_file_as_response(path_name):
    f = File(open(path_name, 'rb'))
    response = HttpResponse(f, content_type='application/octet-stream')
    f.close()
    f_name = os.path.basename(path_name)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(f_name)
    return response


def handler404(request, exception=None):
    """
    Renders 404 page
    """
    return render(request, '404.html', status=404)


def handler500(request, exception=None):
    """
    Renders 500 page
    """
    return render(request, '500.html', status=500)


def index(request):
    """
    Renders the index page
    """
    context = {}
    user = _get_user(request)
    if user is not None:
        status, err = handler.process_person(request.user.email)
        if not status:
            logging.debug(
                'Although user is not none, it could not be processed. More info: {}'.format(err))

    contests = Contest.objects.all()
    permissions = [handler.get_personcontest_permission(
        None if user is None else user.email, contest.pk) for contest in contests]
    context['contests'] = zip(contests, permissions)
    return render(request, 'judge/index.html', context)


def new_contest(request):
    """
    Renders view for the page to create a new contest
    """
    user = _get_user(request)
    if user is None:
        return handler404(request)
    if request.method == 'POST':
        form = NewContestForm(request.POST)
        if form.is_valid():
            contest_name = form.cleaned_data['contest_name']
            contest_start = form.cleaned_data['contest_start']
            contest_soft_end = form.cleaned_data['contest_soft_end']
            contest_hard_end = form.cleaned_data['contest_hard_end']
            penalty = form.cleaned_data['penalty']
            enable_linter_score = form.cleaned_data['enable_linter_score']
            enable_poster_score = form.cleaned_data['enable_poster_score']
            is_public = form.cleaned_data['is_public']
            if penalty < 0 or penalty > 1:
                form.add_error('penalty', 'Penalty should be between 0 and 1.')
            else:
                status, msg = handler.process_contest(
                    contest_name, contest_start, contest_soft_end, contest_hard_end,
                    penalty, is_public, enable_linter_score, enable_poster_score)
                if status:
                    handler.add_person_to_contest(user.email, msg, True)
                    return redirect(reverse('judge:index'))
                else:
                    logging.debug(msg)
                    form.add_error(None, 'Contest could not be created.')
    else:
        form = NewContestForm()
    context = {'form': form}
    return render(request, 'judge/new_contest.html', context)


def get_people(request, contest_id, role):
    """
    Function to render the page for viewing participants and posters
    for a contest based on argument role.
    """
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest_id)
    if perm is None:
        return handler404(request)
    if role is None:
        return handler404(request)
    context = {'contest_id': contest_id,
               'type': 'Poster' if role else 'Participant'}
    if request.method == 'POST' and perm is True:
        form = DeletePersonFromContest(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            status, err = handler.delete_personcontest(email, contest_id)
            if not status:
                logging.debug(err)
                form.add_error(None, 'Could not delete {}. {}'.format(email, err))
    else:
        form = DeletePersonFromContest()
    context['form'] = form
    if role:
        status, value = handler.get_posters(contest_id)
    else:
        status, value = handler.get_participants(contest_id)
    if status:
        context['persons'] = value
    else:
        return handler404(request)
    context['permission'] = perm
    return render(request, 'judge/contest_persons.html', context)


def get_posters(request, contest_id):
    """
    Renders the page for posters of a contest.
    Dispatches to get_people with role=True.
    """
    return get_people(request, contest_id, True)


def get_participants(request, contest_id):
    """
    Renders the page for posters of a contest.
    Dispatches to get_people with role=False.
    """
    return get_people(request, contest_id, False)


def add_person(request, contest_id, role):
    """
    Function to render the page for adding a person - participant or poster to
    a contest.
    """
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest_id)
    if not (perm is True):
        return handler404(request)
    context = {'contest_id': contest_id,
               'type': 'Poster' if role else 'Participant'}
    if request.method == 'POST':
        form = AddPersonToContestForm(request.POST)
        if form.is_valid():
            emails = form.cleaned_data['emails']
            status, err = handler.add_persons_to_contest(emails, contest_id, role)
            if status:
                return redirect(reverse('judge:get_{}s'.format(context['type'].lower()),
                                        args=(contest_id,)))
            else:
                form.add_error(None, err)
    else:
        form = AddPersonToContestForm()
    context['form'] = form
    return render(request, 'judge/contest_add_person.html', context)


def add_poster(request, contest_id):
    """
    Renders the page for adding a poster.
    Dispatches to add_person with role=True.
    """
    return add_person(request, contest_id, True)


def add_participant(request, contest_id):
    """
    Renders the page for adding a participant.
    Dispatches to add_person with role=False.
    """
    return add_person(request, contest_id, False)


def contest_detail(request, contest_id):
    """
    Renders the contest preview page after the contest has been created.
    """
    contest = get_object_or_404(Contest, pk=contest_id)
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest_id)
    if perm is None:
        return handler404(request)
    problems = Problem.objects.filter(contest_id=contest_id)
    status, leaderboard = handler.get_leaderboard(contest_id)
    return render(request, 'judge/contest_detail.html', {
        'contest': contest,
        'type': 'Poster' if perm else 'Participant',
        'problems': problems,
        'leaderboard_status': status,
        'leaderboard': leaderboard,
        'curr_time': timezone.now(),
    })


def contest_scores_csv(request, contest_id):
    """
    Function to provide downloading facility for the CSV of scores
    of participants in a contest.
    """
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest_id)
    if perm:
        status, csv = handler.get_csv(contest_id)
        if status:
            response = HttpResponse(csv.read())
            response['Content-Disposition'] = \
                "attachment; filename=contest_{}.csv".format(contest_id)
            return response
    return handler404(request)


def delete_contest(request, contest_id):
    """
    Function to provide the option to delete a contest.
    """
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest_id)
    if perm and request.method == 'POST':
        status, _ = handler.delete_contest(contest_id)
        if status:
            return redirect(reverse('judge:index'))
        else:
            return handler404(request)
    else:
        return handler404(request)


def delete_problem(request, problem_id):
    """
    Function to provide the option to delete a problem.
    """
    user = _get_user(request)
    problem = get_object_or_404(Problem, pk=problem_id)
    contest_id = problem.contest.pk
    perm = handler.get_personproblem_permission(
        None if user is None else user.email, problem_id)
    if timezone.now() > problem.contest.start_datetime:
        return handler404(request)
    if perm and request.method == 'POST':
        status, _ = handler.delete_problem(problem_id)
        if status:
            return redirect(reverse('judge:contest_detail', args=(contest_id,)))
        else:
            return handler404(request)
    else:
        return handler404(request)


def delete_testcase(request, problem_id, testcase_id):
    """
    Function to provide the option to delete a test-case of a particular problem.
    """
    user = _get_user(request)
    perm = handler.get_personproblem_permission(
        None if user is None else user.email, problem_id)
    testcase = get_object_or_404(TestCase, pk=testcase_id)
    if timezone.now() > testcase.problem.contest.start_datetime:
        return handler404(request)
    if problem_id == testcase.problem.pk and perm and request.method == 'POST':
        status, _ = handler.delete_testcase(testcase_id)
        if status:
            return redirect(reverse('judge:problem_detail', args=(problem_id,)))
        else:
            return handler404(request)
    else:
        return handler404(request)


def problem_detail(request, problem_id):
    """
    Renders the problem preview page after the problem has been created.
    This preview will be changed based on the role of the user (poster or participant)
    """
    problem = get_object_or_404(Problem, pk=problem_id)
    user = _get_user(request)
    perm = handler.get_personproblem_permission(
        None if user is None else user.email, problem_id)
    if perm is None:
        return handler404(request)
    public_tests = TestCase.objects.filter(problem_id=problem_id, public=True)
    private_tests = TestCase.objects.filter(problem_id=problem_id, public=False)
    context = {
        'problem': problem,
        'type': 'Poster' if perm else 'Participant',
    }
    if perm is False and user is None:
        pass
    elif perm is False and user.is_authenticated:
        if request.method == 'POST':
            form = NewSubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                status, err = handler.process_solution(
                    problem_id, user.email, form.cleaned_data['file_type'],
                    form.cleaned_data['submission_file'],
                    timezone.now())
                if status:
                    return redirect(reverse('judge:problem_submissions', args=(problem_id,)))
                if not status:
                    form.add_error(None, err)
        else:
            form = NewSubmissionForm()
        context['form'] = form
    if perm is True:
        if timezone.now() < problem.contest.start_datetime:
            if request.method == 'POST':
                form = AddTestCaseForm(request.POST, request.FILES)
                if form.is_valid():
                    status, err = handler.process_testcase(
                        problem_id,
                        form.cleaned_data['test_type'] == 'public',
                        form.cleaned_data['input_file'],
                        form.cleaned_data['output_file'])
                    if status:
                        redirect(reverse('judge:problem_submissions', args=(problem_id,)))
                    else:
                        form.add_error(None, err)
            else:
                form = AddTestCaseForm()
        else:
            form = None
        context['form'] = form
    context['public_tests'] = []
    context['private_tests'] = []
    for t in public_tests:
        input_file = File(open(t.inputfile.path, 'r'))
        output_file = File(open(t.outputfile.path, 'r'))
        context['public_tests'].append((input_file.file.read(), output_file.file.read(), t.pk))
        input_file.close()
        output_file.close()
    # TODO restrict private tests
    for t in private_tests:
        input_file = File(open(t.inputfile.path, 'r'))
        output_file = File(open(t.outputfile.path, 'r'))
        context['private_tests'].append((input_file.file.read(), output_file.file.read(), t.pk))
        input_file.close()
        output_file.close()
    context['curr_time'] = timezone.now()
    return render(request, 'judge/problem_detail.html', context)


def problem_starting_code(request, problem_id: str):
    """
    Function to provide downloading facility for the starting code
    for a problem.
    """
    problem = get_object_or_404(Problem, pk=problem_id)
    user = _get_user(request)
    perm = handler.get_personproblem_permission(None if user is None else user.email, problem_id)
    if perm is None:
        return handler404(request)
    elif problem.start_code:
        return _return_file_as_response(problem.start_code.path)
    else:
        return handler404(request)


def problem_compilation_script(request, problem_id: str):
    """
    Function to provide downloading facility for the compilation script
    for a problem after creating the problem.
    """
    problem = get_object_or_404(Problem, pk=problem_id)
    user = _get_user(request)
    perm = handler.get_personproblem_permission(None if user is None else user.email, problem_id)
    if perm is None or not perm:
        return handler404(request)
    elif problem.compilation_script:
        return _return_file_as_response(problem.compilation_script.path)
    else:
        return handler404(request)


def problem_test_script(request, problem_id: str):
    """
    Function to provide downloading facility for the testing script
    for a problem after creating the problem.
    """
    problem = get_object_or_404(Problem, pk=problem_id)
    user = _get_user(request)
    perm = handler.get_personproblem_permission(None if user is None else user.email, problem_id)
    if perm is None or not perm:
        return handler404(request)
    elif problem.test_script:
        return _return_file_as_response(problem.test_script.path)
    else:
        return handler404(request)


def problem_default_script(request, script_name: str):
    """
    Function to provide downloading facility for the default compilation or test script.
    """
    return _return_file_as_response(os.path.join('judge', 'default', script_name + '.sh'))


def new_problem(request, contest_id):
    """
    Renders view for the page to create a new problem in a contest.
    """
    contest = get_object_or_404(Contest, pk=contest_id)
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest_id)
    if not (perm is True):
        return handler404(request)
    context = {'contest': contest}
    if timezone.now() > contest.start_datetime:
        return handler404(request)
    if request.method == 'POST':
        form = NewProblemForm(request.POST, request.FILES)
        if form.is_valid():
            code = form.cleaned_data['code']
            status, err = handler.process_problem(
                code, contest_id, form.cleaned_data['name'], form.cleaned_data['statement'],
                form.cleaned_data['input_format'],
                form.cleaned_data['output_format'], form.cleaned_data['difficulty'],
                form.cleaned_data['time_limit'], form.cleaned_data['memory_limit'],
                form.cleaned_data['file_exts'], form.cleaned_data['starting_code'],
                form.cleaned_data['max_score'], form.cleaned_data['compilation_script'],
                form.cleaned_data['test_script'], form.cleaned_data.get('setter_soln'))
            if status:
                return redirect(reverse('judge:problem_detail', args=(code,)))
            else:
                form.add_error(None, err)
    else:
        form = NewProblemForm()
    context['form'] = form
    return render(request, 'judge/new_problem.html', context)


def edit_problem(request, problem_id):
    """
    Renders view for the page to edit selected fields of a pre-existing problem.
    """
    problem = get_object_or_404(Problem, pk=problem_id)
    contest = get_object_or_404(Contest, pk=problem.contest_id)
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest.pk)
    if not (perm is True):
        return handler404(request)
    context = {'contest': contest}
    if request.method == 'POST':
        form = EditProblemForm(request.POST)
        if form.is_valid():
            status, err = handler.update_problem(
                problem.code, form.cleaned_data['name'], form.cleaned_data['statement'],
                form.cleaned_data['input_format'], form.cleaned_data['output_format'],
                form.cleaned_data['difficulty'])
            if status:
                return redirect(reverse('judge:problem_detail', args=(problem.code,)))
            else:
                form.add_error(None, err)
    else:
        form = EditProblemForm({
            'name': problem.name,
            'statement': problem.statement,
            'input_format': problem.input_format,
            'output_format': problem.output_format,
            'difficulty': problem.difficulty
        })
    context['form'] = form
    context['problem'] = problem
    return render(request, 'judge/edit_problem.html', context)


def problem_submissions(request, problem_id: str):
    """
    Renders the page where all submissions to a given problem can be seen.
    For posters, this renders a set of tables for each participant.
    For participants, this renders a table with the scores of their submissions only.
    """
    user = _get_user(request)
    perm = handler.get_personproblem_permission(
        None if user is None else user.email, problem_id)
    if perm is None:
        return handler404(request)
    problem = get_object_or_404(Problem, pk=problem_id)
    context = {'problem': problem, 'perm': perm}
    if request.method == 'POST':
        form = NewCommentForm(request.POST)
        if form.is_valid():
            if perm is False and form.cleaned_data['participant_email'] != user.email:
                form.add_error(None, 'Your comment was not posted.')
            else:
                status, msg = handler.process_comment(
                    problem_id, form.cleaned_data['participant_email'], user.email,
                    timezone.now(), form.cleaned_data['comment'])
                if not status:
                    form.add_error(None, msg)
                else:
                    form = NewCommentForm()
    else:
        form = NewCommentForm()
    submissions = {}
    if perm:
        status, all_subs = handler.get_submissions(problem_id, None)
        if status:
            for email, subs in all_subs.items():
                status, comm = handler.get_comments(problem_id, email)
                if not status:
                    logging.debug(comm)
                    return handler404(request)
                submissions[email] = (subs, comm)
            context['submissions'] = submissions
        else:
            logging.debug(all_subs)
            return handler404(request)
    elif user is not None:
        status, subs = handler.get_submissions(problem_id, user.email)
        if status:
            context['participant'] = True
            status, comm = handler.get_comments(problem_id, user.email)
            if not status:
                logging.debug(comm)
                return handler404(request)
            submissions[user.email] = (subs[user.email], comm)
        else:
            logging.debug(subs)
            return handler404(request)
    else:
        return handler404(request)
    context['form'] = form
    context['submissions'] = submissions
    return render(request, 'judge/problem_submissions.html', context)


def submission_download(request, submission_id: str):
    """
    Function to provide downloading facility of a given submission.
    """
    user = _get_user(request)
    submission = get_object_or_404(Submission, pk=submission_id)
    perm = handler.get_personproblem_permission(
        None if user is None else user.email, submission.problem.pk)
    if user is None:
        return handler404(request)
    if perm or user.email == submission.participant.pk:
        return _return_file_as_response(submission.submission_file.path)
    else:
        return handler404(request)


def submission_detail(request, submission_id: str):
    """
    Renders the page where a detailed breakdown with respect to judge's
    evaluation, additional scores, error messages displayed and so on.
    """
    user = _get_user(request)
    submission = get_object_or_404(Submission, pk=submission_id)
    perm = handler.get_personproblem_permission(
        None if user is None else user.email, submission.problem.pk)
    context = {'submission': submission, 'problem': submission.problem}
    if user is None:
        return handler404(request)
    if perm or user.email == submission.participant.pk:
        context['type'] = 'Poster' if perm else 'Participant'
        if perm and submission.problem.contest.enable_poster_score:
            if request.method == 'POST':
                form = AddPosterScoreForm(request.POST)
                if form.is_valid():
                    status, err = handler.update_poster_score(submission.pk,
                                                              form.cleaned_data['score'])
                    if not status:
                        form.add_error(None, err)
            else:
                form = AddPosterScoreForm(initial={'score': submission.ta_score})
            context['form'] = form
        status, msg = handler.get_submission_status_mini(submission_id)
        if status:
            # TODO Fix this
            context['test_results'] = msg[0]
            context['judge_score'] = msg[1][0]
            context['ta_score'] = msg[1][1]
            context['linter_score'] = msg[1][2]
            context['final_score'] = msg[1][3]
            context['timestamp'] = msg[1][4]
            context['file_type'] = msg[1][5]
        else:
            logging.debug(msg)
            return handler404(request)

        return render(request, 'judge/submission_detail.html', context)
    else:
        return handler404(request)
