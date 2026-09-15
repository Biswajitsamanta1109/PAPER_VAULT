import datetime
from django import forms
from .models import Paper
from django.core.validators import FileExtensionValidator
from colleges.models import Stream


class PaperUploadForm(forms.ModelForm): # This form is used for uploading papers. It includes fields for title, college, stream, subject name, subject code, exam type, year, semester, and the PDF file itself. The form also includes validation to ensure that only PDF files can be uploaded and that all required fields are filled out correctly.
    EXAM_CHOICES = [ # Dropdown choices for exam type field. The first option is a placeholder prompting the user to select an exam type, followed by specific options for internal/CA, semester, and practical exams.
        ('', '--- Select Exam Type ---'),
        ('INTERNAL', 'Internal / CA'),
        ('SEMESTER', 'Semester (End-Sem)'),
        ('PRACTICAL', 'Practical Exam'),
    ]

    stream = forms.ModelChoiceField( # This field allows users to select a stream from the Stream model. It uses a dropdown menu populated with all available streams in the database. The label for each option is set to the name of the stream, and there is a placeholder prompting users to select a stream.
        queryset=Stream.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select shadow-none border-primary-subtle', 
            'required': 'true',
            'id': 'uploadStreamSelect'
        }),
        empty_label="--- Select Stream ---"
    )

    def __init__(self, *args, **kwargs): # 
        super().__init__(*args, **kwargs) #super method is called to initialize the form with any provided arguments and keyword arguments. This allows for customization of the form fields after the default initialization.
        self.fields['stream'].label_from_instance = lambda obj: f"{obj.name}" # This lambda function sets the label for each stream option in the dropdown to be the name of the stream. For example, if there is a stream with the name "Computer Science & Engineering", it will appear as that in the dropdown menu instead of something like "Stream object (1)". This makes the form more user-friendly and easier to navigate when selecting a stream.
        current_year = datetime.date.today().year # Get the current year using the datetime module. This is used to populate the year dropdown with options from the current year down to 2015.
        self.fields['year'].choices = [('', '--- Select Year ---')] + [(r, r) for r in range(current_year, 2014, -1)]  # This line sets the choices for the year field in the form. It creates a list of tuples where each tuple contains a year value and its corresponding label. The choices start with a placeholder option prompting users to select a year, followed by options for each year from the current year down to 2015. For example, if the current year is 2024, the choices will include options for 2024, 2023, 2022, and so on down to 2015.

    SEM_CHOICES = [('', '--- Select Semester ---')] + [(i, f"Semester {i}") for i in range(1, 9)] # This line defines the choices for the semester field in the form. It creates a list of tuples where each tuple contains a semester number and its corresponding label. The choices start with a placeholder option prompting users to select a semester, followed by options for semesters 1 through 8. For example, the options will include "Semester 1", "Semester 2", and so on up to "Semester 8". This allows users to easily select the appropriate semester when uploading a paper.

    exam_type = forms.ChoiceField( # This field allows users to select the type of exam from a predefined set of choices. The choices are defined in the EXAM_CHOICES list, which includes options for internal/CA exams, semester exams, and practical exams. The field uses a dropdown menu for selection and includes attributes to style the dropdown and make it a required field.
        choices=EXAM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select shadow-none border-primary-subtle', 'required': 'true'})
    )
    semester = forms.ChoiceField(
        choices=SEM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select shadow-none border-primary-subtle', 'required': 'true'})
    )
    year = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select shadow-none border-primary-subtle', 'required': 'true'})
    )
    pdf_file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])], # Ensures only PDF files can be uploaded.
        widget=forms.FileInput(attrs={'class': 'form-control', 'required': 'true', 'accept': '.pdf'})
    )

    class Meta:
        model = Paper
        fields = ['title', 'college', 'stream', 'subject_name', 'subject_code', 'exam_type', 'year', 'semester', 'pdf_file']
        widgets = { # This section defines custom widgets for each form field to enhance the appearance and user experience of the form. For example, the title field uses a TextInput widget with specific CSS classes and a placeholder, while the college and stream fields use Select widgets with styling and placeholders. The subject name and code fields also use TextInput widgets with appropriate styling and placeholders. The PDF file field uses a FileInput widget that restricts uploads to PDF files and includes styling.
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Data Structures & Algorithm', 'required': 'true'}),
            'college': forms.Select(attrs={'class': 'form-select shadow-none border-primary-subtle', 'required': 'true', 'id': 'uploadCollegeSelect'}),
            'subject_name': forms.TextInput(attrs={'class': 'form-control shadow-none', 'placeholder': 'Enter Subject Name', 'required': 'true'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-control shadow-none', 'placeholder': 'e.g. CS-401', 'required': 'true'}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-control', 'required': 'true'}),
        }