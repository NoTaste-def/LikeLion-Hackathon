from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from rest_framework.routers import DefaultRouter
from todo import views

router = DefaultRouter()
router.register(r'all-todo-items', views.TodoItemViewSet)
router.register(r'complete', views.TodoItemDateViewSet)
router.register(r'user-todo', views.UserProvidedTodoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),  # Django admin 페이지
    path('csrf-token/', views.CsrfTokenView.as_view(), name='csrf-token'),
    path('calendar/<str:item_name>/', views.CalendarReadAPIView.as_view(), name='calendar-read'),
    path('calendar/cnt/all/', views.CalendarCountAPIView.as_view(), name='calendar-count'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # path('user/', views.UserDetailView.as_view(), name='user_detail'),
    path('save-user-todo/', views.UserProvidedTodoSaveAPIView.as_view(), name='user_todo_save'),
    path('read-user-todo/', views.UserProvidedTodoReadAPIView.as_view(), name='user_todo_read'),
    
    # 이거 안 하면 배포후 미디어 파일 경로를 읽지 못 한다.
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root':settings.MEDIA_ROOT}),
]
