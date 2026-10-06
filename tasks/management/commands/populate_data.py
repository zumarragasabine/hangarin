import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from tasks.models import Priority, Category, Task, Note, SubTask


class Command(BaseCommand):
    help = "Populate the database with fake Task, Note, and SubTask data"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10)

    def handle(self, *args, **options):
        fake = Faker()
        priorities = list(Priority.objects.all())
        categories = list(Category.objects.all())

        if not priorities or not categories:
            self.stdout.write(self.style.ERROR(
                "Add Priority and Category records first."
            ))
            return

        statuses = ["Pending", "In Progress", "Completed"]

        for _ in range(options["count"]):
            task = Task.objects.create(
                title=fake.sentence(nb_words=5),
                description=fake.paragraph(nb_sentences=3),
                deadline=timezone.make_aware(fake.date_time_this_month()),
                status=fake.random_element(elements=statuses),
                category=random.choice(categories),
                priority=random.choice(priorities),
            )

            for _ in range(random.randint(1, 3)):
                Note.objects.create(
                    task=task,
                    content=fake.paragraph(nb_sentences=2),
                )

            for _ in range(random.randint(1, 3)):
                SubTask.objects.create(
                    parent_task=task,
                    title=fake.sentence(nb_words=4),
                    status=fake.random_element(elements=statuses),
                )

        self.stdout.write(self.style.SUCCESS(
            f"Created {options['count']} tasks with notes and subtasks."
        ))
