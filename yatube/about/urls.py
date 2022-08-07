from django.urls import path

from . import views


app_name = 'about'

urlpatterns = [
    path('', views.AboutAuthorView.as_view(), name='about'),
    path('tech/', views.AboutTechView.as_view(), name='tech'),
]
