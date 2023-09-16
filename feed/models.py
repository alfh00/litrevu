from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from PIL import Image

from authentication.models import User

# Create your models here.


class Photo(models.Model):
    file = models.ImageField()
    caption = models.CharField(max_length=128, blank=True)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    IMAGE_SIZE = (800, 800)

    def resize_image(self):
        image = Image.open(self.file)
        image.thumbnail(self.IMAGE_SIZE)
        image.save(self.file.path)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.resize_image()


class Ticket(models.Model):
    title = models.CharField(max_length=128)
    image = models.ForeignKey(Photo, on_delete=models.CASCADE)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket Title: {self.title}, User: {self.user.username}, Time Created: {self.time_created}"


class Review(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Ticket: {self.ticket.title}, User: {self.user.username}, Rating: {self.rating}, Time Created: {self.time_created}"
