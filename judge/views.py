from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta

from .models import Contest, Problem
from . import handler

# Create your views here.


def index(request):
    context = {}
    if request.user.is_authenticated:
        handler.process_person(request.user.email)
    return render(request, 'judge/index.html', context)


def new_contest(request):
    if request.method == 'POST':
        # TODO Sanitize input
        print(request.POST)
        status, err = handler.process_contest(request.POST['name'],
                                              request.POST['start_date'] +
                                              '+0530',
                                              request.POST['end_date'] +
                                              '+0530',
                                              request.POST['penalty'],
                                              True if request.POST['public'] == 'on' else False)
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
            request.POST['email'], contest_id, permission)
        if status:
            return redirect(request.META['HTTP_REFERER'])
    return redirect(request.META['HTTP_REFERER'])


def add_participant(request, contest_id):
    return add_poster(request, contest_id, False)


def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    return render(request, 'judge/contest_detail.html', {
        'contest': contest,
        'contest_start': contest.start_datetime.strftime('%d-%m-%Y %H:%M'),
        'contest_end': contest.end_datetime.strftime('%d-%m-%Y %H:%M'),
    })


def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    return render(request, 'judge/problem_detail.html', {
        'problem': problem,
    })


def new_problem(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    if request.method == 'POST':
        # TODO Sanitize input
        if handler.process_problem(request.POST['code'],
                                   contest_id,
                                   request.POST['name'],
                                   request.POST['statement'],
                                   request.POST['input_format'],
                                   request.POST['output_format'],
                                   request.POST['difficulty'],
                                   timedelta(milliseconds=int(
                                       request.POST['time_limit'])),
                                   request.POST['memory_limit'],
                                   request.POST['file_format'],
                                   # Nullable field
                                   request.FILES.get('start_code'),
                                   request.POST['max_score'],
                                   # Nullable field
                                   request.FILES.get('compilation_script'),
                                   # Nullable field
                                   request.FILES.get('test_script'),
                                   request.FILES.get('setter_solution')):  # Nullable field
            return redirect('/judge/contest/{}/'.format(contest_id))
        else:
            context = {'error_msg': 'Could not create new problem',
                       'post_data': request.POST,
                       'contest': contest}
            return render(request, 'judge/new_problem.html', context)
    else:
        context = {'contest': contest}
        return render(request, 'judge/new_problem.html', context)


def edit_problem(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    contest = get_object_or_404(Contest, pk=problem.contest_id)
    # TODO
    pass
