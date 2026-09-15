from django.db import models
from django.contrib.auth.models import User

class Paper(models.Model):
    EXAM_TYPES = [
        ('INTERNAL', 'Internal / CA'),
        ('SEMESTER', 'Semester (End-Sem)'),
        ('PRACTICAL', 'Practical Exam'),
    ]
    
    title = models.CharField(max_length=200)
    
    college = models.ForeignKey('colleges.College', on_delete=models.CASCADE) # on_delete -> if college is deleted: delete all papers associated with that college as well.
    stream = models.ForeignKey('colleges.Stream', on_delete=models.CASCADE) # COLLEGE and STREAM are ForeignKey fields that create a relationship between the Paper model and the College and Stream models in the colleges app. This allows each paper to be associated with a specific college and stream, enabling better organization and filtering of papers based on these attributes. For example, if a paper is uploaded for "Kolkata University" under the "Computer Science & Engineering" stream, it will be linked to those specific college and stream records in the database.
    
    semester = models.IntegerField(choices=[(i, f"Semester {i}") for i in range(1, 9)])
    year = models.IntegerField()
    subject_name = models.CharField(max_length=150)
    subject_code = models.CharField(max_length=20)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES) 
    pdf_file = models.FileField(upload_to='papers/%Y/%m/') # upload_to -> files will be uploaded to MEDIA_ROOT/papers/<year>/<month>/filename.pdf, this helps in organizing files by upload date and prevents too many files in a single directory.
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True) # AUTO_NOW_ADD -> automatically set the field to now when the object is first created. This means that when a new paper is uploaded, the uploaded_at field will be automatically populated with the current date and time, providing a timestamp for when the paper was added to the system.

    def __str__(self):
        return f"{self.subject_name} ({self.year})"