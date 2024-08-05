from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import TodoItem, TodoItemDate, UserProvidedTodo, User
from .serializers import TodoItemSerializer, TodoItemDateSerializer, UserProvidedTodoSerializer

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .serializers import RegisterSerializer, LoginSerializer

# 회원가입 API View
@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user_email = serializer.validated_data['user_email']
            password = serializer.validated_data['password']
            nickname = serializer.validated_data['nickname']
            user = User.objects.create_user(user_email=user_email, password=password, nickname=nickname)
            return Response({'user_id': user.user_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user_email = serializer.validated_data['user_email']
            password = serializer.validated_data['password']
            user = authenticate(request, user_email=user_email, password=password)
            if user is not None:
                if user.is_login:
                    # 사용자 로그인 상태 업데이트
                    user.is_login = True
                    user.save()  # 데이터베이스에 저장
                    auth_login(request, user)
                    
                    # 사용자 정보를 포함한 응답 반환
                    user_data = {
                        'user_id': user.user_id,
                        'nickname': user.nickname,
                        'level': user.level,
                        'badges': user.badges,
                        'title': user.title,
                        'login_at': user.login_at
                    }
                    return Response(user_data, status=status.HTTP_200_OK)
                return Response({'detail': 'User not active'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 로그아웃 API View
@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        user_id = request.headers.get('X-User-Id')
        if user_id:
            try:
                user = User.objects.get(user_id=user_id)
                if user.is_login:
                    # 사용자 로그아웃 상태 업데이트
                    user.is_login = False
                    user.save()
                    auth_logout(request)
                    return Response({'detail': 'Logged out'}, status=status.HTTP_200_OK)
                return Response({'detail': 'User not active'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'detail': 'User ID header missing'}, status=status.HTTP_400_BAD_REQUEST)


# TodoItem API ViewSet
@method_decorator(csrf_exempt, name='dispatch')
class TodoItemViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer

    def get_user_from_request(self):
        user_id = self.request.headers.get('X-User-Id')
        if user_id:
            return get_object_or_404(User, user_id=user_id, is_login=True)
        return None

# TodoItemDate API ViewSet
@method_decorator(csrf_exempt, name='dispatch')
class TodoItemDateViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    
    queryset = TodoItemDate.objects.all()
    serializer_class = TodoItemDateSerializer

    def perform_create(self, serializer):
        user = self.get_user_from_request()
        serializer.save(user=user)

    def get_user_from_request(self):
        user_id = self.request.headers.get('X-User-Id')
        if user_id:
            return get_object_or_404(User, user_id=user_id, is_login=True)
        return None

# CalendarRead API View
@method_decorator(csrf_exempt, name='dispatch')
class CalendarReadAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, item_name, format=None):
        """
        특정 item_name에 대한 일정을 읽어오는 GET 요청을 처리합니다.
        """
        # 사용자 인증 확인
        user_id = request.headers.get('X-User-Id')
        if user_id:
            user = get_object_or_404(User, user_id=user_id, is_login=True)
        else:
            return Response({'detail': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        # TodoItem 객체 조회
        item = TodoItem.objects.filter(name=item_name).first()
        if not item:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        # TodoItemDate 객체 조회
        dates = TodoItemDate.objects.filter(item=item, user=user).values_list('date', flat=True)

        return Response({'item': item_name, 'dates': list(dates)})

# CalendarCount API View
@method_decorator(csrf_exempt, name='dispatch')
class CalendarCountAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        user = self.get_user_from_request()

        if not user:
            return Response({'detail': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        date_counts = (
            TodoItemDate.objects
            .filter(user=user)
            .values('date')
            .annotate(count=Count('date'))
            .order_by('date')
        )
        return Response({'date_counts': list(date_counts)})

    def get_user_from_request(self):
        user_id = self.request.headers.get('X-User-Id')
        if user_id:
            return get_object_or_404(User, user_id=user_id, is_login=True)
        return None

# UserProvidedTodo API ViewSet
@method_decorator(csrf_exempt, name='dispatch')
class UserProvidedTodoViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]

    queryset = UserProvidedTodo.objects.all()
    serializer_class = UserProvidedTodoSerializer

    def get_queryset(self):
        user = self.get_user_from_request()
        if user:
            return UserProvidedTodo.objects.filter(user=user)
        return UserProvidedTodo.objects.none()

    def perform_create(self, serializer):
        user = self.get_user_from_request()
        if user:
            serializer.save(user=user)
        else:
            return Response({'detail': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    def get_user_from_request(self):
        user_id = self.request.headers.get('X-User-Id')
        if user_id:
            return get_object_or_404(User, user_id=user_id, is_login=True)
        return None

@method_decorator(csrf_exempt, name='dispatch')
class UserProvidedTodoSaveAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        user = self.get_user_from_request()

        if not user:
            return Response({'detail': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        # Extract the list of new todo items from the request
        new_todos = request.data.get('user_todo', [])
        
        # Retrieve or create a UserProvidedTodo instance for the user
        user_todo, created = UserProvidedTodo.objects.get_or_create(user=user)
        
        # Merge existing todos with the new ones
        existing_todos = user_todo.user_todo or []
        updated_todos = list(set(existing_todos + new_todos))  # Remove duplicates by converting to set and back to list
        
        # Update the UserProvidedTodo instance
        user_todo.user_todo = updated_todos
        user_todo.save()
        
        # Serialize and return the updated data
        serializer = UserProvidedTodoSerializer(user_todo)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_user_from_request(self):
        user_id = self.request.headers.get('X-User-Id')
        if user_id:
            return get_object_or_404(User, user_id=user_id, is_login=True)
        return None

# UserProvidedTodoRead API View
@method_decorator(csrf_exempt, name='dispatch')
class UserProvidedTodoReadAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        user = self.get_user_from_request()
        if not user:
            return Response({'detail': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        todos = UserProvidedTodo.objects.filter(user=user)
        serializer = UserProvidedTodoSerializer(todos, many=True)
        return Response(serializer.data)

    def get_user_from_request(self):
        user_id = self.request.headers.get('X-User-Id')
        if user_id:
            return get_object_or_404(User, user_id=user_id, is_login=True)
        return None