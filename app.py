from flask import Flask, request, render_template, redirect, url_for
from youtube_transcript_api import YouTubeTranscriptApi
import re
import requests

app = Flask(__name__)

# Replace with your actual YouTube Data API key
YOUTUBE_API_KEY = 'YOUR_YOUTUBE_API_KEY'

def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^\&\?\/]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^\&\?\/]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^\&\?\/]+)",
        r"(?:https?:\/\/)?youtu\.be\/([^\&\?\/]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([^\&\?\/]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_title(video_id):
    """
    Retrieves the video title using YouTube Data API.
    """
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}'
    response = requests.get(url)
    data = response.json()
    if response.status_code != 200:
        print(f"Error fetching video title: {response.status_code} - {response.text}")
        return "Unknown Title"

    if 'items' in data and len(data['items']) > 0:
        return data['items'][0]['snippet']['title']
    else:
        print(f"Error: No items found in response for video ID {video_id}")
        return "Unknown Title"

def get_youtube_transcript(video_url):
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en', 'hi', 'es'])  # Priority order of languages
        captions = ""
        for entry in transcript.fetch():
            captions += entry['text'] + '\n\n'
        
        title = get_video_title(video_id)
        return title, captions
    except Exception as e:
        return "Error", f"Error for {video_url}: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_urls = request.form.get('video_urls').splitlines()
        transcripts = []
        for video_url in video_urls:
            title, captions = get_youtube_transcript(video_url)
            transcripts.append((title, captions))

        return render_template('index.html', transcripts=transcripts, processed=True)

    return render_template('index.html', processed=False)

if __name__ == "__main__":
    app.run(debug=True)
