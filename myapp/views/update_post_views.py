import logging
from socialtalkBE.models import Posts,Hashtags;
from django.db.models import Q
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend
from django.contrib.auth import authenticate
from django.conf import settings

logging.basicConfig(filename='server.log', level=logging.INFO)

class UpdatePostView(APIView):
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
        caption = request.data.get('caption')
        image_file = request.data.get('image')
        hashtags = request.data.get('hashtags')
        id = request.data.get('post_id')
        if not all([caption, image_file,hashtags]):
            return Response({'detail': 'All parameters are required'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(image_file,str):
            return Response({'detail': 'image path is not a string'}, status=status.HTTP_400_BAD_REQUEST)
        
        image_path = f"post_images/{image_file}"

        post_info = Posts.objects.filter(id=id)
        if not post_info:
            return Response({'detail':'post not found'},status=status.HTTP_400_BAD_REQUEST)
        for post_data in post_info:
            if user_name !=post_data.username:
                    return Response({'detail':'post is not created by this user'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the post instance to update
            post_instance = Posts.objects.get(id=id)
            
            # Update fields if provided
            if caption:
                post_instance.caption = caption
            if image_file:
                post_instance.image = image_path
            

            # Save the updated instance
            post_instance.save()

            try:

                if hashtags:
                    hashtags_to_delete = Hashtags.objects.filter(
                        Q(post_id=id)
                    )
                    if hashtags_to_delete:
                        hashtags_to_delete.delete()
                    for hashtag in hashtags:
                        hashtag_obj = Hashtags.objects.create(
                            hashtag=hashtag,
                            post = post_instance
                        )
                        hashtag_obj.save()
            except Exception as e:
                print("error",str(e))
                return Response({'detail': 'Error updating hashtags table'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("error",str(e))
            return Response({'detail': 'Error updating posts table'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'detail': 'post updated successfully'}, status=status.HTTP_201_CREATED)
