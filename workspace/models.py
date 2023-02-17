from django.db import models

# Create your models here.
class VoiceTrack(models.Model):
    name = models.CharField(max_length=255)
    track_file = models.FileField(upload_to='voices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BackgroundTrack(models.Model):
    name = models.CharField(max_length=255)
    track_file = models.FileField(upload_to='backgrounds')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ResultTrack(models.Model):
    name = models.CharField(max_length=255)
    track_file = models.FileField(upload_to='results')
    voice_track = models.ForeignKey(VoiceTrack, null=True, on_delete=models.SET_NULL)
    background_track = models.ForeignKey(BackgroundTrack, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
