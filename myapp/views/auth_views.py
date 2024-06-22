import csv,os,logging,re
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from socialtalkBE.models import CustomUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



logging.basicConfig(filename='server.log', level=logging.INFO)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Save user name in session
            refresh = RefreshToken.for_user(user)
            refresh['user_name'] = username
            return Response({
                'access_token': str(refresh.access_token),
            })
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class SignupView(APIView):
    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        mobile = request.data.get('mobile')
    
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
        
        userExist = CustomUser.objects.filter(username=username)
        if userExist:
            return Response({'error': 'username already exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        emailExist = CustomUser.objects.filter(email=email)
        if emailExist:
            return Response({'error': 'email already exist'}, status=status.HTTP_400_BAD_REQUEST)
        

        # Create user
        try:
            user = CustomUser.objects.create_user(username=username, email=email, password=password,mobile_number=mobile)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)