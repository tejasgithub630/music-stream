from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ListeningSession, UserStatistics, GlobalStatistics, Song, Playlist, PlaylistSong
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
import json

def home(request):
    # Get search query
    search_query = request.GET.get('q', '')
    language_filter = request.GET.get('language', '')
    
    # Base queryset
    songs = Song.objects.all()
    
    # Apply search filter if query exists
    if search_query:
        songs = songs.filter(
            Q(title__icontains=search_query) |
            Q(artist__icontains=search_query) |
            Q(album__icontains=search_query)
        )
    
    # Apply language filter if specified
    if language_filter:
        songs = songs.filter(language=language_filter)
    
    # Get popular songs by views
    popular_songs = Song.objects.order_by('-views')[:10]
    
    # Get songs by language
    songs_by_language = {}
    for lang_code, lang_name in Song.LANGUAGE_CHOICES:
        songs_by_language[lang_name] = Song.objects.filter(language=lang_code).order_by('-views')[:5]
    
    # Get user's playlists if authenticated, otherwise empty list
    playlists = Playlist.objects.filter(user=request.user) if request.user.is_authenticated else []
    
    global_stats = GlobalStatistics.get_or_create_stats()
    context = {
        'songs': songs.order_by('-uploaded_at'),
        'popular_songs': popular_songs,
        'songs_by_language': songs_by_language,
        'languages': Song.LANGUAGE_CHOICES,
        'total_users': global_stats.total_users,
        'total_listening_time': global_stats.total_listening_time,
        'total_sessions': global_stats.total_sessions,
        'last_updated': global_stats.last_updated,
        'search_query': search_query,
        'selected_language': language_filter,
        'playlists': playlists,  # Add playlists to context
    }
    return render(request, 'music/home.html', context)

@api_view(['GET'])
def get_songs(request):
    search_query = request.GET.get('q', '')
    language = request.GET.get('language', '')
    
    songs = Song.objects.all()
    
    if search_query:
        songs = songs.filter(
            Q(title__icontains=search_query) |
            Q(artist__icontains=search_query) |
            Q(album__icontains=search_query)
        )
    
    if language:
        songs = songs.filter(language=language)
    
    song_list = [{
        'id': song.id,
        'title': song.title,
        'artist': song.artist,
        'album': song.album,
        'audio_url': song.audio_file.url,
        'cover_url': song.cover_image.url if song.cover_image else None,
        'duration': str(song.duration) if song.duration else None,
        'language': dict(Song.LANGUAGE_CHOICES)[song.language],
        'views': song.views
    } for song in songs]
    return Response(song_list)

@api_view(['GET'])
def get_global_stats(request):
    stats = GlobalStatistics.get_or_create_stats()
    return Response({
        'total_users': stats.total_users,
        'total_listening_time': str(stats.total_listening_time),
        'total_sessions': stats.total_sessions,
        'last_updated': stats.last_updated
    })

@api_view(['GET'])
@login_required
def get_user_stats(request):
    user_stats, created = UserStatistics.objects.get_or_create(user=request.user)
    return Response({
        'username': request.user.username,
        'total_listening_time': str(user_stats.total_listening_time),
        'total_sessions': user_stats.total_sessions,
        'last_active': user_stats.last_active
    })

@api_view(['GET'])
def get_my_stats(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=401)
    user_stats, created = UserStatistics.objects.get_or_create(user=request.user)
    return Response({
        'username': request.user.username,
        'total_listening_time': str(user_stats.total_listening_time),
        'total_sessions': user_stats.total_sessions,
        'last_active': user_stats.last_active
    })

@api_view(['POST'])
def start_listening_session(request):
    user = request.user if request.user.is_authenticated else None
    song_id = request.data.get('song_id')
    try:
        song = Song.objects.get(id=song_id) if song_id else None
        session = ListeningSession.objects.create(user=user, song=song)
        return Response({'session_id': session.id})
    except Song.DoesNotExist:
        return Response({'error': 'Song not found'}, status=404)

@api_view(['POST'])
def end_listening_session(request):
    session_id = request.data.get('session_id')
    try:
        session = ListeningSession.objects.get(id=session_id)
        session.end_session()
        # Update user statistics if user is set
        if session.user:
            user_stats, created = UserStatistics.objects.get_or_create(user=session.user)
            user_stats.update_statistics(session.duration)
        # Update global statistics
        global_stats = GlobalStatistics.get_or_create_stats()
        global_stats.total_listening_time += session.duration
        global_stats.total_sessions += 1
        global_stats.save()
        return Response({'status': 'success'})
    except ListeningSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=404)

def statistics_dashboard(request):
    global_stats = GlobalStatistics.get_or_create_stats()
    context = {
        'total_users': global_stats.total_users,
        'total_listening_time': global_stats.total_listening_time,
        'total_sessions': global_stats.total_sessions,
        'last_updated': global_stats.last_updated
    }
    return render(request, 'music/statistics.html', context)

@api_view(['POST'])
@login_required
def increment_views(request):
    song_id = request.data.get('song_id')
    try:
        song = Song.objects.get(id=song_id)
        song.views += 1
        song.save()
        return Response({'status': 'success', 'views': song.views})
    except Song.DoesNotExist:
        return Response({'error': 'Song not found'}, status=404)

@login_required
def playlist_list(request):
    if not request.user.is_authenticated:
        return render(request, 'music/login_required.html')
    playlists = Playlist.objects.filter(user=request.user)
    context = {
        'playlists': playlists
    }
    return render(request, 'music/playlist_list.html', context)

@login_required
def playlist_detail(request, playlist_id):
    try:
        playlist = Playlist.objects.get(id=playlist_id, user=request.user)
        songs = playlist.songs.all().order_by('playlistsong__order')
        
        # Create JSON data for songs
        songs_json = json.dumps([{
            'id': str(song.id),
            'audio_url': song.audio_file.url,
            'title': song.title,
            'artist': song.artist,
            'cover_url': song.cover_image.url if song.cover_image else None
        } for song in songs])
        
        context = {
            'playlist': playlist,
            'songs': songs,
            'songs_json': songs_json
        }
        return render(request, 'music/playlist_detail.html', context)
    except Playlist.DoesNotExist:
        return redirect('playlist_list')

@login_required
def create_playlist(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        cover_image = request.FILES.get('cover_image')
        
        playlist = Playlist.objects.create(
            name=name,
            description=description,
            user=request.user,
            cover_image=cover_image
        )
        return redirect('playlist_detail', playlist_id=playlist.id)
    
    return render(request, 'music/create_playlist.html')

@login_required
def add_to_playlist(request, playlist_id, song_id):
    try:
        playlist = Playlist.objects.get(id=playlist_id, user=request.user)
        song = Song.objects.get(id=song_id)
        
        # Get the highest order number
        highest_order = PlaylistSong.objects.filter(playlist=playlist).order_by('-order').first()
        new_order = (highest_order.order + 1) if highest_order else 0
        
        PlaylistSong.objects.create(
            playlist=playlist,
            song=song,
            order=new_order
        )
        return JsonResponse({'status': 'success'})
    except (Playlist.DoesNotExist, Song.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Playlist or song not found'}, status=404)

@login_required
def remove_from_playlist(request, playlist_id, song_id):
    try:
        playlist = Playlist.objects.get(id=playlist_id, user=request.user)
        song = Song.objects.get(id=song_id)
        
        PlaylistSong.objects.filter(playlist=playlist, song=song).delete()
        return JsonResponse({'status': 'success'})
    except (Playlist.DoesNotExist, Song.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Playlist or song not found'}, status=404)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'music/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'music/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('home')

@login_required
def account_view(request):
    if not request.user.is_authenticated:
        return render(request, 'music/login_required.html')
    user_stats, _ = UserStatistics.objects.get_or_create(user=request.user)
    return render(request, 'music/account.html', {
        'user': request.user,
        'user_stats': user_stats
    })
