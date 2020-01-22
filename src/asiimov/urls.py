"""
asiimov URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout')
]
