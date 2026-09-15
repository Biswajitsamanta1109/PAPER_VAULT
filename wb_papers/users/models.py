from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model): # This model extends the built-in User model to include additional fields specific to our application's needs, such as role, college affiliation, and verification status.
    ROLE_CHOICES = [('STUDENT', 'Student'), ('FACULTY', 'Faculty')] #Defines dropdown choices for role field.
    user = models.OneToOneField(User, on_delete=models.CASCADE) #  OneToOneField -> Each user can have:,, on_delete -> only ONE profile,, If user is deleted: profile also gets deleted automatically,on
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT') 
    college = models.ForeignKey('colleges.College', on_delete=models.SET_NULL, null=True) # ForeignKey -> Many profiles can be associated with one college,, on_delete -> if college is deleted: set college field to null in profile instead of deleting profile itself.set null=True allows the college field to be empty if the college is deleted.
    is_verified = models.BooleanField(default=False) # Used for Faculty ID verification.

    def __str__(self):
        return f"{self.user.username} ({self.role})"