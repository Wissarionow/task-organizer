from django.db import models
from django.contrib.auth.models import AbstractUser


class Task(models.Model):
    NEW = 'NEW'
    IN_PROGRESS = 'IN_PROGRESS'
    SOLVED = 'SOLVED'
    STATUS_CHOICES = [
        (NEW, 'New'),
        (IN_PROGRESS, 'In progress'),
        (SOLVED, 'Solved'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(
        max_length=11,
        choices=STATUS_CHOICES,
        default=NEW,
    )

    assigned_user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,  
        null=True, 
        blank=True 
    )
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.name} {self.id}"

class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    assigned_user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,  
        null=True, 
        blank=True 
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True)



class User(AbstractUser):
    email = models.EmailField(unique=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
    )

