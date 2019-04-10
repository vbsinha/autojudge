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
    path('contest/<int:contest_id>/problem/new/', views.new_problem, name='new_problem'),
]
