import discord
from discord.ext import commands, tasks
import os
from navertts import NaverTTS
from dotenv import load_dotenv
import yt_dlp
import time

# .env 파일 활성화
load_dotenv()
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
VOICE_CHANNEL_ID = os.getenv('VOICE_CHANNEL_ID')
VOICE_TEXTCHANNEL_ID = os.getenv('VOICE_TEXTCHANNEL_ID')

# Define intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
# Initialize bot with intents

# 명령어 시작부분
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# 연결확인
@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user}')
    channel = bot.get_channel(int(VOICE_CHANNEL_ID))
    await channel.connect()

# test

progress_message = None  # 이전 메시지를 저장
start_time = None  # 노래 시작 시점

# YouTube URL에서 오디오 스트리밍
def get_youtube_audio_source(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        return info['url'], info['title'], info['duration']

# 음성 채널에 연결하여 YouTube 음악 재생
@bot.command(name='ymusic')
async def play(ctx, url):
    global start_time
    try:
        # 사용자가 음성 채널에 접속해 있는지 확인
        if ctx.author.voice is None:
            await ctx.send("먼저 음성 채널에 접속해주세요.")
            return

        # 음성 채널 가져오기
        channel = ctx.author.voice.channel

        # 음성 클라이언트 생성 및 음성 채널로 이동
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)

        # YouTube URL에서 오디오 스트리밍 소스 가져오기
        audio_url, title, duration = get_youtube_audio_source(url)

        # source = discord.FFmpegPCMAudio(audio_url, options='-vn -bufsize 64M -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')

        source = discord.FFmpegPCMAudio(
            audio_url,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            options='-vn -bufsize 64M'
        )

        # 오디오 재생
        start_time = time.time()
        ctx.voice_client.play(source, after=lambda e: print(f'오류 발생: {e}') if e else None)

        # 재생바 업데이트를 위한 루프 시작
        # 이전 메시지 초기화
        progress_message = None
        start_time = time.time()  # 시작 시간 갱신
        update_progress_bar.start(ctx, title, duration)

    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {str(e)}")

@tasks.loop(seconds=3)
async def update_progress_bar(ctx, title, duration):
    """3초마다 재생바 업데이트"""
    global progress_message, start_time
    if ctx.voice_client and ctx.voice_client.is_playing():
        elapsed = time.time() - start_time  # 경과 시간 계산
        progress_bar = create_progress_bar(elapsed, duration)
        
        # 이전 메시지 업데이트
        if progress_message is None:
            progress_message = await ctx.send(f"{progress_bar} - `{title}`")
        else:
            await progress_message.edit(content=f"{progress_bar} - `{title}`")

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

# 재생 중지 명령어
@bot.command(name='stop')
async def stop(ctx):
    try:
        if ctx.voice_client is not None:
            progress_message = None  # 메시지 초기화
            start_time = None  # 시작 시간 초기화
            await ctx.voice_client.disconnect()
            await ctx.send("재생을 중지하고 음성 채널에서 나갔습니다.")
        else:
            await ctx.send("봇이 음성 채널에 연결되어 있지 않습니다.")
    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {str(e)}")

# 볼륨조절
@bot.command(name='volume')
async def volume(ctx, volume: int):
    if ctx.voice_client is None or not ctx.voice_client.is_playing():
        await ctx.send("재생 중인 노래가 없습니다.")
    else:
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"볼륨이 {volume}%로 설정되었습니다.")

# 인사
@bot.command(name='hello')
async def hello(ctx):
    await ctx.channel.send('생존확인')

# 메세지 삭제
@bot.command(name='clean')
async def clean(ctx, ea:int):
    await ctx.channel.purge(limit=ea)
    await ctx.channel.send(str(ea) +'EA Message DELETE')

# # 보이스채널 입장 (봇 실행시 자동입장)
# @bot.command(name='voicein')
# async def voicein(ctx):
#     if str(ctx.channel.id) == str(VOICE_TEXTCHANNEL_ID):    
#         channel = bot.get_channel(int(VOICE_CHANNEL_ID))
#         await channel.connect()

# 보이스채널 퇴장
@bot.command(name='voiceout')
async def voiceout(ctx):
    if str(ctx.channel.id) == str(VOICE_TEXTCHANNEL_ID): 
        channel = bot.voice_clients[0]
        await ctx.channel.purge(limit=99)
        await channel.disconnect()

# tts test
@bot.command(name='tts')
async def on_message(ctx, *, text:str):
    if str(ctx.channel.id) == str(VOICE_TEXTCHANNEL_ID):   
        voice = bot.voice_clients[0]
        tts = NaverTTS(text, speed=0)
        tts.save('tts.mp3')
        voice.play(discord.FFmpegPCMAudio('tts.mp3'))

# 봇 작동
bot.run(TOKEN)