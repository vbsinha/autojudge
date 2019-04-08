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
]
