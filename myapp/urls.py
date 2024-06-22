
from django.urls import path
from .views.auth_views import LoginView,SignupView
from .views.create_post_views import CreatePostView
from .views.comment_post_views import CommentPostView
from .views.search_user_views import SearchUserView
from .views.posts_views import PostView
from .views.users_views import UsersView
from .views.delete_post_views import DeletePostView
from .views.delete_comment_views import DeleteCommentView
from .views.search_hashtag_views import SearchHashtagView
from .views.search_caption_views import SearchCaptionView
from .views.delete_user_views import DeleteUserView
from .views.update_user_views import UpdateUserView
from .views.update_post_views import UpdatePostView
from .views.update_comment_views import UpdateCommentView
from .views.like_post_views import LikePostView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('allusers/',UsersView.as_view(), name='allusers'),
    path('createpost/',CreatePostView.as_view(), name='createpost'),
    path('commentpost/',CommentPostView.as_view(), name='commentpost'),
    path('searchuser/',SearchUserView.as_view(), name='searchuser'),
    path('allposts/',PostView.as_view(), name='allposts'),
    path('deletepost/',DeletePostView.as_view(), name='deletepost'),
    path('deletecomment/',DeleteCommentView.as_view(), name='deletecomment'),
    path('searchhashtag/',SearchHashtagView.as_view(), name='searchhashtag'),
    path('searchcaption/', SearchCaptionView.as_view(), name='searchcaption'),
    path('deleteuser/',DeleteUserView.as_view(),name='deleteuser'),
    path('updateuser/',UpdateUserView.as_view(), name='updateuser'),
    path('updatepost/',UpdatePostView.as_view(),name='updatepost'),
    path('updatecomment/',UpdateCommentView.as_view(),name='updatecomment'),
    path('likepost/',LikePostView.as_view(), name='likepost')

]
