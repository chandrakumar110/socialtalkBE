from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    mobile_number = models.BigIntegerField(unique=True,default=0,null=False)
    email = models.EmailField(unique=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.user_type
    
class Posts(models.Model):
    caption = models.CharField(max_length=2555)
    image = models.ImageField(upload_to='post_images/')
    created_date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    username = models.CharField(max_length=255)

    class Meta:
        db_table = 'posts'  #s Specify the custom table name here

    def __str__(self):
        return f"Post {self.id}"
    
class Comments(models.Model):
    comment = models.CharField(max_length=2555)
    username = models.CharField(max_length=255)
    like_status = models.BooleanField(default=False)
    post = models.ForeignKey(Posts, related_name='comments', on_delete=models.CASCADE,default=1)

    class Meta:
        db_table = 'comments'

    def __str__(self):
        return f"Comment {self.id}"
    
class Hashtags(models.Model):
    hashtag = models.CharField(max_length=255)
    post = models.ForeignKey(Posts, related_name='hashtags', on_delete=models.CASCADE,default=1)

    class Meta:
        db_table = 'hashtags'

    def __str__(self):
        return f"Hashtag {self.id}"
    
class PostLikes(models.Model):
    post = models.ForeignKey(Posts, related_name='post_likes', on_delete=models.CASCADE,default=1)
    username= models.CharField(max_length=255,default=None)

    class Meta:
        db_table = 'post_likes'
    
    def __str__(self):
        return f"Like {self.id}" 