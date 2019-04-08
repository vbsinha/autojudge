from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render

# Create your views here.


def index(request):
    context = {}
    return render(request, 'judge/index.html', context)
