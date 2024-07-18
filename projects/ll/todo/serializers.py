from rest_framework import serializers
from .models import TodoItem, TodoItemDate

class TodoItemDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoItemDate
        fields = '__all__'

class TodoItemSerializer(serializers.ModelSerializer):
    # dates = TodoItemDateSerializer(many=True, read_only=True)
    class Meta:
        model = TodoItem
        fields = '__all__'  # 모든 필드를 직렬화