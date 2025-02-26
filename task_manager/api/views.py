from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView
)
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from .models import Task, User, TaskHistory
from .serializer import TaskSerializer, UserSerializer

# ===== TASK VIEWS =====

class UserTaskListView(ListAPIView):
    """
    Zwraca listę zadań przypisanych do konkretnego użytkownika.
    """
    permission_classes = [AllowAny]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Task.objects.filter(assigned_user=user_id)


class TaskCreateView(CreateAPIView):
    """
    Tworzy nowe zadanie.
    """
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        serializer.save(created_at=timezone.now())


class TaskHistoryView(APIView):
    """
    Zwraca historię zmian danego zadania.
    """
    permission_classes = [AllowAny]

    def get(self, request, task_id):
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


class TaskFilterView(ListAPIView):
    """
    Zwraca listę zadań z możliwością filtrowania według statusu, słowa kluczowego lub przypisanego użytkownika.
    """
    permission_classes = [AllowAny]
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = Task.objects.all()
        status_param = self.request.query_params.get('status')
        keyword = self.request.query_params.get('keyword')
        assigned_user = self.request.query_params.get('assigned_user')
        if status_param:
            qs = qs.filter(status=status_param.upper())
        if keyword:
            qs = qs.filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))
        if assigned_user:
            qs = qs.filter(assigned_user=assigned_user)
        return qs


class TaskEditView(APIView):
    """
    Pozwala na aktualizację (PUT/POST) oraz usunięcie (DELETE) zadania.
    Przed aktualizacją/usunięciem dodaje wpis do historii.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Dodajemy wpis do historii przed aktualizacją
        TaskHistory.objects.create(
            task_id=task.id,
            name=task.name,
            description=task.description,
            assigned_user=task.assigned_user,
            created_at=task.created_at,
            updated_at=timezone.now()
        )
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Dodajemy wpis do historii przed usunięciem
        TaskHistory.objects.create(
            task_id=task.id,
            name=task.name,
            description=task.description,
            assigned_user=task.assigned_user,
            created_at=task.created_at,
            updated_at=timezone.now()
        )
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request, task_id):
        # Jeśli metoda POST ma działać jak aktualizacja, przekierowujemy do PUT
        return self.put(request, task_id)


class TaskDeleteView(APIView):
    """
    Alternatywny widok do usuwania zadania (może być użyty zamiast metody DELETE w TaskEditView).
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        TaskHistory.objects.create(
            task_id=task.id,
            name=task.name,
            description=task.description,
            assigned_user=task.assigned_user,
            created_at=task.created_at,
            updated_at=timezone.now()
        )
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskListView(ListAPIView):
    """
    Zwraca wszystkie zadania.
    """
    permission_classes = [AllowAny]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskDetailView(RetrieveAPIView):
    """
    Zwraca szczegóły konkretnego zadania.
    """
    permission_classes = [AllowAny]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'task_id'


# ===== USER VIEWS =====

class UserListView(ListAPIView):
    """
    Zwraca listę wszystkich użytkowników.
    """
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginUserView(APIView):
    """
    Logowanie użytkownika i zwrócenie tokenów.
    """
    permission_classes = [AllowAny]

    def post(self, request):
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
            'name': user.username
        })


class RegisterUserView(APIView):
    """
    Rejestracja nowego użytkownika.
    """
    permission_classes = [AllowAny]

    def post(self, request):
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
