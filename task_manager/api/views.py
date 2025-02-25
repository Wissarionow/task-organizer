from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from .models import Task, User, TaskHistory
from .serializer import TaskSerializer, UserSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

##############
####TASK######
##############
@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_tasks(request, user_id):
    try:
        tasks = Task.objects.filter(assigned_user=user_id)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    try:
        request.data['created_at'] = timezone.now()
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_task_history(request, task_id):
    try:
        task_history = TaskHistory.objects.filter(task_id=task_id).order_by('-updated_at')
        
        if not task_history.exists():
            return Response({"message": "No history found for this task"}, status=status.HTTP_404_NOT_FOUND)

        history_data = []
        for entry in task_history:
            history_data.append({
                "name": entry.name,
                "description": entry.description,
                "assigned_user": entry.assigned_user.username if entry.assigned_user else "Unassigned",
                "created_at": entry.created_at,
                "updated_at": entry.updated_at,
                "deleted_at": entry.deleted_at
            })

        return Response(history_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def filter_tasks(request):
    try:
        status = request.GET.get('status', None)
        keyword = request.GET.get('keyword', None)
        assigned_user = request.GET.get('assigned_user', None)

        tasks = Task.objects.all()

        if status:
            tasks = tasks.filter(status=status.upper())

        if keyword:
            tasks = tasks.filter(
                Q(description__icontains=keyword) | Q(name__icontains=keyword)
            )

        if assigned_user:
            tasks = tasks.filter(assigned_user=assigned_user)
        
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT','POST','DELETE'])
@permission_classes([IsAuthenticated])
def edit_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        
        #add to history
        TaskHistory.objects.create(
            task_id=task.id,
            name=task.name,
            description=task.description,
            assigned_user=task.assigned_user,
            created_at=task.created_at,
            updated_at=timezone.now(),
        )
        
        if request.method == 'DELETE':
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = TaskSerializer(instance=task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        
        # add to history
        TaskHistory.objects.create(
            task_id=task.id,
            name=task.name,
            description=task.description,
            assigned_user=task.assigned_user,
            created_at=task.created_at,
            updated_at=timezone.now(),
        )
        
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ObjectDoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_tasks(request):
    try:
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

##############
####USER######
##############
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_users(request):
    try:
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    try:
        username = request.data.get('name')
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username)
            if not check_password(password, user.password):
                return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'name': user.name
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    try:
        data = request.data.copy()

        if User.objects.filter(username=data.get('username')).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=data.get('email')).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User created successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'name': user.username
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)