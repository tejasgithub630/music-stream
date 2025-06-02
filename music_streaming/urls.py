"""
URL configuration for music_streaming project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from music.views import (
    home,
    get_global_stats,
    get_user_stats,
    start_listening_session,
    end_listening_session,
    statistics_dashboard,
    get_songs,
    increment_views,
    get_my_stats,
    playlist_list,
    playlist_detail,
    create_playlist,
    add_to_playlist,
    remove_from_playlist,
    signup,
    login_view,
    logout_view,
    account_view
)
from music.admin import admin_site

def test_view(request):
    return JsonResponse({"message": "Music Streaming API is working!"})

urlpatterns = [
    path('admin/', admin_site.urls),  # Use our custom admin site
    path('', include('music.urls')),
    path('login/', login_view, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('account/', account_view, name='account'),
    path('api/test/', test_view, name='test'),
    path('api/songs/', get_songs, name='songs'),
    path('api/stats/global/', get_global_stats, name='global_stats'),
    path('api/stats/user/', get_user_stats, name='user_stats'),
    path('api/session/start/', start_listening_session, name='start_session'),
    path('api/session/end/', end_listening_session, name='end_session'),
    path('api/songs/increment-views/', increment_views, name='increment_views'),
    path('api/stats/my/', get_my_stats, name='my_stats'),
    path('stats/', statistics_dashboard, name='statistics_dashboard'),
    path('playlists/', playlist_list, name='playlist_list'),
    path('playlists/create/', create_playlist, name='create_playlist'),
    path('playlists/<int:playlist_id>/', playlist_detail, name='playlist_detail'),
    path('playlists/<int:playlist_id>/add/<int:song_id>/', add_to_playlist, name='add_to_playlist'),
    path('playlists/<int:playlist_id>/remove/<int:song_id>/', remove_from_playlist, name='remove_from_playlist'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
