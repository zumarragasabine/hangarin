from django.shortcuts import render, get_object_or_404
from .models import Task
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import TaskForm

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).select_related("priority", "category").order_by("deadline")  # changed
    status = request.GET.get("status")
    if status in dict(Task.STATUS_CHOICES):
        tasks = tasks.filter(status=status)
    else:
        status = None
    return render(request, "tasks/task_list.html", {
        "tasks": tasks,
        "status": status,
        "statuses": [s[0] for s in Task.STATUS_CHOICES],
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)  # changed
    return render(request, "tasks/task_detail.html", {
        "task": task,
        "notes": task.note_set.all(),
        "subtasks": task.subtask_set.all(),
    })


def register(request):
    if request.user.is_authenticated:
        return redirect("task_list")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("task_list")
    return render(request, "tasks/register.html", {"form": form})

@login_required
def task_create(request):
    form = TaskForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.user = request.user
        task.save()
        return redirect("task_detail", pk=task.pk)
    return render(request, "tasks/task_form.html", {"form": form, "heading": "New task"})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    form = TaskForm(request.POST or None, instance=task)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("task_detail", pk=task.pk)
    return render(request, "tasks/task_form.html", {"form": form, "heading": "Edit task"})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == "POST":
        task.delete()
        return redirect("task_list")
    return render(request, "tasks/task_confirm_delete.html", {"task": task})


@login_required
@require_POST
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.status = "Completed"
    task.save()
    return redirect("task_list")