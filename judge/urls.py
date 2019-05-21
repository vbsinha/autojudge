from django.urls import path
from django.conf.urls import include
from django.contrib.auth.views import LoginView, LogoutView

from . import views
from . import apps

app_name = apps.JudgeConfig.name
handler404 = views.handler404
handler500 = views.handler500

urlpatterns = [
    # General-purpose paths
    path('', views.index, name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('auth/', include('social_django.urls', namespace='social')),

    # Contest-specific paths
    path('contest/new/', views.new_contest, name='new_contest'),
    path('contest/<int:contest_id>/', views.contest_detail, name='contest_detail'),
    path('contest/<int:contest_id>/scores/', views.contest_scores_csv, name='contest_scores_csv'),
    path('contest/<int:contest_id>/delete/', views.delete_contest, name='delete_contest'),
    path('contest/<int:contest_id>/problem/new/',
         views.new_problem, name='new_problem'),
    path('contest/<int:contest_id>/poster/new/',
         views.add_poster, name='contest_add_poster'),
    path('contest/<int:contest_id>/participant/new/',
         views.add_participant, name='contest_add_participant'),
    path('contest/<int:contest_id>/posters/',
         views.get_posters, name='get_posters'),
    path('contest/<int:contest_id>/participants/',
         views.get_participants, name='get_participants'),

    # Problem-specific paths
    path('problem/<str:problem_id>/', views.problem_detail, name='problem_detail'),
    path('problem/<str:problem_id>/delete/', views.delete_problem, name='delete_problem'),
    path('problem/<str:problem_id>/starting-code/',
         views.problem_starting_code, name='problem_starting_code'),
    path('problem/<str:problem_id>/compilation-script/',
         views.problem_compilation_script, name='problem_compilation_script'),
    path('problem/<str:problem_id>/test-script/',
         views.problem_test_script, name='problem_test_script'),
    path('problem/default-scripts/<str:script_name>/',
         views.problem_default_script, name='problem_default_script'),
    path('problem/<str:problem_id>/edit/',
         views.edit_problem, name='edit_problem'),
    path('problem/<str:problem_id>/submissions/',
         views.problem_submissions, name='problem_submissions'),

    # Submission-specific paths
    path('submission/<str:submission_id>/',
         views.submission_detail, name='submission_detail'),
    path('submission/<str:submission_id>/download/',
         views.submission_download, name='submission_download'),
    path('problem/<str:problem_id>/testcase/<str:testcase_id>/delete/',
         views.delete_testcase, name='delete_testcase'),
]
