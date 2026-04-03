import json
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings


@api_view(['GET'])
def get_menu(request):
    user = request.user

    # Xác định role
    if not user.is_authenticated:
        role = "guest"
    else:
        role = getattr(user, "role", None)  # tùy model của em
    # Đường dẫn file JSON
    path = os.path.join(settings.BASE_DIR, f"data\\menu_bar\\{role}.json")

    # fallback nếu không tồn tại
    if not os.path.exists(path):
        path = os.path.join(settings.BASE_DIR, "data\\menu_bar\\guest.json")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return Response(data)