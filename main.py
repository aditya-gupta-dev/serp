import dotenv
import os
import yt_dlp
from googleapiclient.discovery import build 
import re 

def youtube_search(query, max_results=5, api_key="YOUR_API_KEY"):
    youtube = build("youtube", "v3", developerKey=api_key)

    search_response = youtube.search().list(
        q=query, part="id", type="video", maxResults=max_results
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response["items"]]

    video_response = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=",".join(video_ids)
    ).execute()

    results = []
    for item in video_response["items"]:
        duration_iso = item["contentDetails"]["duration"]
        # Convert ISO 8601 duration to human-readable format
        match = re.match(r"PT((?P<h>\d+)H)?((?P<m>\d+)M)?((?P<s>\d+)S)?", duration_iso)
        hours = int(match.group("h") or 0)
        minutes = int(match.group("m") or 0)
        seconds = int(match.group("s") or 0)
        duration = f"{hours:02}:{minutes:02}:{seconds:02}"

        data = {
            "video_name": item["snippet"]["title"],
            "video_id": item["id"],
            "duration": duration,
            "views": int(item["statistics"]["viewCount"])
        }
        results.append(data)


    return results

def download_mp3(video_url: str, output_path: str):
    try: 
        ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0', 
        }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return None 
    except Exception as e: 
        return e


API_KEY, OUTPUT_DIR = None, None 

dotenv.load_dotenv()

API_KEY = os.getenv('API_KEY')
OUTPUT_DIR = os.getenv('OUTPUT_DIR')

print('Serp - Music downloader')

try: 
    query = input('Enter your music name :')
    results = youtube_search(query, api_key=API_KEY)
    
    for i, video in enumerate(results, 1):
        print(f"{i}. {video['video_name']} ({video['video_id']})")
        print(f"   Duration: {video['duration']}")
        print(f"   Views: {video['views']:,}")
        print("-" * 40)
    
    selection = int(input('\n\tEnter your selection :'))

    if selection > len(results):
        print('out of range of results')
        exit(1) 

    result = download_mp3(video_url=f"https://www.youtube.com/watch?v={results[selection - 1]['video_id']}", output_path=OUTPUT_DIR)
    if result is None: 
        print(f'Saved at :{OUTPUT_DIR}')
    else:
        print(f"error: {result}") 

except Exception as e:
    print(f'Error Occured : {e}')