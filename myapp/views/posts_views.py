import logging
from socialtalkBE.models import Posts,Hashtags,Comments;
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings

logging.basicConfig(filename='server.log', level=logging.INFO)

class PostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_posts = []
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

        
        # Query the database for posts data
        posts_queryset = Posts.objects.all().order_by("created_date")

        # Query the database for hashtags data
        hashtags_queryset = Hashtags.objects.all()

        # Query the database for comments data
        comments_queryset = Comments.objects.all()

        for post in posts_queryset:

            post_data = {
                'caption': post.caption,
                'image_info': str(post.image),
                'likes': post.likes,
                'created_on': post.created_date,
                'created_by': post.username,
                'hashtags' : [],
                'comments' : [],
                'id' : post.id
            }

            for hashtag in hashtags_queryset:
                if post.id == hashtag.post_id:
                    post_data['hashtags'].append(hashtag.hashtag)

            for comment in comments_queryset:
                if post.id == comment.post_id:
                    comment_info ={}
                    comment_info['comment'] = comment.comment
                    comment_info['username'] = comment.username
                    comment_info['id'] = comment.id
                    post_data['comments'].append(comment_info)
            
            all_posts.append(post_data)
        return JsonResponse({'posts': all_posts})

