from django.contrib import admin
from .models import Song, ListeningSession, UserStatistics, GlobalStatistics, Playlist, PlaylistSong
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse

# Custom admin site class
class MusicAdminSite(admin.AdminSite):
    site_header = 'Music Streaming Administration'
    site_title = 'Music Streaming Admin'
    index_title = 'Welcome to Music Streaming Admin'
    index_template = 'admin/index.html'

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        return app_list

    def index(self, request, extra_context=None):
        app_list = self.get_app_list(request)
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'app_list': app_list,
            'total_songs': Song.objects.count(),
            'total_users': UserStatistics.objects.count(),
            'total_playlists': Playlist.objects.count(),
            'total_listening_time': f"{ListeningSession.objects.aggregate(total=Sum('duration'))['total'] or 0} minutes",
            **(extra_context or {}),
        }
        request.current_app = self.name
        return TemplateResponse(request, self.index_template, context)

# Create custom admin site instance
admin_site = MusicAdminSite(name='music_admin')

# Register models with the custom admin site
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'language', 'uploaded_at', 'views', 'display_cover')
    search_fields = ('title', 'artist', 'album')
    list_filter = ('language', 'artist', 'uploaded_at')
    readonly_fields = ('uploaded_at', 'views', 'popularity', 'display_cover')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'artist', 'album', 'language')
        }),
        ('Media Files', {
            'fields': ('audio_file', 'cover_image', 'display_cover'),
            'description': 'Upload MP3/WAV files for audio and JPG/PNG files for cover images'
        }),
        ('Statistics', {
            'fields': ('views', 'popularity', 'uploaded_at'),
            'classes': ('collapse',)
        }),
    )

    def display_cover(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.cover_image.url)
        return "No cover image"
    display_cover.short_description = 'Cover Preview'

class ListeningSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'start_time', 'end_time', 'duration')
    list_filter = ('user', 'start_time')

class UserStatisticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_listening_time', 'total_sessions', 'last_active')
    list_filter = ('user', 'last_active')

class GlobalStatisticsAdmin(admin.ModelAdmin):
    list_display = ('total_users', 'total_listening_time', 'total_sessions', 'last_updated')

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'song_count')
    search_fields = ('name', 'user__username')
    list_filter = ('created_at', 'user')
    
    def song_count(self, obj):
        return obj.songs.count()
    song_count.short_description = 'Number of Songs'

class PlaylistSongAdmin(admin.ModelAdmin):
    list_display = ('playlist', 'song', 'added_at')
    list_filter = ('added_at', 'playlist')
    search_fields = ('playlist__name', 'song__title')

# Register models with our custom admin site
admin_site.register(Song, SongAdmin)
admin_site.register(ListeningSession, ListeningSessionAdmin)
admin_site.register(UserStatistics, UserStatisticsAdmin)
admin_site.register(GlobalStatistics, GlobalStatisticsAdmin)
admin_site.register(Playlist, PlaylistAdmin)
admin_site.register(PlaylistSong, PlaylistSongAdmin)
