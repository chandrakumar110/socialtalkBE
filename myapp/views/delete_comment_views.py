import logging
from socialtalkBE.models import Comments;
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


class DeleteCommentView(APIView):
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


        id = request.data.get('comment_id')
        if not all([id]):
            return Response({'detail': 'comment id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(id, int):
            return Response({'detail': 'comment id should be integer'}, status=status.HTTP_400_BAD_REQUEST)
        
        #checking whether this user added the comment
        comment_data = Comments.objects.filter(id=id)

        if comment_data:
            for comment in comment_data:
                if user_name !=comment.username:
                        return Response({'detail':'comment is not added by this user'},status=status.HTTP_400_BAD_REQUEST)

        # Query the post to delete
        try:
            comment_to_delete = Comments.objects.filter(
                Q(id=id)
            )
            if not comment_to_delete:
                return Response({'detail': 'comment not found'}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                comment_to_delete.delete()
            except Exception as e:
                return Response({'error':e},status= status.HTTP_404_NOT_FOUND)
            return Response({'detail': 'comment deleted successfully'}, status=status.HTTP_200_OK)
        except Comments.DoesNotExist:
            return Response({'detail': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

