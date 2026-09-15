from django.db import models
from django.contrib.auth.models import User
from colleges.models import College, Stream


class Material(models.Model):
    MATERIAL_TYPES = [
        ('NOTES', 'Notes'),
        ('ASSIGNMENT', 'Assignment / Teacher Suggestion'),
        ('LAB_MANUAL', 'Lab Manual'),
        ('PLACEMENT', 'Placement Notes'),
    ]

    title = models.CharField(max_length=200)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='NOTES')
    # FIX: college and stream are optional for placement notes, as Placement Notes are Universal
    college = models.ForeignKey(College, on_delete=models.CASCADE) #foreign key to College model, to associate each material with a specific college. This allows us to filter materials by college and ensures that materials are organized according to the colleges they belong to. ,on_delete=models.CASCADE means that if a college is deleted, all associated materials will also be deleted, which helps maintain data integrity. 
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE) #foreign key to Stream model, to associate each material with a specific stream. This allows us to filter materials by stream and ensures that materials are organized according to the streams they belong to. ,on_delete=models.CASCADE means that if a stream is deleted, all associated materials will also be deleted, which helps maintain data integrity.
    subject_name = models.CharField(max_length=200)
    semester = models.IntegerField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='materials/%Y/%m/') 
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE) #foreign key to User model, to track which user uploaded each material. This allows us to associate materials with their uploaders and can be useful for features like displaying the uploader's name or implementing user-specific permissions. ,on_delete=models.CASCADE means that if a user is deleted, all materials they uploaded will also be deleted, which helps maintain data integrity.
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.subject_name}"

    class Meta:
        ordering = ['-uploaded_at'] #orders materials by upload date in descending order, so that the most recently uploaded materials appear first when queried.g