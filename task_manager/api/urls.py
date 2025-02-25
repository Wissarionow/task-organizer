from django.urls import path
from .views import (get_user_tasks, 
                    create_task, 
                    edit_task, 
                    delete_task, 
                    login_user, register_user, 
                    get_all_users, get_all_tasks, 
                    get_task,
                    filter_tasks,
                    get_task_history
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('user/tasks/<int:user_id>/', get_user_tasks, name='get_user_tasks'),
    path('task/create/', create_task, name='create_task'),
    path('task/edit/<int:task_id>/', edit_task, name='edit_task'),
    path('task/delete/<int:task_id>/', delete_task, name='delete_task'),
    path('user/login/', login_user, name='login_user'),
    path('user/register/', register_user, name='register_user'),
    path('user/all/', get_all_users, name='get_all_users'),
    path('task/all/', get_all_tasks, name='get_all_tasks'),
    path('task/<int:task_id>/', get_task, name='get_task'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('task/filter/', filter_tasks, name='filter_tasks'),
    path('task/history/<int:task_id>/', get_task_history, name='get_task_history'),


]