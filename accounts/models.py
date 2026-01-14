from django.contrib.auth.models import User
from django.db import models

class CustomUser(models.Model):
    USER_TYPES = (
        ('user', 'Regular User'),
        ('employee', 'Employee'),
        ('admin', 'Administrator'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"
    


class Conversation(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='user_chats'
    )
    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='employee_chats'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.user.user_type != 'user':
            raise ValueError("User must have user_type='user'")
        if self.employee.user_type != 'employee':
            raise ValueError("Employee must have user_type='employee'")

    def __str__(self):
        return f"{self.user} ↔ {self.employee}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} - {self.timestamp}"
