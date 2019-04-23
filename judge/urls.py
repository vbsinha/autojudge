from django.urls import path
from django.conf.urls import include
from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = 'judge'
handler404 = views.handler404
handler500 = views.handler500

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
    path('problem/<str:problem_id>/starting-code/',
         views.problem_starting_code, name='problem_starting_code'),
    path('contest/<int:contest_id>/poster/new/',
         views.add_poster, name='contest_add_poster'),
    path('contest/<int:contest_id>/participant/new/',
         views.add_participant, name='contest_add_participant'),
    path('contest/<int:contest_id>/posters/',
         views.get_posters, name='get_posters'),
    path('contest/<int:contest_id>/participants/',
         views.get_participants, name='get_participants'),
    path('problem/<str:problem_id>/edit/',
         views.edit_problem, name='edit_problem'),
    path('problem/<str:problem_id>/submissions/',
         views.problem_submissions, name='problem_submissions'),
    path('submission/<str:submission_id>/',
         views.submission_detail, name='submission_detail'),
]
