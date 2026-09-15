from django.contrib import admin
from .models import Profile

@admin.register(Profile) # Registers the Profile model with the Django admin site using the custom ProfileAdmin configuration defined below.
class ProfileAdmin(admin.ModelAdmin): # Creates a custom admin panel configuration for the Profile model.
    # This lets you see at a glance who needs help
    list_display = ['user', 'role', 'is_verified'] #  Controls which columns appear in admin table., is_verified is important to quickly see who needs approval.
    list_filter = ['role', 'is_verified'] # Adds filter sidebar in admin panel.
    
    # Simple action to verify faculty in one click
    actions = ['verify_faculty'] # Admin can: ,,select multiple faculty users,,click action,,approve them instantly

    def verify_faculty(self, request, queryset): # Custom admin action to set is_verified=True for selected profiles.
        queryset.update(is_verified=True)
    verify_faculty.short_description = "Approve Selected Faculty Members" # This text appears in the admin action dropdown.