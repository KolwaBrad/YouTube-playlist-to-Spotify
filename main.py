import os
import re
import webbrowser
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

def get_authenticated_youtube_service():
    """Authenticate with YouTube API and return service object."""
    # Set up YouTube API credentials
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"  # You need to download this from Google Developer Console
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    
    # Check if credentials file exists
    if not Path(client_secrets_file).exists():
        print(f"\n⚠️ Error: {client_secrets_file} not found.")
        print("Please download the client secret file from Google Developer Console:")
        print("1. Go to https://console.developers.google.com/")
        print("2. Create a project or select an existing one")
        print("3. Enable the YouTube Data API v3")
        print("4. Create OAuth credentials (OAuth client ID, Web application)")
        print("5. Download the credentials and save as 'client_secret.json' in this directory")
        raise FileNotFoundError(f"{client_secrets_file} not found")
    
    print("\n🔑 Starting YouTube authentication process...")
    print("A browser window will open. Please sign in and grant permission.")
    
    # Get credentials and create an API client
    try:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        # Automatically open the browser for better user experience
        flow.run_local_server(port=8080, prompt='consent', open_browser=True)
        credentials = flow.credentials
        
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)
        
        print("✅ YouTube authentication successful!")
        return youtube
    except Exception as e:
        print(f"\n⚠️ Authentication error: {str(e)}")
        print("If a browser window didn't open automatically, please manually copy and paste")
        print("the URL that appears in your terminal into a web browser.")
        raise

def get_authenticated_spotify_client():
    """Authenticate with Spotify API and return client object."""
    # Set up Spotify API credentials
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    redirect_uri = "http://localhost:8888/callback"
    
    # Check if environment variables are set
    if not client_id or not client_secret:
        print("\n⚠️ Error: Spotify API credentials not found in environment variables.")
        print("Please set the following environment variables:")
        print("  export SPOTIFY_CLIENT_ID='your_client_id'")
        print("  export SPOTIFY_CLIENT_SECRET='your_client_secret'")
        print("\nYou can get these credentials from the Spotify Developer Dashboard:")
        print("1. Go to https://developer.spotify.com/dashboard/")
        print("2. Create a new app")
        print("3. Set the redirect URI to 'http://localhost:8888/callback'")
        print("4. Copy the Client ID and Client Secret")
        raise ValueError("Spotify API credentials not found")
    
    print("\n🔑 Starting Spotify authentication process...")
    print("A browser window will open. Please sign in and grant permission.")
    
    # Create Spotify client
    try:
        cache_path = ".spotify_cache"
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="playlist-modify-public playlist-modify-private",
            cache_path=cache_path,
            open_browser=True
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Test the connection
        user = sp.current_user()
        print(f"✅ Spotify authentication successful! Logged in as: {user['display_name']}")
        return sp
    except Exception as e:
        print(f"\n⚠️ Spotify authentication error: {str(e)}")
        print("If a browser window didn't open automatically, please manually copy and paste")
        print("the URL that appears in your terminal into a web browser.")
        raise

def extract_playlist_id(youtube_playlist_url):
    """Extract playlist ID from YouTube playlist URL."""
    # Regular expression to match playlist ID in various URL formats
    playlist_id_match = re.search(r"(?:list=)([a-zA-Z0-9_-]+)", youtube_playlist_url)
    
    if playlist_id_match:
        return playlist_id_match.group(1)
    else:
        raise ValueError("Could not extract playlist ID from the provided URL.")

def get_songs_from_youtube_playlist(youtube, playlist_id):
    """Retrieve songs from a YouTube playlist."""
    songs = []
    
    # Get the playlist title
    playlist_response = youtube.playlists().list(
        part="snippet",
        id=playlist_id
    ).execute()
    
    if not playlist_response["items"]:
        raise ValueError("Playlist not found or is private.")
    
    playlist_title = playlist_response["items"][0]["snippet"]["title"]
    
    # Get playlist items
    next_page_token = None
    total_videos = 0
    
    print("\n📋 Fetching playlist contents...")
    
    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        batch_size = len(response["items"])
        total_videos += batch_size
        print(f"  Processing {batch_size} videos (total: {total_videos})...")
        
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            # Clean up the title to better match song formats
            # Remove common patterns in YouTube music videos
            cleaned_title = video_title
            # Remove text like "Official Video", "Lyrics", etc.
            patterns = [
                r"\(Official Video\)", r"\(Official Music Video\)",
                r"\(Lyrics\)", r"\(Lyric Video\)", r"\[Official Video\]",
                r"\[Official Music Video\]", r"\[Lyrics\]", r"\[Lyric Video\]",
                r"Official Video", r"Official Music Video", r"Lyric Video",
                r"Video Oficial", r"Audio Oficial", r"HD", r"HQ",
                r"\d{4} New", r"ft\.", r"feat\.", r"Ft\.", r"Feat\."
            ]
            for pattern in patterns:
                cleaned_title = re.sub(pattern, "", cleaned_title, flags=re.IGNORECASE)
            
            # Remove anything in brackets or parentheses
            cleaned_title = re.sub(r"\[.*?\]|\(.*?\)", "", cleaned_title)
            
            # Remove extra whitespace
            cleaned_title = re.sub(r"\s+", " ", cleaned_title).strip()
            
            if cleaned_title:  # Only add if there's something left after cleaning
                songs.append(cleaned_title)
        
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    
    return songs, playlist_title

def search_spotify_for_songs(sp, songs):
    """Search for songs on Spotify and return their URIs."""
    song_uris = []
    not_found = []
    
    print(f"\n🔍 Searching for {len(songs)} songs on Spotify...")
    
    for i, song in enumerate(songs, 1):
        result = sp.search(q=song, type="track", limit=1)
        if result["tracks"]["items"]:
            track = result["tracks"]["items"][0]
            artist_name = track['artists'][0]['name']
            track_name = track['name']
            print(f"  ✅ [{i}/{len(songs)}] Found: {track_name} by {artist_name}")
            song_uris.append(track["uri"])
        else:
            print(f"  ❌ [{i}/{len(songs)}] Not found: {song}")
            not_found.append(song)
    
    return song_uris, not_found

def create_spotify_playlist(sp, playlist_name, song_uris):
    """Create a Spotify playlist and add songs to it."""
    # Get user ID
    user_id = sp.current_user()["id"]
    
    # Create playlist
    print(f"\n📝 Creating Spotify playlist: '{playlist_name} (YouTube Import)'...")
    
    playlist = sp.user_playlist_create(
        user=user_id,
        name=f"{playlist_name} (YouTube Import)",
        public=False,
        description="Imported from YouTube playlist"
    )
    
    # Add songs to playlist (in batches of 100 as per Spotify API limits)
    total_songs = len(song_uris)
    for i in range(0, total_songs, 100):
        batch = song_uris[i:i+100]
        batch_end = min(i+100, total_songs)
        print(f"  Adding songs {i+1}-{batch_end} to playlist...")
        sp.playlist_add_items(
            playlist_id=playlist["id"],
            items=batch
        )
    
    return playlist["external_urls"]["spotify"]

def main():
    print("\n🎵 YouTube to Spotify Playlist Converter 🎵")
    print("==========================================")
    
    try:
        # Get YouTube playlist URL
        youtube_playlist_url = input("\n📺 Enter the YouTube playlist URL: ")
        
        # Set up APIs
        youtube = get_authenticated_youtube_service()
        sp = get_authenticated_spotify_client()
        
        # Extract playlist ID
        playlist_id = extract_playlist_id(youtube_playlist_url)
        
        # Get songs from YouTube playlist
        songs, playlist_title = get_songs_from_youtube_playlist(youtube, playlist_id)
        print(f"✅ Found {len(songs)} videos in the playlist.")
        
        # Search for songs on Spotify
        song_uris, not_found = search_spotify_for_songs(sp, songs)
        
        if not song_uris:
            print("\n⚠️ No songs could be found on Spotify. Exiting.")
            return
        
        # Create Spotify playlist
        playlist_url = create_spotify_playlist(sp, playlist_title, song_uris)
        
        print("\n🎉 Success! Your Spotify playlist has been created.")
        print(f"🔗 Playlist URL: {playlist_url}")
        
        if not_found:
            print(f"\n⚠️ {len(not_found)} songs could not be found on Spotify:")
            for song in not_found[:10]:  # Show first 10
                print(f"  - {song}")
            
            if len(not_found) > 10:
                print(f"  ... and {len(not_found) - 10} more")
    
    except Exception as e:
        print(f"\n⚠️ An error occurred: {str(e)}")
        print("Please check the error message above and try again.")

if __name__ == "__main__":
    main()