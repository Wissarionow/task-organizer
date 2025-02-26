from django.urls import path
from .views import (
    UserTaskListView,
    TaskCreateView,
    TaskHistoryView,
    TaskFilterView,
    TaskEditView,
    TaskDeleteView,
    TaskListView,
    TaskDetailView,
    UserListView,
    LoginUserView,
    RegisterUserView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('user/tasks/<int:user_id>/', UserTaskListView.as_view(), name='get_user_tasks'),
    path('task/create/', TaskCreateView.as_view(), name='create_task'),
    path('task/edit/<int:task_id>/', TaskEditView.as_view(), name='edit_task'),
    path('task/delete/<int:task_id>/', TaskDeleteView.as_view(), name='delete_task'),
    path('user/login/', LoginUserView.as_view(), name='login_user'),
    path('user/register/', RegisterUserView.as_view(), name='register_user'),
    path('user/all/', UserListView.as_view(), name='get_all_users'),
    path('task/all/', TaskListView.as_view(), name='get_all_tasks'),
    path('task/<int:task_id>/', TaskDetailView.as_view(), name='get_task'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('task/filter/', TaskFilterView.as_view(), name='filter_tasks'),
    path('task/history/<int:task_id>/', TaskHistoryView.as_view(), name='get_task_history'),
]
