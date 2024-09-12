from django.db import models


class DentalMesh(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='')

