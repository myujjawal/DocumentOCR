from django.db import models

# Create your models here.


class Aadhaar(models.Model):
    aadhaar_number = models.IntegerField()
    name = models.CharField(max_length=100)
    dob = models.DateField()
    address = models.CharField(max_length=300)


class AadhaarImg(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(AadhaarImg, self).save(*args, **kwargs)

        # Img = Scanner(self.ImageFile)
