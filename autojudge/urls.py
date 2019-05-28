"""
autojudge URL Configuration.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/judge/')),
    path('judge/', include('judge.urls')),
    path('admin/', admin.site.urls),
]
