import logging
from socialtalkBE.models import Posts,Hashtags,Comments;
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings

logging.basicConfig(filename='server.log', level=logging.INFO)

class SearchHashtagView(APIView):
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
                    user_name = valid_data.get('user_name')
                except (InvalidToken, TokenError) as e:
                    logging.error(f"Token error: {str(e)}")
                    return JsonResponse({'error': 'Invalid token'}, status=401)
            else:
                return JsonResponse({'error': 'Authorization header missing or malformed'}, status=401)

            hashtag = request.data.get("hashtag")
            if not hashtag:
                return Response({'error': 'hashtag param is required'}, status=status.HTTP_400_BAD_REQUEST)


            posts = []
            hashtag_queryset = Hashtags.objects.filter(hashtag__icontains = hashtag)
            
            for hashtag in hashtag_queryset:
                try:
                    post_queryset = Posts.objects.filter(id=hashtag.post_id)
                    
                    for post in post_queryset:
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
                        hashtags_queryset = Hashtags.objects.filter(post_id=post.id)

                        comments_queryset = Comments.objects.filter(post_id=post.id)

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

                        posts.append(post_data)
                except Exception as e:
                    return Response({'error':e},status= status.HTTP_404_NOT_FOUND)
            return JsonResponse({'posts': posts})
        else:
            return Response({"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

