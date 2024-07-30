import discord
import asyncio
import yt_dlp
import re
import json

# JSON 파일 경로
QUEUE_FILE = 'music_queue.json'

# 현재 재생 중인 노래 정보를 저장할 변수
current_song = None

# 큐 관리 함수들
async def save_queue_to_file(queue):
    """큐를 JSON 파일에 저장합니다."""
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=4)

async def load_queue_from_file():
    """JSON 파일에서 큐를 불러옵니다."""
    try:
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            queue = json.load(f)
    except FileNotFoundError:
        queue = []
    return queue

async def add_song_to_queue(song):
    """노래를 큐에 추가하고 JSON 파일에 저장합니다."""
    queue = await load_queue_from_file()
    queue.append(song)
    await save_queue_to_file(queue)

async def get_next_song():
    """큐에서 다음 노래를 가져오고 JSON 파일에 저장합니다."""
    queue = await load_queue_from_file()
    if queue:
        next_song = queue.pop(0)
        await save_queue_to_file(queue)
        return next_song
    return None

async def get_queue_list():
    queue = await load_queue_from_file()  # await 사용하여 비동기 작업 처리

    queue_text = [f"{idx + 1}. {song['title']}" for idx, song in enumerate(queue)]
    return "\n".join(queue_text)

async def play_next_song(ctx, bot):
    """큐에서 다음 노래를 재생합니다."""
    global current_song
    next_song = await get_next_song()

    audio_url = next_song['audio_url']
    title = next_song['title']
    original_url = next_song['original_url']

    # 오디오 소스 생성
    source = discord.FFmpegPCMAudio(
        audio_url,
        before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        options='-vn -bufsize 64M'
    )

    # 현재 재생 중인 노래 설정
    current_song = next_song

    # 오디오 재생
    ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(ctx, bot), bot.loop) if e is None else print(f'오류 발생: {e}'))

    embed = discord.Embed(title=f'{title}', description=f'{original_url}', color=0x00ff56)
    await ctx.send(embed=embed)

# 명령어 함수들
async def play(ctx, bot, url, voice_channel_id):
    """노래를 재생합니다."""
    global current_song
    try:
        channel = bot.get_channel(int(voice_channel_id))

        # 음성 클라이언트 생성 및 음성 채널로 이동
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)

        # YouTube URL에서 오디오 스트리밍 소스 가져오기
        audio_url, title, duration, original_url = get_youtube_audio_source(url)

        if audio_url is None:
            await ctx.send("오류가 발생했습니다. 유효한 YouTube URL을 입력하세요.")
            return

        # 큐에 추가
        await add_song_to_queue({'audio_url': audio_url, 'title': title, 'duration': duration, 'original_url': original_url})

        # 현재 재생 중인 음악이 없으면 재생 시작
        if current_song is None or not ctx.voice_client.is_playing():
            await play_next_song(ctx, bot)
        else:
            await ctx.send(f"{title}이(가) 대기열에 추가되었습니다.")

    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {str(e)}")

async def stop(ctx):
    """현재 재생 중인 음악을 중지합니다."""
    global current_song
    try:
        # 음성 채널에 연결되어 있는지 확인
        if ctx.voice_client is not None:
            # 오디오 재생 중지
            ctx.voice_client.stop()
            current_song = None  # 현재 재생 중인 노래를 None으로 설정

            await ctx.send("현재 재생 중인 음악을 중지합니다.")
        else:
            await ctx.send("봇이 음성 채널에 연결되어 있지 않습니다.")
    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {str(e)}")

async def show_queue(ctx):
    """현재 재생 목록을 출력합니다."""
    queue_list = await get_queue_list()  # 코루틴 실행 결과를 대기
    embed = discord.Embed(title='재생목록', description=queue_list, color=0x00ff56)
    await ctx.send(embed=embed)

def get_youtube_audio_source(query):
    """YouTube URL이나 검색어로부터 오디오 소스를 가져옵니다."""
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

            # 검색 결과일 경우 첫 번째 항목 선택
            if 'entries' in info:
                info = info['entries'][0]

            # 오디오 URL과 메타데이터 반환
            return info['url'], info['title'], info['duration'], info['webpage_url']

        except Exception as e:
            print(f"오류 발생: {str(e)}")
            return None, None, None, None