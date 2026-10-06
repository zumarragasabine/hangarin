from django.shortcuts import render, get_object_or_404
from .models import Task


def task_list(request):
    tasks = Task.objects.select_related("priority", "category").order_by("deadline")
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


def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, "tasks/task_detail.html", {
        "task": task,
        "notes": task.note_set.all(),
        "subtasks": task.subtask_set.all(),
    })