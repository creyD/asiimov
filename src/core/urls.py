# Default routing imports
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('offers/', views.offer_overview, name='offer_overview'),
    path('offers/<int:offerID>', views.offer, name='offer'),
    path('offers/<int:offerID>/refresh', views.offer_refresh, name='offer_refresh'),
    path('offers/<int:offerID>', views.offer_delete, name='offer_delete'),
    path('offers/create', views.offer_create, name='offer_create'),
    path('search/<str:filter>', views.search, name='search'),
    path('profile/<int:steamID>', views.profile, name='profile'),
    path('profile/me', views.me, name='me'),
    path('profile/settings', views.me_settings, name='me_settings'),

    path('help', views.help, name='help'),
    path('imprint', views.imprint, name='imprint'),
    path('about', views.about, name='about'),

    path('signup', views.signup, name='signup'),
    path('signup_confirm', views.signup_confirm)
]
