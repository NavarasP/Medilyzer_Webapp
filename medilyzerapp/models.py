from django.db import models
from django.contrib.auth.models import User

class Prescription(models.Model):
    # name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='Output/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # return self.name
        return f"Prescription for {self.user.first_name} {self.user.last_name}"


class Upload_Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(max_length=255, upload_to="Upload/")

    def __str__(self):
        # return self.name
        return f"Prescription for {self.user.first_name} {self.user.last_name}"

