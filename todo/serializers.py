from rest_framework import serializers
from .models import TodoItem, TodoItemDate, UserProvidedTodo, User

class TodoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoItem
        fields = '__all__'

class TodoItemDateSerializer(serializers.ModelSerializer):
    item = serializers.CharField()  # 문자열로 처리

    class Meta:
        model = TodoItemDate
        fields = ['item', 'date']

    def to_internal_value(self, data):
        # 문자열을 기본키로 변환하여 internal_value로 설정
        if 'item' in data:
            try:
                item = TodoItem.objects.get(name=data['item'])
                data['item'] = item.id
            except TodoItem.DoesNotExist:
                raise serializers.ValidationError({"item": "Invalid item name"})
        return super().to_internal_value(data)

    def create(self, validated_data):
        # 변환된 TodoItem 객체를 사용하여 저장
        item_id = validated_data.pop('item')
        item = TodoItem.objects.get(id=item_id)
        return TodoItemDate.objects.create(item=item, **validated_data)


class UserProvidedTodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProvidedTodo
        fields = ['user_todo', 'created_at']