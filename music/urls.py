from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/stats/global/', views.get_global_stats, name='global_stats'),
    path('api/stats/user/', views.get_user_stats, name='user_stats'),
    path('api/session/start/', views.start_listening_session, name='start_session'),
    path('api/session/end/', views.end_listening_session, name='end_session'),
    path('api/songs/', views.get_songs, name='songs'),
    path('api/songs/increment-views/', views.increment_views, name='increment_views'),
    path('api/stats/my/', views.get_my_stats, name='my_stats'),
    path('stats/', views.statistics_dashboard, name='statistics_dashboard'),
    path('playlists/', views.playlist_list, name='playlist_list'),
    path('playlists/create/', views.create_playlist, name='create_playlist'),
    path('playlists/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('playlists/<int:playlist_id>/add/<int:song_id>/', views.add_to_playlist, name='add_to_playlist'),
    path('playlists/<int:playlist_id>/remove/<int:song_id>/', views.remove_from_playlist, name='remove_from_playlist'),
] 