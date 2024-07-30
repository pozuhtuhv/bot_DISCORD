import yt_dlp
import re

def get_youtube_audio_source(query):
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
        'default_search': 'ytsearch',  # URL이 아닐 경우 검색어로 간주
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            if not url_pattern.match(query):
                # 입력이 URL이 아닐 경우 검색어로 처리
                query = f"ytsearch:{query}"
            info = ydl.extract_info(query, download=False)

            # 검색 결과일 경우 첫 번째 항목 가져오기
            if 'entries' in info:
                info = info['entries'][0]

            return info['url'], info['title'], info['duration'], info.get('webpage_url', '')
        
        except Exception as e:
            print(f"정보 추출 중 오류 발생: {e}")
            return None, None, None, None