import logging
from socialtalkBE.models import Posts,PostLikes;
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings

logging.basicConfig(filename='server.log', level=logging.INFO)

class LikePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method == 'POST' :
            
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                try:                    
                    token_backend = TokenBackend(
                    algorithm=settings.SIMPLE_JWT['ALGORITHM'], 
                    signing_key=settings.SIMPLE_JWT['SIGNING_KEY']
                    )
                    valid_data = token_backend.decode(token, verify=True)
                    user_type = valid_data.get('user_type')
                    user_name = valid_data.get('user_name')
                except (InvalidToken, TokenError) as e:
                    logging.error(f"Token error: {str(e)}")
                    return JsonResponse({'error': 'Invalid token'}, status=401)
            else:
                return JsonResponse({'error': 'Authorization header missing or malformed'}, status=401)
            
            id=request.data.get("post_id")
            if not id:
                return Response({'detail':'post_id is required'},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                post_instance = Posts.objects.get(id=id)

            except Exception as e:
                return Response({'detail':'post_id not found'+' '+str(e)},status=status.HTTP_404_NOT_FOUND)
            
            try:
                post_likes_data = PostLikes.objects.filter(post_id=id,username=user_name)
                if post_likes_data:
                    return Response({'detail':'you have already liked the post'},status=status.HTTP_400_BAD_REQUEST)
                new_post_like = PostLikes(
                    username=user_name,
                    post=post_instance
                )
                new_post_like.save()
                
                post_instance.likes= post_instance.likes+1
                post_instance.save()
                return Response({'detail':'your like added to the post'},status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error':'error with database'+' '+str(e)},status=status.HTTP_400_BAD_REQUEST)
            


        else:
            return Response({"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            