from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import TodoItem

@receiver(post_migrate)
def create_initial_todo_items(sender, **kwargs):
    if sender.name == 'todo':
        items = TodoItem.ITEM_CHOICES
        for item in items:
            TodoItem.objects.get_or_create(name=item[0], defaults={'name': item[1]})
