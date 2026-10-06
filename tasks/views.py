from django.shortcuts import render, get_object_or_404
from .models import Task
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

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