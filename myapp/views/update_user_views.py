import logging,re
from socialtalkBE.models import CustomUser;
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

logging.basicConfig(filename='server.log', level=logging.INFO)

class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                
                token_backend = TokenBackend(
                algorithm=settings.SIMPLE_JWT['ALGORITHM'], 
                signing_key=settings.SIMPLE_JWT['SIGNING_KEY']
                )
                valid_data = token_backend.decode(token, verify=True)
                user_name = str(valid_data.get('user_name'))
            except (InvalidToken, TokenError) as e:
                logging.error(f"Token error: {str(e)}")
                return JsonResponse({'error': 'Invalid token'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header missing or malformed'}, status=401)

        
        # Validate parameters
        username = request.data.get('username')
        email = request.data.get('email')
        mobile = request.data.get('mobile')
        password = request.data.get('password')
        
        if user_name != username:
            return Response({'detail': 'you cannot update other user'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username is a string
        if not isinstance(username, str):
            return Response({'error': 'Username should be a string'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if password is a string and meets the requirements
        if not isinstance(password, str):
            return Response({'error': 'Password should be a string'}, status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 8 or not re.search(r'\d', password) or not re.search(r'[a-zA-Z]', password):
            return Response({'error': 'Password should contain at least 1 letter, 1 number, and be at least 8 characters long'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)
        
        #validate mobile
        if not str(mobile).isdigit() or len(str(mobile)) != 10:
            return Response({'error':'Mobile number must be a 10-digit number.'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the user instance to update
            user_instance = CustomUser.objects.get(username=user_name)
            
            # Update fields if provided
            if username:
                user_instance.username = username
            if email:
                user_instance.email = email
            if mobile:
                user_instance.mobile_number = mobile
            if password:
                user_instance.set_password(password)  

            # Save the updated instance
            user_instance.save()
        except Exception as e:
            print("error",str(e))
            return Response({'detail': 'Error updating users table:'+' '+str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'detail': 'user updated successfully'}, status=status.HTTP_201_CREATED)
