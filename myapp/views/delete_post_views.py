import logging
from socialtalkBE.models import Posts,Comments,Hashtags,PostLikes;
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

class DeletePostView(APIView):
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


        id = request.data.get('post_id')

        if not id:
            return Response({'detail': 'post id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(id, int):
            return Response({'detail': 'post id should be integer'}, status=status.HTTP_400_BAD_REQUEST)
        
        #checking whether this user created the post
        post_data = Posts.objects.filter(id=id)
        
        for post in post_data:
            if user_name !=post.username:
                    return Response({'detail':'post is not created by this user'},status=status.HTTP_400_BAD_REQUEST)

        # Query the post to delete
        try:
            post_to_delete = Posts.objects.filter(
                Q(id=id)
            )
            if not post_to_delete:
                return Response({'detail': 'post not found'}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                comments_to_delete = Comments.objects.filter(
                    Q(post_id=id)
                )
                if comments_to_delete:
                    comments_to_delete.delete()
                
                hashtags_to_delete = Hashtags.objects.filter(
                    Q(post_id=id)
                )
                if hashtags_to_delete:
                    hashtags_to_delete.delete()

                likes_to_delete = PostLikes.objects.filter(
                    Q(post_id=id)
                )
                if likes_to_delete:
                    likes_to_delete.delete()
                post_to_delete.delete()
            except Exception as e:
                return Response({'error':e},status= status.HTTP_404_NOT_FOUND)
            return Response({'detail': 'Post deleted successfully'}, status=status.HTTP_200_OK)
        except Posts.DoesNotExist:
            return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

