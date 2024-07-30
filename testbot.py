import discord
from discord.ext import commands
import os
from navertts import NaverTTS
from dotenv import load_dotenv
import sys
from function.ymusic import *
import asyncio
import json

# .env 파일 활성화
load_dotenv()
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
VOICE_CHANNEL_ID = os.getenv('VOICE_CHANNEL_ID')
VOICE_TEXTCHANNEL_ID = os.getenv('VOICE_TEXTCHANNEL_ID')
ADMIN_ID = os.getenv('ADMIN_ID')
STAFF_ROLE = "Admin"
QUEUE_FILE = 'music_queue.json'

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
    channel = bot.get_channel(int(VOICE_CHANNEL_ID))
    await channel.connect()
    print(f'Logged in as: {bot.user}')

# 봇 재시작
@bot.command(name='restart')
async def restart(ctx):
    try:
        if any(role.name == str(STAFF_ROLE) for role in ctx.author.roles):
            await ctx.send("봇을 재시작합니다.")

            # 봇을 종료하고 프로세스를 다시 시작
            await bot.close()

            # Python 스크립트를 다시 실행
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            await ctx.send('이 명령어를 사용할 수 있는 권한이 없습니다.')

    except Exception as e:
        await ctx.send(f"재시작 도중 오류가 발생했습니다: {str(e)}")

# ROLE 확인
@bot.command(name='myrole')
async def list_roles(ctx):
    # 사용자의 역할 목록 가져오기
    roles = ctx.author.roles
    role_names = [role.name for role in roles if role.name != "@everyone"]

    if role_names:
        # 역할 이름 출력
        await ctx.send(f"{ctx.author.mention}님의 역할: " + ", ".join(role_names))
    else:
        await ctx.send(f"{ctx.author.mention}님은 특별한 역할이 없습니다.")

# 인사
@bot.command(name='hello')
async def hello(ctx):
    await ctx.channel.send('생존확인')

# 메세지 삭제
@bot.command(name='clean')
async def clean(ctx):
    await ctx.channel.purge(limit=int(100))

# 보이스채널 입장 (봇 실행시 자동입장)
@bot.command(name='voicein')
async def voicein(ctx):
    if str(ctx.channel.id) == str(VOICE_TEXTCHANNEL_ID):    
        channel = bot.get_channel(int(VOICE_CHANNEL_ID))
        await channel.connect()

# 보이스채널 퇴장
@bot.command(name='voiceout')
async def voiceout(ctx):
    if str(ctx.channel.id) == str(VOICE_TEXTCHANNEL_ID): 
        channel = bot.voice_clients[0]
        await ctx.channel.purge(limit=99)
        await channel.disconnect()

# Naver tts 출력 (음악재생시 동시 이용불가)
@bot.command(name='tts')
async def on_message(ctx, *, text:str):
    if str(ctx.channel.id) == str(VOICE_TEXTCHANNEL_ID):
        voice = bot.voice_clients[0]
        tts = NaverTTS(text, speed=0)
        tts.save('tts.mp3')
        await voice.play(discord.FFmpegPCMAudio('tts.mp3'))

# 현재 재생 중인 노래 정보를 저장할 변수
current_song = None

async def save_queue_to_file(queue):
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=4)

async def load_queue_from_file():
    try:
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            queue = json.load(f)
    except FileNotFoundError:
        queue = []
    return queue

async def add_song_to_queue(song):
    queue = await load_queue_from_file()
    queue.append(song)
    await save_queue_to_file(queue)

async def get_next_song():
    queue = await load_queue_from_file()
    if queue:
        next_song = queue.pop(0)
        await save_queue_to_file(queue)
        return next_song
    return None

def get_queue_list():
    queue = asyncio.run(load_queue_from_file())
    if not queue:
        return "재생 목록이 비어 있습니다."

    queue_text = [f"{idx + 1}. {song['title']}" for idx, song in enumerate(queue)]
    return "\n".join(queue_text)

async def play_next_song(ctx):
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
    ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(ctx), bot.loop) if e is None else print(f'오류 발생: {e}'))

    embed = discord.Embed(title=f'{title}', description=f'{original_url}', color=0x00ff56)
    await ctx.send(embed=embed)


@bot.command(name='ymusic')
async def play(ctx, *, url):
    try:
        # YouTube URL에서 오디오 스트리밍 소스 가져오기
        audio_url, title, duration, original_url = get_youtube_audio_source(url)

        if audio_url is None:
            await ctx.send("오류가 발생했습니다. 유효한 YouTube URL을 입력하세요.")
            return

        # 큐에 추가
        await add_song_to_queue({'audio_url': audio_url, 'title': title, 'duration': duration, 'original_url': original_url})

        # 현재 재생 중인 음악이 없으면 재생 시작
        if current_song is None or not ctx.voice_client.is_playing():
            await play_next_song(ctx)
        else:
            await ctx.send(f"{title}이(가) 대기열에 추가되었습니다.")

    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {str(e)}")

@bot.command(name='stop')
async def stop(ctx):
    try:
        # 음성 채널에 연결되어 있는지 확인
        if ctx.voice_client is not None:
            # 오디오 재생 중지
            ctx.voice_client.stop()
            global current_song
            current_song = None  # 현재 재생 중인 노래를 None으로 설정

            await ctx.send("현재 재생 중인 음악을 중지합니다.")
        else:
            await ctx.send("봇이 음성 채널에 연결되어 있지 않습니다.")
    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {str(e)}")

@bot.command(name='Que')
async def Que(ctx):
    queue_content = get_queue_list()
    embed = discord.Embed(title='재생목록', description=queue_content, color=0x00ff56)
    await ctx.send(embed=embed)

# 봇 작동
bot.run(TOKEN)