import logging
from socialtalkBE.models import CustomUser,Posts,Comments,Hashtags;
from django.db.models import Q
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings

logging.basicConfig(filename='server.log', level=logging.INFO)

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
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


        username = request.data.get('username')

        if not username:
            return Response({'detail': 'username is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(username, str):
            return Response({'detail': 'username should be string'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user_name != username:
            return Response({'detail': 'you cannot delete other user'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_data = CustomUser.objects.filter(username=username)
        if not user_data:
            return Response({'detail': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Query the post to delete
        try:
            user_to_delete = CustomUser.objects.filter(
                Q(username=username)
            )
            post_to_delete = Posts.objects.filter(
                Q(username=username)
            )
            if post_to_delete:
                for post in post_to_delete:
                    post_id=post.id
                try:
                    comments_to_delete = Comments.objects.filter(
                        Q(post_id=post_id)
                    )
                    if comments_to_delete:
                        comments_to_delete.delete()
                    
                    hashtags_to_delete = Hashtags.objects.filter(
                        Q(post_id=post_id)
                    )
                    if hashtags_to_delete:
                        hashtags_to_delete.delete()
                    post_to_delete.delete()
                except Exception as e:
                    return Response({'error':e},status= status.HTTP_404_NOT_FOUND)
            user_to_delete.delete()

            return Response({'detail': 'User deleted successfully'}, status=status.HTTP_200_OK)
        except Posts.DoesNotExist:
            return Response({'detail': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

