from django.db import models

class College(models.Model):
    UNIVERSITY_CHOICES = [
        ('MAKAUT', 'MAKAUT (formerly WBUT)'),
        ('JU', 'Jadavpur University'),
        ('CU', 'Calcutta University'),
        ('AUTONOMOUS', 'Autonomous Institution'),
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    university = models.CharField(max_length=20, choices=UNIVERSITY_CHOICES)
    logo = models.ImageField(upload_to='college_logos/', blank=True) # Optional field for college logo, can be used in the frontend for better UI,upload to media/college_logos/

    def __str__(self):
        return self.name

class Stream(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='streams') # Each stream is associated with a college, if a college is deleted, its streams will also be deleted,related_name='streams' allows us to access all streams of a college using college.streams.all(),College can have multiple streams, but a stream belongs to only one college,College is the parent entity and Stream is the child entity in this relationship.,College is primaary key and Stream has a foreign key to College, which creates a one-to-many relationship between College and Stream.,models.foreignkey is used to create a foreign key relationship between Stream and College, which allows us to link each stream to a specific college.
    name = models.CharField(max_length=100) # e.g. CSE, IT, ECE, ME, CE # Stream name, max length 100 characters

    def __str__(self):
        return f"{self.name} - {self.college.name}"