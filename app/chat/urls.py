from django.urls import path
from . import views

urlpatterns = [
    path('main/view/', views.MainView.as_view(), name='main-view')
]