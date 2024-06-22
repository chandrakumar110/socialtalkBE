import logging
from socialtalkBE.models import Posts,Hashtags;
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings

logging.basicConfig(filename='server.log', level=logging.INFO)

class CreatePostView(APIView):
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
                user_name = valid_data.get('user_name')
            except (InvalidToken, TokenError) as e:
                logging.error(f"Token error: {str(e)}")
                return JsonResponse({'error': 'Invalid token'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header missing or malformed'}, status=401)

        
        # Validate parameters
        caption = request.data.get('caption')
        image_file = request.data.get('image')
        hashtags = request.data.get('hashtags')
        if not all([caption, image_file,hashtags]):
            return Response({'detail': 'All parameters are required'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(image_file,str):
            return Response({'detail': 'image path is not a string'}, status=status.HTTP_400_BAD_REQUEST)
        
        image_path = f"post_images/{image_file}"
        try:
            # Create a new instance of the Posts model
            new_post = Posts(
            caption=caption,
            image=image_path,
            username=user_name,
            )

            # Save the new instance to the database
            new_post.save()

            #handle hashtags
            if hashtags:
                for hashtag in hashtags:
                    hashtag_obj = Hashtags.objects.create(
                        hashtag=hashtag,
                        post=new_post
                    )
                    hashtag_obj.save()
        except Exception as e:
            logging.error("hey",str(e))
            return Response({'detail': 'Error inserting data into posts table'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'detail': 'post created successfully'}, status=status.HTTP_201_CREATED)
