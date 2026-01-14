from django.shortcuts import render

# Create your views here.
# views.py
from django.http import JsonResponse
from .models import Conversation

def chat_list(request):
    user = request.user.customuser

    conversations = Conversation.objects.filter(
        user=user
    ) | Conversation.objects.filter(
        employee=user
    )

    data = []
    for c in conversations:
        other = c.employee if c.user == user else c.user
        last_msg = c.messages.last()

        data.append({
            "id": c.id,
            "name": other.user.username,
            "avatar": "",  # optional
            "lastMessage": last_msg.text if last_msg else "",
            "timestamp": last_msg.timestamp.strftime("%H:%M") if last_msg else "",
            "unread": c.messages.filter(is_read=False).count(),
            "online": False,
            "type": "personal"
        })

    return JsonResponse(data, safe=False)
