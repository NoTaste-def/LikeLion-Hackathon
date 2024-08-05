from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Group, Permission

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, user_email, password=None, **extra_fields):
        if not user_email:
            raise ValueError('The Email field must be set')
        user = self.model(user_email=user_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(user_email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    user_email = models.EmailField(max_length=64, unique=True)
    nickname = models.CharField(max_length=64)
    password = models.CharField(max_length=128)  # 비밀번호 해싱은 직접 구현해야 합니다
    level = models.IntegerField(default=1)
    badges = models.CharField(max_length=64, null=True, blank=True)
    title = models.CharField(max_length=64, null=True, blank=True)
    login_at = models.DateField(auto_now=True)
    is_login = models.BooleanField(default=False)  # 사용자 활성화 여부

    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = ['nickname']  # 필수 입력 필드로 설정

    objects = UserManager()

    def __str__(self):
        return self.user_email

    class Meta:
        db_table = 'user'
        verbose_name = '사용자 id'
        verbose_name_plural = '사용자'



class TodoItem(models.Model):
    # 할 일 항목의 선택지를 정의합니다.
    ITEM_CHOICES = [
        ('water_8_cups', '물 8컵 마시기'),
        ('breakfast', '아침 식사하기'),
        ('salad', '샐러드 먹기'),
        ('nuts', '견과류 먹기'),
        ('fish', '생선 먹기'),
        ('vegetable_juice', '야채주스 마시기'),
        ('fermented_food', '발효식품 먹기'),
        ('protein', '단백질 먹기'),
        ('cardio', '유산소 운동하기'),
        ('strength_training', '근력 운동하기'),
        ('stretching', '스트레칭하기'),
        ('meditation', '명상하기'),
        ('therapeutic_bath', '목욕하기'),
        ('massage', '마사지 받기'),
        ('sleep_7_hours', '7시간 이상 잠자기'),
    ]

    # 할 일 항목 이름
    name = models.CharField(max_length=255, choices=ITEM_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

class TodoItemDate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(TodoItem, related_name='dates', on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'item', 'date'], name='unique_user_item_date')
        ]


class UserProvidedTodo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자와 연결
    user_todo = models.JSONField(default=list)  # TODO 항목 내용, List 형태로 저장
    created_at = models.DateField(auto_now_add=True)  # 생성 날짜

    def __str__(self):
        return str(self.user_todo)  # 변경: 리스트를 문자열로 변환
