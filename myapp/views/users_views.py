import logging
from socialtalkBE.models import CustomUser;
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings

logging.basicConfig(filename='server.log', level=logging.INFO)

class UsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.method == 'GET' :
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                try:                    
                    token_backend = TokenBackend(
                    algorithm=settings.SIMPLE_JWT['ALGORITHM'], 
                    signing_key=settings.SIMPLE_JWT['SIGNING_KEY']
                    )
                    valid_data = token_backend.decode(token, verify=True)
                    user_name = valid_data.get('user_name')
                except (InvalidToken, TokenError) as e:
                    logging.error(f"Token error: {str(e)}")
                    return JsonResponse({'error': 'Invalid token'}, status=401)
            else:
                return JsonResponse({'error': 'Authorization header missing or malformed'}, status=401)

            #Query to fetch all user data
            user_queryset = CustomUser.objects.all().order_by('username')
            users=[]
            for user in user_queryset:
                user_data = {
                    'username': user.username,
                }
                users.append(user_data)
            return JsonResponse({'users': users})
        else:
            return Response({"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

