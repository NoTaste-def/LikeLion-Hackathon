from django.contrib.auth.hashers import make_password, check_password
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.contrib.auth import get_user_model, authenticate, login as auth_login
from django.contrib.auth import logout as django_logout

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from .models import TodoItem, TodoItemDate, UserProvidedTodo
from .serializers import TodoItemSerializer, TodoItemDateSerializer, UserProvidedTodoSerializer

# from datetime import date
from django.utils import timezone

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication

User = get_user_model()

# CSRF 토큰 발급 API
@method_decorator(csrf_exempt, name='dispatch')
class CsrfTokenView(APIView):
    permission_classes = [AllowAny]  # 모든 사용자에게 접근 허용
    def get(self, request, *args, **kwargs):
        token = get_token(request)
        return Response({'csrfToken': token}, status=status.HTTP_200_OK)

# TodoItem API ViewSet
class TodoItemViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [SessionAuthentication]
    
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer


class TodoItemDateViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = TodoItemDate.objects.all()
    serializer_class = TodoItemDateSerializer

    def perform_create(self, serializer):
        user = self.request.user  # 현재 로그인된 사용자
        serializer.save(user=user)  # user 필드에 현재 사용자 설정


class CalendarReadAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, item_name, format=None):
        user = request.user  # 현재 로그인된 사용자 가져오기
        
        try:
            item = TodoItem.objects.get(name=item_name)  # 이름으로 TodoItem 검색
        except TodoItem.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # 로그인한 사용자와 관련된 날짜만 조회
        dates = TodoItemDate.objects.filter(item=item, user=user).values_list('date', flat=True)
        return Response({'item': item_name, 'dates': list(dates)})


class CalendarCountAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user  # 현재 로그인된 사용자 가져오기
        
        date_counts = (
            TodoItemDate.objects
            .filter(user=user)  # 로그인한 사용자와 관련된 데이터만 필터링
            .values('date')
            .annotate(count=Count('date'))  # 날짜별 카운트 집계
            .order_by('date')
        )
        return Response({'date_counts': list(date_counts)})


# UserProvidedTodo API ViewSet
class UserProvidedTodoViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = UserProvidedTodo.objects.all()
    serializer_class = UserProvidedTodoSerializer

    def get_queryset(self):
        user = self.request.user
        return UserProvidedTodo.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserProvidedTodoSaveAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            data = request.data
            user_todo_list = data.get('user_todo', [])

            if not user_todo_list:
                return Response({"error": "user_todo가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

            user = request.user

            # 기존 UserProvidedTodo가 있다면 삭제하고 새로 생성
            UserProvidedTodo.objects.filter(user=user).delete()

            # 사용자에 대한 TODO 리스트 저장
            user_todo_obj = UserProvidedTodo.objects.create(user=user, user_todo=user_todo_list)

            serializer = UserProvidedTodoSerializer(user_todo_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProvidedTodoReadAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user

        try:
            user_todo = UserProvidedTodo.objects.get(user=user)
        except UserProvidedTodo.DoesNotExist:
            return Response({"error": "User's TODO not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProvidedTodoSerializer(user_todo)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = [AllowAny]  # 모든 사용자에게 접근 허용
    
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            user_email = data.get("user_email")
            password = data.get("password")
            nickname = data.get("nickname")

            if not (user_email and password and nickname):
                return Response({"error": "모든 값을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(user_email=user_email).exists():
                return Response({"error": "이미 사용 중인 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)

            user = User(
                user_email=user_email,
                nickname=nickname,
            )
            user.set_password(password) # 비밀번호 해싱
            user.save()
            return Response({"message": "회원가입 성공"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            user_email = data.get("user_email")
            password = data.get("password")

            if not (user_email and password):
                return Response({"error": "모든 값을 입력해 주세요."}, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(request, user_email=user_email, password=password)
            if user is not None:
                auth_login(request, user)

                # 로그인 날짜 갱신 및 UserProvidedTodo 항목 삭제
                user.login_at = timezone.now()
                user.save()

                # user의 UserProvidedTodo 중 생성 날짜가 마지막 로그인 날짜보다 이전인 항목 삭제
                UserProvidedTodo.objects.filter(user=user, created_at__lt=user.login_at).delete()

                return Response({
                    "message": "로그인 성공",
                    "user_email": user.user_email,
                    "nickname": user.nickname,
                    "level": user.level,
                    "badges": user.badges,
                    "title": user.title,
                    "login_at": user.login_at
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "비밀번호 혹은 이메일이 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "존재하지 않는 사용자입니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# @method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 현재 로그인된 사용자 가져오기
        # current_user = request.user

        # 로그아웃 처리, 세션 종료
        django_logout(request)
        
        return Response({"message": "로그아웃 성공"}, status=status.HTTP_200_OK)