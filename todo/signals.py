from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import TodoItem

@receiver(post_migrate)
def create_initial_todo_items(sender, **kwargs):
    if sender.name == 'todo':
        items = TodoItem.ITEM_CHOICES
        for item in items:
            try:
                TodoItem.objects.get_or_create(name=item[0], defaults={'name': item[1]})
            except Exception as e:
                print(f"Error creating item: {item}, Error: {e}")
