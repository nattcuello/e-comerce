from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.services.services import authenticate_user, generate_jwt_for_user

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate_user(email, password)
        if user:
            token = generate_jwt_for_user(user)
            return Response({
                'access_token': token,
                'user_id': user.id,
                'role_id': user.role_id
            })
        return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
