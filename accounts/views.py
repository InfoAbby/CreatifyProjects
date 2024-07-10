import json

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer

User = get_user_model()


class SignupView(APIView):
    def post(self, request):
        data = json.loads(request.body)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return JsonResponse({'id': user.id, 'email': user.email}, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SigninView(APIView):
    def post(self, request):
        data = json.loads(request.body)

        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            return JsonResponse({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(data['password']):
            return JsonResponse({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return JsonResponse({'id': user.id, 'email': user.email})
