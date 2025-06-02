from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import os

# Create your models here.

class Song(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('te', 'Telugu'),
        ('kn', 'Kannada'),
        ('ta', 'Tamil'),
        ('ko', 'others'),
    ]
    
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    album = models.CharField(max_length=200, blank=True)
    audio_file = models.FileField(
        upload_to='songs/',
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav'])],
        help_text='Upload MP3 or WAV files'
    )
    cover_image = models.ImageField(
        upload_to='covers/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text='Upload JPG or PNG files'
    )
    duration = models.DurationField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    popularity = models.IntegerField(default=0)
    views = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.artist}"

    def save(self, *args, **kwargs):
        # Ensure the file is not too large
        if self.audio_file:
            if self.audio_file.size > 50 * 1024 * 1024:  # 50MB in bytes
                raise ValueError('Audio file size must be less than 50MB')
        
        if self.cover_image:
            if self.cover_image.size > 5 * 1024 * 1024:  # 5MB in bytes
                raise ValueError('Cover image size must be less than 5MB')
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Delete the actual files when the song is deleted
        if self.audio_file:
            if os.path.isfile(self.audio_file.path):
                os.remove(self.audio_file.path)
        if self.cover_image:
            if os.path.isfile(self.cover_image.path):
                os.remove(self.cover_image.path)
        super().delete(*args, **kwargs)

class ListeningSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    def end_session(self):
        self.end_time = timezone.now()
        self.duration = self.end_time - self.start_time
        self.save()

class UserStatistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_listening_time = models.DurationField(default=timezone.timedelta())
    last_active = models.DateTimeField(auto_now=True)
    total_sessions = models.IntegerField(default=0)
    
    def update_statistics(self, session_duration):
        self.total_listening_time += session_duration
        self.total_sessions += 1
        self.save()

class GlobalStatistics(models.Model):
    total_users = models.IntegerField(default=0)
    total_listening_time = models.DurationField(default=timezone.timedelta())
    total_sessions = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    @classmethod
    def get_or_create_stats(cls):
        stats, created = cls.objects.get_or_create(pk=1)
        return stats

class Playlist(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song, through='PlaylistSong')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cover_image = models.ImageField(upload_to='playlist_covers/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.song.title} in {self.playlist.name}"
