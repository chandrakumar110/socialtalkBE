import logging
from socialtalkBE.models import Comments;
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings

logging.basicConfig(filename='server.log', level=logging.INFO)


class CommentPostView(APIView):
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
        try:
            comment = request.data.get('comment')
            post_id = request.data.get('post_id')
            if not all([comment, post_id]):
                return Response({'detail': 'All parameters are required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': 'comment and post_id should be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        try:
            # Create a new instance of the Comment model
            new_comment = Comments(
            comment=comment,
            post_id=post_id,
            username=user_name,
            )

            # Save the new instance to the database
            new_comment.save()
        except Exception as e:
            print("error",str(e))
            return Response({'detail': 'Error inserting data into comments table'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'detail': 'comment added successfully'}, status=status.HTTP_201_CREATED)
