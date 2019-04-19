from django.urls import path
from django.conf.urls import include
from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = 'judge'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('contest/new/', views.new_contest, name='new_contest'),
    path('contest/<int:contest_id>/', views.contest_detail, name='contest_detail'),
    path('contest/<int:contest_id>/problem/new/',
         views.new_problem, name='new_problem'),
    path('problem/<str:problem_id>/', views.problem_detail, name='problem_detail'),
    path('contest/<int:contest_id>/poster/new/',
         views.add_poster, name='contest_add_poster'),
    path('contest/<int:contest_id>/participant/new/',
         views.add_participant, name='contest_add_participant'),
    path('problem/<str:problem_id>/edit/',
         views.edit_problem, name='edit_problem'),
    path('problem/<str:problem_id>/submit/',
         views.problem_submit, name='problem_submit'),
    path('problem/<str:problem_id>/tests/add/',
         views.add_test_case_problem, name='new_problem_test'),
]
