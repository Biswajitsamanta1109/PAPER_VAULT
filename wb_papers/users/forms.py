from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# usercreation Form -> Ready made from in django that has fields: username,email,password1, password2 etc.

class SignUpForm(UserCreationForm): # UserCreationForm is a built-in Django form used for user registration,,,It already contains:,,username field,,password1,,password2,,password validation logic
    # Inherit everything from UserCreationForm plus my custom email field
    email = forms.EmailField(required=True, help_text="Use @college.ac.in for Faculty") 
    
    class Meta(UserCreationForm.Meta): # Meta class is used to specify metadata for the form, such as which model it is associated with and which fields to include.
        # model = User  -> This is already written in UserCreationForm,so we didnt have to write any model,data will be saved in User Table by default
        fields = UserCreationForm.Meta.fields + ('email',) # fields = UserCreationForm.Meta.fields + ('email',) -> This line extends the default fields provided by UserCreationForm to include the custom email field we defined above. It ensures that when the form is rendered, it will include all the default fields (username, password1, password2) plus the new email field.