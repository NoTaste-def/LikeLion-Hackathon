from django.contrib.auth.hashers import make_password, check_password
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import TodoItem, TodoItemDate, UserProvidedTodo, User
from .serializers import TodoItemSerializer, TodoItemDateSerializer, UserProvidedTodoSerializer

# CSRF 토큰 발급 API
@method_decorator(csrf_exempt, name='dispatch')
class CsrfTokenView(APIView):
    permission_classes = [AllowAny]  # 모든 사용자에게 접근 허용
    def get(self, request, *args, **kwargs):
        token = get_token(request)
        return Response({'csrfToken': token}, status=status.HTTP_200_OK)

# TodoItem API ViewSet
class TodoItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TodoItem.objects.all()
    serializer_class = TodoItemSerializer

# TodoItemDate API ViewSet
class TodoItemDateViewSet(viewsets.ModelViewSet):
    queryset = TodoItemDate.objects.all()
    serializer_class = TodoItemDateSerializer

    def perform_create(self, serializer):
        user_id = self.request.data.get('user_id')
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer.save(user=user)

# CalendarRead API View
class CalendarReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, item_name, format=None):
        user_id = request.headers.get('User-ID')
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = TodoItem.objects.get(name=item_name)  # 이름으로 TodoItem 검색
        except TodoItem.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        # 로그인한 사용자와 관련된 날짜만 조회
        dates = TodoItemDate.objects.filter(item=item, user=user).values_list('date', flat=True)
        return Response({'item': item_name, 'dates': list(dates)})

# CalendarCount API View
class CalendarCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_id = request.headers.get('User-ID')
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

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
    queryset = UserProvidedTodo.objects.all()
    serializer_class = UserProvidedTodoSerializer

    def get_queryset(self):
        user_id = self.request.headers.get('User-ID')
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return UserProvidedTodo.objects.none()
        return UserProvidedTodo.objects.filter(user=user)

    def perform_create(self, serializer):
        user_id = self.request.data.get('user_id')
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer.save(user=user)

# UserProvidedTodoSave API View
class UserProvidedTodoSaveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            data = request.data
            user_todo_list = data.get('user_todo', [])
            user_id = data.get('user_id')

            if not user_todo_list or not user_id:
                return Response({"error": "user_todo와 user_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # 기존 UserProvidedTodo가 있다면 삭제하고 새로 생성
            UserProvidedTodo.objects.filter(user=user).delete()

            # 사용자에 대한 TODO 리스트 저장
            user_todo_obj = UserProvidedTodo.objects.create(user=user, user_todo=user_todo_list)

            serializer = UserProvidedTodoSerializer(user_todo_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# UserProvidedTodoRead API View
class UserProvidedTodoReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_id = request.headers.get('User-ID')
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_todo = UserProvidedTodo.objects.get(user=user)
        except UserProvidedTodo.DoesNotExist:
            return Response({"error": "User's TODO not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProvidedTodoSerializer(user_todo)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Register API View
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
                password=make_password(password)  # 비밀번호 해싱
            )
            user.save()
            return Response({"message": "회원가입 성공"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Login API View
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            user_email = data.get("user_email")
            password = data.get("password")

            if not (user_email and password):
                return Response({"error": "모든 값을 입력해 주세요."}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(user_email=user_email).first()
            if user and check_password(password, user.password):
                # 인증 성공
                request.session['user_id'] = user.user_id

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

# Logout API View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 로그아웃 처리
        request.session.pop('user_id', None)

        return Response({"message": "로그아웃 성공"}, status=status.HTTP_200_OK)
