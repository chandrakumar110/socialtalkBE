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


class UpdateCommentView(APIView):
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
        comment = request.data.get('comment')
        id = request.data.get('comment_id')
        if not all([comment, id]):
            return Response({'detail': 'All parameters are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(id,int):
            return Response({'detail': 'comment_id should be integer'}, status=status.HTTP_400_BAD_REQUEST)
        
        comment_info = Comments.objects.filter(id=id)
        if not comment_info:
            return Response({'detail':'comment not found'},status=status.HTTP_400_BAD_REQUEST)
        for comment_data in comment_info:
            if user_name !=comment_data.username:
                    return Response({'detail':'comment is not added by this user'},status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the comment instance to update
            comment_instance = Comments.objects.get(id=id)
            
            # Update fields if provided
            if comment:
                comment_instance.comment = comment
            
            # Save the updated instance
            comment_instance.save()

        except Exception as e:
            print("error",str(e))
            return Response({'detail': 'Error updating comments table'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'detail': 'comment updated successfully'}, status=status.HTTP_201_CREATED)
