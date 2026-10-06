from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("tasks/", views.task_list, name="task_list"),
    path("task/<int:pk>/", views.task_detail, name="task_detail"),
    path("login/", auth_views.LoginView.as_view(template_name="tasks/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("task/new/", views.task_create, name="task_create"),
    path("task/<int:pk>/edit/", views.task_update, name="task_update"),
    path("task/<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("task/<int:pk>/complete/", views.task_complete, name="task_complete"),
    path("task/<int:task_pk>/subtask/new/", views.subtask_create, name="subtask_create"),
    path("subtask/<int:pk>/edit/", views.subtask_update, name="subtask_update"),
    path("subtask/<int:pk>/complete/", views.subtask_complete, name="subtask_complete"),
    path("subtask/<int:pk>/delete/", views.subtask_delete, name="subtask_delete"),
    path("task/<int:task_pk>/note/new/", views.note_create, name="note_create"),
    path("note/<int:pk>/edit/", views.note_update, name="note_update"),
    path("note/<int:pk>/delete/", views.note_delete, name="note_delete"),
]