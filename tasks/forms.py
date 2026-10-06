from django import forms
from .models import Task, SubTask, Note


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "deadline", "status", "category", "priority"]
        widgets = {
            "deadline": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["deadline"].input_formats = ["%Y-%m-%dT%H:%M"]


class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ["title", "status"]


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["content"]
        widgets = {"content": forms.Textarea(attrs={"rows": 3})}