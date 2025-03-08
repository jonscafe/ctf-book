from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.writeup_list, name='writeup_list'),
    path('writeup/<int:pk>/', views.writeup_detail, name='writeup_detail'),
    path('writeup/new/', views.writeup_create, name='writeup_create'),
    path('writeup/<int:pk>/edit/', views.writeup_edit, name='writeup_edit'),
    path('writeup/<int:pk>/toggle/', views.toggle_visibility, name='toggle_visibility'),
    path('writeup/<int:pk>/rollback/<int:version_id>/', views.rollback_writeup, name='rollback_writeup'),
    path('writeup/<int:pk>/delete/', views.writeup_delete, name='writeup_delete'),
    path('search/', views.search_writeups, name='search_writeups'),
]