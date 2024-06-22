# utils.py

from .models import CustomUser



def insert_sample_users():
     
    # Create a new CustomUser instance
    user = CustomUser.objects.create_user(username='admin' , password='admin123' , email='admin@gmail.com' , user_type='admin',mobile_number=9542266602)
    
    # Save the user to the database
    user.save()