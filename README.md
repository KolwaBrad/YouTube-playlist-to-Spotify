# YouTube to Spotify Playlist Converter

A Python tool that automatically transfers songs from a YouTube playlist to Spotify. It extracts tracks from any public YouTube playlist and creates a matching Spotify playlist.

## Features

- 🎵 Extracts songs from any public YouTube playlist
- 🔍 Smart song title parsing and matching
- 🎯 Intelligent search algorithm to find the best matches on Spotify
- 🔐 Secure authentication with both YouTube and Spotify APIs
- 💫 User-friendly interface with clear progress indicators

## Prerequisites

Before using this tool, you'll need:

1. Python 3.7 or higher
2. Google Developer account (for YouTube API access)
3. Spotify Developer account (for Spotify API access)
4. The following Python packages:
   - google-auth-oauthlib
   - google-api-python-client
   - spotipy

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/KolwaBrad/youtube-to-spotify.git
   cd youtube-to-spotify
   ```

2. Install the required Python packages:
   ```
   pip install google-auth-oauthlib google-api-python-client spotipy
   ```

3. Set up the YouTube Data API:
   - Go to the [Google Developer Console](https://console.developers.google.com/)
   - Create a new project
   - Enable the YouTube Data API v3
   - Create OAuth credentials (OAuth client ID, Web application type)
   - Add `http://localhost:8080/` as an authorized redirect URI
   - Download the credentials as `client_secret.json` and place it in the project directory

4. Set up the Spotify API:
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Create a new app
   - Set the redirect URI to `http://localhost:8888/callback`
   - Note your Client ID and Client Secret
   - Set them as environment variables:
     ```
     # On Windows
     set SPOTIFY_CLIENT_ID=your_client_id
     set SPOTIFY_CLIENT_SECRET=your_client_secret
     
     # On macOS/Linux
     export SPOTIFY_CLIENT_ID=your_client_id
     export SPOTIFY_CLIENT_SECRET=your_client_secret
     ```

## Usage

1. Run the script:
   ```
   python youtube_to_spotify.py
   ```

2. Enter the YouTube playlist URL when prompted

3. The script will:
   - Open browser windows for authentication with both services
   - Fetch all videos from the YouTube playlist
   - Clean up video titles to identify songs
   - Search for each song on Spotify
   - Create a new Spotify playlist with the found songs
   - Provide a summary of successfully transferred songs

## How It Works

1. **Authentication**: The tool uses OAuth to securely connect to both the YouTube Data API and Spotify API.

2. **Playlist Analysis**: It fetches the YouTube playlist and extracts video titles.

3. **Title Processing**: The tool cleans up titles by:
   - Attempting to extract artist and title information
   - Removing common phrases like "Official Video", "Lyrics", etc.
   - Eliminating text in parentheses and brackets

4. **Spotify Matching**: For each processed title, the tool:
   - Searches Spotify for the best matching track
   - Calculates a similarity score between the YouTube title and Spotify result
   - Adds the track to the playlist, with warnings for low-confidence matches

5. **Playlist Creation**: Finally, it creates a new Spotify playlist with all the matched songs.

## Troubleshooting

### Common Issues:

1. **Redirect URI Mismatch**: Make sure the redirect URIs in your code match exactly what you've configured in the Google/Spotify developer consoles.

2. **Authentication Errors**: Ensure you've enabled the correct APIs and that your credentials are properly set up.

3. **Rate Limiting**: Both YouTube and Spotify APIs have rate limits. For large playlists, you might need to implement pauses between requests.

4. **Missing Songs**: Some songs on YouTube might not be available on Spotify. The script will list these in the final report.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [Spotipy](https://github.com/spotipy-dev/spotipy)