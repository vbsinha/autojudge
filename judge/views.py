import os

from django.urls import reverse
from django.core.files import File
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from . import handler
from .models import Contest, Problem, TestCase, Submission
from .forms import NewContestForm, AddPersonToContestForm, DeletePersonFromContestForm
from .forms import NewProblemForm, EditProblemForm, NewSubmissionForm, AddTestCaseForm
from .forms import NewCommentForm, UpdateContestForm, AddPosterScoreForm


def _get_user(request) -> User:
    if request.user.is_authenticated:
        # For superusers without email ID, we have to create a dummy email ID.
        # This is a hotpatch: we need to fix the createsuperuser.
        if request.user.email == '':
            if request.user.is_superuser:
                request.user.email = request.user.username + '@autojudge.superuser'
            else:
                return None
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


def handler404(request, *args):
    """
    Renders 404 page.

    :param request: the request object used
    :type request: HttpRequest
    """
    return render(request, '404.html', status=404)


def handler500(request, *args):
    """
    Renders 500 page.

    :param request: the request object used
    :type request: HttpRequest
    """
    return render(request, '500.html', status=500)


def index(request):
    """
    Renders the index page.

    :param request: the request object used
    :type request: HttpRequest
    """
    context = {}
    user = _get_user(request)
    if user is not None:
        status, maybe_error = handler.process_person(request.user.email)
        if not status:
            return handler404(request)
    contests = Contest.objects.all()
    permissions = [handler.get_personcontest_permission(
        None if user is None else user.email, contest.pk) for contest in contests]
    context['contests'] = zip(contests, permissions)
    return render(request, 'judge/index.html', context)


def new_contest(request):
    """
    Renders view for the page to create a new contest.

    :param request: the request object used
    :type request: HttpRequest
    """
    user = _get_user(request)
    if user is None:
        return handler404(request)
    if request.method == 'POST':
        form = NewContestForm(request.POST)
        if form.is_valid():
            status, code_or_error = handler.process_contest(**form.cleaned_data)
            if status:
                handler.add_person_to_contest(user.email, code_or_error, True)
                return redirect(reverse('judge:index'))
            else:
                form.add_error(None, code_or_error)
    else:
        form = NewContestForm()
    context = {'form': form}
    return render(request, 'judge/new_contest.html', context)


def get_people(request, contest_id, role):
    """
    Function to render the page for viewing participants and posters
    for a contest based on :attr:`role`.

    :param request: the request object used
    :type request: HttpRequest
    :param contest_id: the contest ID
    :type contest_id: int
    :param role: ``True`` for Poster, ``False`` for Participant
    :type role: bool
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
        form = DeletePersonFromContestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            status, maybe_error = handler.delete_personcontest(email, contest_id)
            if not status:
                form.add_error(None, maybe_error)
    else:
        form = DeletePersonFromContestForm()
    context['form'] = form
    if role:
        status, value_or_error = handler.get_posters(contest_id)
    else:
        status, value_or_error = handler.get_participants(contest_id)
    if status:
        context['persons'] = value_or_error
    else:
        return handler404(request)
    context['permission'] = perm
    return render(request, 'judge/contest_persons.html', context)


def get_posters(request, contest_id):
    """
    Renders the page for posters of a contest.
    Dispatches to :func:`get_people` with :attr:`role` set to ``True``.

    :param request: the request object used
    :type request: HttpRequest
    :param contest_id: the contest ID
    :type contest_id: int
    """
    return get_people(request, contest_id, True)


def get_participants(request, contest_id):
    """
    Renders the page for posters of a contest.
    Dispatches to :func:`get_people` with :attr:`role` set to ``False``.

    :param request: the request object used
    :type request: HttpRequest
    :param contest_id: the contest ID
    :type contest_id: int
    """
    return get_people(request, contest_id, False)


def add_person(request, contest_id, role):
    """
    Function to render the page for adding a person - participant or poster to
    a contest.

    :param request: the request object used
    :type request: HttpRequest
    :param contest_id: the contest ID
    :type contest_id: int
    :param role: ``True`` for Poster, ``False`` for Participant
    :type role: bool
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
            status, maybe_error = handler.add_persons_to_contest(emails, contest_id, role)
            if status:
                return redirect(reverse('judge:get_{}s'.format(context['type'].lower()),
                                        args=(contest_id,)))
            else:
                form.add_error(None, maybe_error)
    else:
        form = AddPersonToContestForm()
    context['form'] = form
    return render(request, 'judge/contest_add_person.html', context)


def add_poster(request, contest_id):
    """
    Renders the page for adding a poster.
    Dispatches to :func:`add_person` with :attr:`role` set to ``True``.

    :param request: the request object used
    :type request: HttpRequest
    :param contest_id: the contest ID
    :type contest_id: int
    """
    return add_person(request, contest_id, True)


def add_participant(request, contest_id):
    """
    Renders the page for adding a participant.
    Dispatches to :func:`add_person` with :attr:`role` set to ``False``.

    :param request: the request object used
    :type request: HttpRequest
    :param contest_id: the contest ID
    :type contest_id: int
    """
    return add_person(request, contest_id, False)


def contest_detail(request, contest_id):
    """
    Renders the contest preview page after the contest has been created.

    :param request: the request object used
    :type request: HttpRequest
    :param contest_id: the contest ID
    :type contest_id: int
    """
    contest = get_object_or_404(Contest, pk=contest_id)
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest_id)
    if perm is None:
        return handler404(request)
    problems = Problem.objects.filter(contest_id=contest_id)
    status, leaderboard = handler.get_leaderboard(contest_id)
    curr_time = timezone.now()
    context = {
        'contest': contest,
        'type': 'Poster' if perm else 'Participant',
        'problems': problems,
        'leaderboard_status': status,
        'leaderboard': leaderboard,
        'curr_time': curr_time,
    }
    if perm is True:
        if request.method == 'POST':
            form = UpdateContestForm(request.POST)
            if form.is_valid():
                if (curr_time < contest.soft_end_datetime or
                    (form.cleaned_data['contest_soft_end'] == contest.soft_end_datetime and
                        curr_time < contest.hard_end_datetime)):
                    try:
                        contest.start_datetime = form.cleaned_data['contest_start']
                        contest.soft_end_datetime = form.cleaned_data['contest_soft_end']
                        contest.hard_end_datetime = form.cleaned_data['contest_hard_end']
                        contest.save()
                    except Exception as e:
                        form.add_error(None, str(e))
                else:
                    form.add_error(None, 'Deadline cannot be extended if it has passed')
        else:
            form = UpdateContestForm(initial={
                'contest_start': contest.start_datetime,
                'contest_soft_end': contest.soft_end_datetime,
                'contest_hard_end': contest.hard_end_datetime,
            })
        context['form'] = form
    return render(request, 'judge/contest_detail.html', context)


def contest_scores_csv(request, contest_id):
    """
    Function to provide the facility to download a CSV of scores
    of participants in a contest at a given point in time.

    :param request: the request object used
    :type request: HttpRequest
    :param contest_id: the contest ID
    :type contest_id: int
    """
    user = _get_user(request)
    perm = handler.get_personcontest_permission(
        None if user is None else user.email, contest_id)
    if perm:
        status, csv_or_error = handler.get_csv(contest_id)
        if status:
            response = HttpResponse(csv_or_error.read())
            response['Content-Disposition'] = \
                "attachment; filename=contest_{}.csv".format(contest_id)
            return response
    return handler404(request)


def delete_contest(request, contest_id):
    """
    Function to provide the option to delete a contest.

    :param request: the request object used
    :type request: HttpRequest
    :param contest_id: the contest ID
    :type contest_id: int
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

    :param request: the request object used
    :type request: HttpRequest
    :param problem_id: the problem ID
    :type problem_id: str
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

    :param request: the request object used
    :type request: HttpRequest
    :param problem_id: the problem ID
    :type problem_id: str
    :param testcase_id: the testcase ID
    :type testcase_id: str
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
    This preview will be changed based on the role of the user (poster or participant).

    :param request: the request object used
    :type request: HttpRequest
    :param problem_id: the problem ID
    :type problem_id: str
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
    elif perm is False and user.is_authenticated and timezone.now() < problem.contest.hard_end_datetime:
        if request.method == 'POST':
            form = NewSubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                status, maybe_error = handler.process_submission(
                    problem_id, user.email, **form.cleaned_data, timestamp=timezone.now())
                if status:
                    return redirect(reverse('judge:problem_submissions', args=(problem_id,)))
                if not status:
                    form.add_error(None, maybe_error)
        else:
            form = NewSubmissionForm()
        context['form'] = form
    if perm is True:
        if timezone.now() < problem.contest.start_datetime:
            if request.method == 'POST':
                form = AddTestCaseForm(request.POST, request.FILES)
                if form.is_valid():
                    status, maybe_error = handler.process_testcase(problem_id, **form.cleaned_data)
                    if status:
                        redirect(reverse('judge:problem_submissions', args=(problem_id,)))
                    else:
                        form.add_error(None, maybe_error)
            else:
                form = AddTestCaseForm()
        else:
            form = None
        context['form'] = form
    context['public_tests'] = []
    context['private_tests'] = []
    for t in public_tests:
        input_file = open(t.inputfile.path, 'r')
        output_file = open(t.outputfile.path, 'r')
        context['public_tests'].append((input_file.read(), output_file.read(), t.pk))
        input_file.close()
        output_file.close()
    for t in private_tests:
        input_file = open(t.inputfile.path, 'r')
        output_file = open(t.outputfile.path, 'r')
        context['private_tests'].append((input_file.read(), output_file.read(), t.pk))
        input_file.close()
        output_file.close()
    context['curr_time'] = timezone.now()
    return render(request, 'judge/problem_detail.html', context)


def problem_starting_code(request, problem_id: str):
    """
    Function to provide the facility to download the starting code
    for a problem.

    :param request: the request object used
    :type request: HttpRequest
    :param problem_id: the problem ID
    :type problem_id: str
    """
    problem = get_object_or_404(Problem, pk=problem_id)
    user = _get_user(request)
    perm = handler.get_personproblem_permission(None if user is None else user.email, problem_id)
    if perm is None:
        return handler404(request)
    elif problem.starting_code:
        return _return_file_as_response(problem.starting_code.path)
    else:
        return handler404(request)


def problem_compilation_script(request, problem_id: str):
    """
    Function to provide the facility to download the compilation script
    for a problem after creating the problem.

    :param request: the request object used
    :type request: HttpRequest
    :param problem_id: the problem ID
    :type problem_id: str
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
    Function to provide the facility to download the testing script
    for a problem after creating the problem.

    :param request: the request object used
    :type request: HttpRequest
    :param problem_id: the problem ID
    :type problem_id: str
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
    Function to provide the facility to download the
    default compilation or test script.

    :param request: the request object used
    :type request: HttpRequest
    :param script_name: name of the script - one of `compilation_script` or `test_script`
    :type script_name: str
    """
    if script_name not in ['compilation_script', 'test_script']:
        return handler404(request)
    else:
        return _return_file_as_response(os.path.join('judge', 'default', script_name + '.sh'))


def new_problem(request, contest_id):
    """
    Renders view for the page to create a new problem in a contest.

    :param request: the request object used
    :type request: HttpRequest
    :param contest_id: the contest ID
    :type contest_id: int
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
            status, maybe_error = handler.process_problem(contest_id=contest_id,
                                                          **form.cleaned_data)
            if status:
                code = form.cleaned_data['code']
                return redirect(reverse('judge:problem_detail', args=(code,)))
            else:
                form.add_error(None, maybe_error)
    else:
        form = NewProblemForm()
    context['form'] = form
    return render(request, 'judge/new_problem.html', context)


def edit_problem(request, problem_id):
    """
    Renders view for the page to edit selected fields of a pre-existing problem.

    :param request: the request object used
    :type request: HttpRequest
    :param problem_id: the problem ID
    :type problem_id: str
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
            status, maybe_error = handler.update_problem(problem.code, **form.cleaned_data)
            if status:
                return redirect(reverse('judge:problem_detail', args=(problem.code,)))
            else:
                form.add_error(None, maybe_error)
    else:
        required_fields = ['name', 'statement', 'input_format', 'output_format', 'difficulty']
        form = EditProblemForm({field: getattr(problem, field) for field in required_fields})
    context['form'] = form
    context['problem'] = problem
    return render(request, 'judge/edit_problem.html', context)


def problem_submissions(request, problem_id: str):
    """
    Renders the page where all submissions to a given problem can be seen.
    For posters, this renders a set of tables for each participant.
    For participants, this renders a table with the scores of their submissions only.

    :param request: the request object used
    :type request: HttpRequest
    :param problem_id: the problem ID
    :type problem_id: str
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
                status, maybe_error = handler.process_comment(
                    problem_id, form.cleaned_data['participant_email'], user.email,
                    timezone.now(), form.cleaned_data['comment'])
                if not status:
                    form.add_error(None, maybe_error)
                else:
                    form = NewCommentForm()
    else:
        form = NewCommentForm()
    submissions = {}
    if perm:
        status, all_subs_or_error = handler.get_submissions(problem_id, None)
        if status:
            for email, subs in all_subs_or_error.items():
                comment_set = handler.get_comments(problem_id, email)
                submissions[email] = (subs, comment_set)
            context['submissions'] = submissions
        else:
            return handler404(request)
    elif user is not None:
        status, subs_or_error = handler.get_submissions(problem_id, user.email)
        if status:
            context['participant'] = True
            comments = handler.get_comments(problem_id, user.email)
            submissions[user.email] = (subs_or_error[user.email], comments)
        else:
            return handler404(request)
    else:
        return handler404(request)
    context['form'] = form
    context['submissions'] = submissions
    return render(request, 'judge/problem_submissions.html', context)


def submission_download(request, submission_id: str):
    """
    Function to provide the facility to download a given submission.

    :param request: the request object used
    :type request: HttpRequest
    :param submission_id: the submission ID
    :type submission_id: str
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

    :param request: the request object used
    :type request: HttpRequest
    :param submission_id: the submission ID
    :type submission_id: str
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
                    status, maybe_error = handler.update_poster_score(submission.pk,
                                                                      form.cleaned_data['score'])
                    if not status:
                        form.add_error(None, maybe_error)
            else:
                form = AddPosterScoreForm(initial={'score': submission.poster_score})
            context['form'] = form
        status, info_or_error = handler.get_submission_status(submission_id)
        if status:
            context['test_results'] = info_or_error[0]
            context['judge_score'] = info_or_error[1][0]
            context['poster_score'] = info_or_error[1][1]
            context['linter_score'] = info_or_error[1][2]
            context['final_score'] = info_or_error[1][3]
            context['timestamp'] = info_or_error[1][4]
            context['file_type'] = info_or_error[1][5]
        else:
            return handler404(request)

        return render(request, 'judge/submission_detail.html', context)
    else:
        return handler404(request)
