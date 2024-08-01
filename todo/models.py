from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Group, Permission

class UserManager(BaseUserManager):
    def create_user(self, user_email, nickname, password=None):
        if not user_email:
            raise ValueError("Users must have an email address")
        if not nickname:
            raise ValueError("Users must have a nickname")

        user = self.model(
            user_email=self.normalize_email(user_email),
            nickname=nickname,
        )
        user.set_password(password)  # 비밀번호 해싱
        user.save(using=self._db)
        return user

    def create_superuser(self, user_email, nickname, password=None):
        user = self.create_user(
            user_email,
            nickname=nickname,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    user_email = models.EmailField(max_length=64, unique=True)
    nickname = models.CharField(max_length=64)
    level = models.IntegerField(default=1)
    badges = models.CharField(max_length=64, null=True, blank=True)
    title = models.CharField(max_length=64, null=True, blank=True)
    login_at = models.DateField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return self.user_email

    class Meta:
        db_table = 'user'
        verbose_name = '사용자 id'
        verbose_name_plural = '사용자'

    # Update the related_name for permissions and groups
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


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
    user_todo = models.JSONField()  # TODO 항목 내용, List 형태로 저장
    created_at = models.DateField(auto_now_add=True)  # 생성 날짜

    def __str__(self):
        return str(self.user_todo)  # 변경: 리스트를 문자열로 변환
