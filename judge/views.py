from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.utils import timezone

from .models import Contest, Problem, TestCase
from . import handler

# Create your views here.


def index(request):
    context = {}
    if request.user.is_authenticated:
        handler.process_person(request.user.email)
    # TODO
    # Get all public contests if user not signed in
    # Get contests for which the current user is poster/participant
    contests = Contest.objects.all()
    context['contests'] = contests
    return render(request, 'judge/index.html', context)


def new_contest(request):
    if request.method == 'POST':
        # TODO Sanitize input
        status, err = handler.process_contest(request.POST.get('name'),
                                              request.POST['start_date'] +
                                              '+0530',
                                              request.POST['end_date'] +
                                              '+0530',
                                              request.POST.get('penalty'),
                                              True if request.POST.get('public') == 'on' else False)
        if status:
            return redirect('/judge/')
        context = {'error_msg': 'Could not create new contest',
                   'post_data': request.POST}
        return render(request, 'judge/new_contest.html', context)
    else:
        context = {}
        return render(request, 'judge/new_contest.html', context)


def add_poster(request, contest_id, permission=True):
    # TODO Error handling
    if request.method == 'POST':
        status, err = handler.add_person_to_contest(
            request.POST.get('email'), contest_id, permission)
        if status:
            return redirect(request.META['HTTP_REFERER'])
    return redirect(request.META['HTTP_REFERER'])


def add_participant(request, contest_id):
    return add_poster(request, contest_id, False)


def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    problems = Problem.objects.filter(contest_id=contest_id)
    return render(request, 'judge/contest_detail.html', {
        'contest': contest,
        'problems': problems,
        'contest_start': contest.start_datetime.strftime('%d-%m-%Y %H:%M'),
        'contest_end': contest.end_datetime.strftime('%d-%m-%Y %H:%M'),
    })


def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    return render(request, 'judge/problem_detail.html', {
        'problem': problem,
        'public_tests': TestCase.objects.filter(problem_id=problem_id, public=True),
        'private_tests': TestCase.objects.filter(problem_id=problem_id, public=False),
    })


def new_problem(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    if request.method == 'POST':
        # TODO Sanitize input
        status, err = handler.process_problem(request.POST.get('code'),
                                              contest_id,
                                              request.POST.get('name'),
                                              request.POST.get('statement'),
                                              request.POST.get('input_format'),
                                              request.POST.get('output_format'),
                                              request.POST.get('difficulty'),
                                              timedelta(milliseconds=int(
                                                  request.POST.get('time_limit'))),  # Ensure not null
                                              request.POST.get('memory_limit'),
                                              request.POST.get('file_format'),
                                              # Nullable field
                                              request.FILES.get('start_code'),
                                              request.POST.get('max_score'),
                                              # Nullable field
                                              request.FILES.get(
                                                  'compilation_script'),
                                              # Nullable field
                                              request.FILES.get('test_script'),
                                              request.FILES.get(
                                                  'setter_solution')
                                              # Nullable field
                                              )
        print(request.POST)
        if status:
            # no_test_cases = int(request.POST['no_test_cases'])
            # print(no_test_cases)
            # for i in range(no_test_cases):
            #     status, err = handler.process_testcase(
            #         request.POST['code'], True if request.POST['test'+str(i)] == 'on' else False,
            #         request.FILES.get('input'+str(i)), request.FILES.get('output'+str(i)))
            #     print(status, err)
            return redirect('/judge/contest/{}/'.format(contest_id))
        else:
            print(err)
            context = {'error_msg': 'Could not create new problem',
                       'post_data': request.POST,
                       'contest': contest}
            return render(request, 'judge/new_problem.html', context)
    else:
        context = {'contest': contest}
        return render(request, 'judge/new_problem.html', context)


def add_test_case_problem(request, problem_id):
    if request.method == 'POST':
        status, err = handler.process_testcase(problem_id,
                                               True if request.POST.get(
                                                   'test-type') == 'public' else False,
                                               request.FILES.get('input'),
                                               request.FILES.get('output'))
        print(status, err)
        if status:
            return redirect(request.META['HTTP_REFERER'])
        else:
            print(err)
            return redirect(request.META['HTTP_REFERER'])
    else:
        print('Not POST')
        return redirect(request.META['HTTP_REFERER'])


def edit_problem(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    contest = get_object_or_404(Contest, pk=problem.contest_id)
    # TODO
    pass


def problem_submit(request, problem_id):
    if request.method == 'POST':
        # TODO What is file_type?
        # TODO Process return and display result
        status, err = handler.process_solution(
            problem_id, request.user.email, '.cpp', request.FILES.get('file'), timezone.now())
        if status:
            # TODO give status
            return redirect('/judge/')
        else:
            print(err)
            return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect('/judge/')
