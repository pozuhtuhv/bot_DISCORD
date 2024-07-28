import yt_dlp
import re

# Function to get the YouTube audio source from URL or search query
def get_youtube_audio_source(query):
    # Regular expression to check if input is a URL
    url_pattern = re.compile(r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$')
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',  # Default search option for non-URL inputs
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            if not url_pattern.match(query):
                # If query is not a URL, treat it as a search term
                query = f"ytsearch:{query}"
            info = ydl.extract_info(query, download=False)

            # info 데이터 확인
            # a = open("test.txt",'w', encoding="utf-8")
            # a.write(str(info))
            # a.close()
            
            # If it's a search result, get the first entry
            if 'entries' in info:
                info = info['entries'][0]
                
            return info['url'], info['title'], info['duration'], info['original_url']
        
        except Exception as e:
            print(f"Error extracting info: {e}")
            return None, None, None
    
def create_progress_bar(elapsed, duration, bar_length=30):
    """재생바 생성 함수"""
    progress = elapsed / duration
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    elapsed_time = format_time(elapsed)
    total_time = format_time(duration)
    return f"|{bar}| {elapsed_time} / {total_time}"

def format_time(seconds):
    """초를 MM:SS 형식으로 변환"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"