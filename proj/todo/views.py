from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action

from .models import TodoItem, TodoItemDate, UserProvidedTodo
from .serializers import TodoItemSerializer, TodoItemDateSerializer, UserProvidedTodoSerializer

from django.db.models import Count
from django.http import JsonResponse

class TodoItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer

class TodoItemDateViewSet(viewsets.ModelViewSet):
    queryset = TodoItemDate.objects.all()
    serializer_class = TodoItemDateSerializer

class CalendarReadAPIView(APIView):
    def get(self, request, item_name, format=None):
        try:
            item = TodoItem.objects.get(name=item_name)
        except TodoItem.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        dates = TodoItemDate.objects.filter(item=item).values_list('date', flat=True)
        return Response({'item': item_name, 'dates': list(dates)})

class CalendarCountAPIView(APIView):
    def get(self, request, format=None):
        date_counts = (
            TodoItemDate.objects
            .values('date')
            .annotate(count=Count('date'))
            .order_by('date')
        )
        return Response({'date_counts': list(date_counts)})

class UserProvidedTodoViewSet(viewsets.ModelViewSet):
    queryset = UserProvidedTodo.objects.all()
    serializer_class = UserProvidedTodoSerializer

    def perform_create(self, serializer):
        serializer.save()

class UserProvidedTodoAPIView(APIView):
    def post(self, request, format=None):
        serializer = UserProvidedTodoSerializer(data=request.data)
        
        if serializer.is_valid():
            user_todo_string = serializer.validated_data.get('user_todo', '')
            user_todo_list = [todo.strip() for todo in user_todo_string.split(',') if todo.strip()]
            
            # 데이터베이스에 저장
            user_todo_obj = UserProvidedTodo.objects.create(user_todo=', '.join(user_todo_list))
            
            # 성공적으로 저장되었음을 응답
            return Response({'detail': 'Successfully created.', 'id': user_todo_obj.id}, status=status.HTTP_201_CREATED)
        else:
            # 유효성 검사 실패 시 에러 응답
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
# 유저 완성되면 쓰기        
# class UserProvidedTodoAPIView(APIView):
#     def post(self, request, format=None):
#         serializer = UserProvidedTodoSerializer(data=request.data)
        
#         if serializer.is_valid():
#             # 요청을 보낸 유저 정보 가져오기 (예시: 로그인한 유저)
#             user = request.user
            
#             user_todo_string = serializer.validated_data.get('user_todo', '')
#             user_todo_list = [todo.strip() for todo in user_todo_string.split(',') if todo.strip()]
            
#             # 데이터베이스에 저장
#             user_todo_obj = UserProvidedTodo.objects.create(user=user, user_todo=', '.join(user_todo_list))
            
#             # 성공적으로 저장되었음을 응답
#             return Response({'detail': 'Successfully created.', 'id': user_todo_obj.id}, status=status.HTTP_201_CREATED)
#         else:
#             # 유효성 검사 실패 시 에러 응답
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)