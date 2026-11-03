from django.contrib import admin
from .models import Paper 

@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ('subject_name', 'college', 'stream', 'year', 'exam_type') # list_display is a tuple that defines the fields of the Paper model that will be displayed in the list view of the Django admin interface. In this case, it includes subject_name, college, stream, year, and exam_type.
    list_filter = ('college', 'stream', 'exam_type', 'year') # list_filter is a tuple that defines the fields of the Paper model that will be available as filters in the Django admin interface. This allows admin users to filter the list of papers based on college, stream, exam_type, and year, making it easier to find specific records.
    search_fields = ('subject_name', 'title') # search_fields is a tuple that defines the fields of the Paper model that will be searchable in the Django admin interface. Admin users can use the search bar to find papers based on their subject_name or title, allowing for quick access to specific records.