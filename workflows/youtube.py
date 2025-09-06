import os
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import dotenv

dotenv.load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def fetch_youtube_data(search_term, limit=100, region_code=None):
    """
    Searches YouTube for videos in a specific region, with pagination and enriched metadata.
    """
    region_info = f" in region '{region_code}'" if region_code else ""
    print(f"Searching YouTube for '{search_term}'{region_info} (up to {limit} results)...")
    
    if 'YOUR_YOUTUBE_API_KEY_HERE' in API_KEY or not API_KEY:
        print("ERROR: YouTube API key not configured.")
        return []

    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
        all_video_ids = []
        next_page_token = None
        
        while len(all_video_ids) < limit:
            results_per_page = min(50, limit - len(all_video_ids))
            
            search_request = youtube.search().list(
                q=search_term,
                part='snippet',
                type='video',
                order='viewCount',
                maxResults=results_per_page,
                pageToken=next_page_token,
                regionCode=region_code 
            )
            search_response = search_request.execute()

            page_video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            all_video_ids.extend(page_video_ids)
            
            next_page_token = search_response.get('nextPageToken')
            if not next_page_token: break 
            time.sleep(1)

        if not all_video_ids:
            return []
        
        collected_videos = []
        for i in range(0, len(all_video_ids), 50):
            batch_ids = all_video_ids[i:i+50]
            video_response = youtube.videos().list(id=','.join(batch_ids), part='statistics,snippet,contentDetails').execute()

            for item in video_response.get('items', []):
                snippet, stats, content = item.get('snippet', {}), item.get('statistics', {}), item.get('contentDetails', {})
                views, likes, comments = int(stats.get('viewCount', 0)), int(stats.get('likeCount', 0)), int(stats.get('commentCount', 0))
                
                collected_videos.append({
                    "workflow": snippet.get('title', "N/A"), "platform": "YouTube",
                    "link": f"https://www.youtube.com/watch?v={item['id']}",
                    "popularity_metrics": {
                        "views": views, "likes": likes, "comments": comments,
                        "like_to_view_ratio": round(likes / views, 5) if views > 0 else 0,
                        "comment_to_view_ratio": round(comments / views, 5) if views > 0 else 0
                    },

                    "country": region_code or "Global", 
                    "metadata": {
                        "author": snippet.get('channelTitle', 'N/A'), "published_at": snippet.get('publishedAt'),
                        "description": snippet.get('description', ''), "duration": content.get('duration', 'N/A'),
                        "tags": snippet.get('tags', [])
                    }
                })
        return collected_videos

    except HttpError as e:
        print(f"An HTTP error occurred with YouTube: {e.content}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred with YouTube: {e}")
        return []
