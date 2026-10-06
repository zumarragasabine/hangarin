from unicodedata import category
from urllib import request

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Task, SubTask, Note, Category, Priority
from .forms import TaskForm, SubTaskForm, NoteForm
from django.utils import timezone

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)   

    status = request.GET.get("status")                
    if status:
        tasks = tasks.filter(status=status)

    
    if request.GET.get("filter") == "open":
        tasks = tasks.exclude(status="Completed")
    elif request.GET.get("filter") == "overdue":
        tasks = tasks.filter(deadline__lt=timezone.now()).exclude(status="Completed")
    category = request.GET.get("category")
    priority = request.GET.get("priority")
    if category:
        tasks = tasks.filter(category_id=category)
    if priority:
     tasks = tasks.filter(priority_id=priority)

    return render(request, "tasks/task_list.html", {
        "tasks": tasks,
        "statuses": [s[0] for s in Task.STATUS_CHOICES],
        "status": status,
        "categories": Category.objects.all(),
        "priorities": Priority.objects.all(),
        "category": category,
        "priority": priority,
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)  # changed
    return render(request, "tasks/task_detail.html", {
        "task": task,
        "notes": task.note_set.all(),
        "subtasks": task.subtask_set.all(),
    })



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


# ---------- Subtasks ----------

@login_required
def subtask_create(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    form = SubTaskForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        sub = form.save(commit=False)
        sub.parent_task = task
        sub.save()
        return redirect("task_detail", pk=task.pk)
    return render(request, "tasks/item_form.html", {
        "form": form, "heading": "New subtask", "back": task,
    })


@login_required
def subtask_update(request, pk):
    sub = get_object_or_404(SubTask, pk=pk, parent_task__user=request.user)
    form = SubTaskForm(request.POST or None, instance=sub)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("task_detail", pk=sub.parent_task.pk)
    return render(request, "tasks/item_form.html", {
        "form": form, "heading": "Edit subtask", "back": sub.parent_task,
    })


@login_required
@require_POST
def subtask_complete(request, pk):
    sub = get_object_or_404(SubTask, pk=pk, parent_task__user=request.user)
    sub.status = "Completed"
    sub.save()
    return redirect("task_detail", pk=sub.parent_task.pk)


@login_required
@require_POST
def subtask_delete(request, pk):
    sub = get_object_or_404(SubTask, pk=pk, parent_task__user=request.user)
    task_pk = sub.parent_task.pk
    sub.delete()
    return redirect("task_detail", pk=task_pk)


# ---------- Notes ----------

@login_required
def note_create(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    form = NoteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        note = form.save(commit=False)
        note.task = task
        note.save()
        return redirect("task_detail", pk=task.pk)
    return render(request, "tasks/item_form.html", {
        "form": form, "heading": "New note", "back": task,
    })


@login_required
def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk, task__user=request.user)
    form = NoteForm(request.POST or None, instance=note)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("task_detail", pk=note.task.pk)
    return render(request, "tasks/item_form.html", {
        "form": form, "heading": "Edit note", "back": note.task,
    })


@login_required
@require_POST
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, task__user=request.user)
    task_pk = note.task.pk
    note.delete()
    return redirect("task_detail", pk=task_pk)


@login_required
def home(request):
    mine = Task.objects.filter(user=request.user)
    now = timezone.now()
    hour = timezone.localtime().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    open_tasks = mine.exclude(status="Completed")
    total = mine.count()
    completed = mine.filter(status="Completed").count()
    return render(request, "tasks/home.html", {
        "greeting": greeting,
        "name": request.user.first_name or request.user.username,
        "total": total,
        "open_count": open_tasks.count(),
        "completed": completed,
        "percent": round(completed / total * 100) if total else 0,
        "overdue": open_tasks.filter(deadline__lt=now).count(),
        "due_soon": open_tasks.filter(deadline__gte=now)
                              .select_related("priority", "category")
                              .order_by("deadline")[:5],
    })