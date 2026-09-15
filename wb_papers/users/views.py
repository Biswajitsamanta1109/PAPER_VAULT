from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from .models import Profile

def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST) # django form
        if form.is_valid(): #Checks  :empty fields ,password rules ,email format,duplicate username
            user = form.save() #Creates a new user in Django authentication table.
            role = request.POST.get('role', 'STUDENT') #If role is missing:  default value becomes:
            
            # Logic: Students verified by default, Faculty needs Admin check
            is_verified = True if role == 'STUDENT' else False # means : if role is 'STUDENT' then is_verified = True else False,  Needs admin approval

            
            
            Profile.objects.create( # Creates profile record in database.
                user=user,
                role=role,
                is_verified=is_verified
            )
            # means : user registered once will stay logged in : login(request, user)
            login(request, user)  # Logs user into the system immediately after registration.  ,User does NOT need to login again manually.
            return redirect('dashboard')
    else:
        form = SignUpForm() # Used when user first visits registration page.
    return render(request, 'registration.html', {'form': form})

# AI DashBoard Page(Logic is written in 'Papers' app)
def ai_analyzer(request):
    return render(request, 'ai_analyzer.html')