from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render

# Create your views here.


def index(request):
    context = {}
    return render(request, 'judge/index.html', context)

def new_contest(request):
    if request.method == 'POST':
        # TODO
        context = {}
        return render(request, 'judge/new_contest.html', context)
    else:
        context = {}
        return render(request, 'judge/new_contest.html', context)
