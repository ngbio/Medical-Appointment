import json
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings


@api_view(['GET'])
def get_menu(request):
    user = request.user

    if not user.is_authenticated:
        role = "guest"
    else:
        role = user.role  # đã có field role

    path = os.path.join(settings.BASE_DIR, f"data/menu_bar/{role}.json")

    if not os.path.exists(path):
        path = os.path.join(settings.BASE_DIR, "data/menu_bar/guest.json")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return Response(data)