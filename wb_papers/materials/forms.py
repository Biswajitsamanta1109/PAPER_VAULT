import datetime
from django import forms
from .models import Material
from django.core.validators import FileExtensionValidator
from colleges.models import Stream


class MaterialUploadForm(forms.ModelForm):

    MATERIAL_TYPE_CHOICES = [
        ('', '--- Select Type ---'),
        ('NOTES', 'Notes'),
        ('ASSIGNMENT', 'Assignment / Teacher Suggestion'),
        ('LAB_MANUAL', 'Lab Manual'),
        ('PLACEMENT', 'Placement Notes'),
    ]
 
    SEM_CHOICES = [('', '--- Select Semester ---')] + [(i, f"Semester {i}") for i in range(1, 9)]

    material_type = forms.ChoiceField(
        choices=MATERIAL_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select shadow-none border-primary-subtle',
            'id': 'materialTypeSelect'
        })
    )

    stream = forms.ModelChoiceField(
        queryset=Stream.objects.all(),
        required=True,
        widget=forms.Select(attrs={ # forms.Select widget is used to render a dropdown select field in HTML. The attrs parameter allows you to specify additional HTML attributes for the select element, such as CSS classes and IDs.
            'class': 'form-select shadow-none border-primary-subtle',
            'id': 'uploadStreamSelect'
        }),
        empty_label="--- Select Stream ---"
    )

    semester = forms.ChoiceField(
        choices=SEM_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select shadow-none border-primary-subtle'}) # widget is used to customize the HTML representation of the form field. In this case, it specifies that the semester field should be rendered as a dropdown select element with specific CSS classes for styling.
    )

    pdf_file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])], #allowed_extensions=['pdf'] ensures that only files with a .pdf extension can be uploaded. If a user tries to upload a file with a different extension, the form will raise a validation error.
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}) #file input field in HTML. The accept attribute restricts the file types that can be selected to only PDF files, enhancing user experience by preventing the selection of unsupported file types.
    )

    def __init__(self, *args, **kwargs): # this method is using to customize the initialization of the form. It allows you to modify the form fields, set labels, and add additional attributes to the form fields when the form is created.
        super().__init__(*args, **kwargs)
        self.fields['stream'].label_from_instance = lambda obj: f"{obj.name}"
        self.fields['college'].required = True
        self.fields['college'].widget.attrs.update({
            'class': 'form-select shadow-none border-primary-subtle',
            'id': 'uploadCollegeSelect'
        })

    def clean(self): # this method is using to perform custom validation on the form data. It checks if the college and stream fields are filled out. If either field is empty, it adds an error message to that field, prompting the user to select a value. This ensures that the form cannot be submitted without selecting both a college and a stream.
        cleaned_data = super().clean() #cleaned_data is a dictionary that contains the validated data from the form fields after they have been cleaned and processed. It is used to access the values of the form fields for further validation or processing.
        college = cleaned_data.get('college')
        stream = cleaned_data.get('stream')
        if not college:
            self.add_error('college', 'Please select a college.')
        if not stream:
            self.add_error('stream', 'Please select a stream.')
        return cleaned_data

    class Meta: #class Meta is a nested class within the MaterialUploadForm that provides metadata about the form. It specifies which model the form is associated with (Material) and which fields from that model should be included in the form. Additionally, it defines custom widgets for certain fields to control their appearance and behavior in the rendered HTML form.
        model = Material
        fields = ['title', 'material_type', 'college', 'stream', 'subject_name', 'semester', 'description', 'pdf_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Data Structures Notes Unit 1-3'}),
            'subject_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Data Structures & Algorithm'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional: briefly describe what this covers...'}),
        }