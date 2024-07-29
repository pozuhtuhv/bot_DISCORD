import discord
from discord.ext import commands
import os
from navertts import NaverTTS
from dotenv import load_dotenv
import sys
from function.ymusic import *

# .env 파일 활성화
load_dotenv()
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
VOICE_CHANNEL_ID = os.getenv('VOICE_CHANNEL_ID')
VOICE_TEXTCHANNEL_ID = os.getenv('VOICE_TEXTCHANNEL_ID')
ADMIN_ID = os.getenv('ADMIN_ID')
STAFF_ROLE = "Admin"

# Youtube Stream 
current_video_url = None # 비디오 영상 주소

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

# Naver tts 출력
@bot.command(name='tts')
async def on_message(ctx, *, text:str):
    if str(ctx.channel.id) == str(VOICE_TEXTCHANNEL_ID):   
        voice = bot.voice_clients[0]
        tts = NaverTTS(text, speed=0)
        tts.save('tts.mp3')
        voice.play(discord.FFmpegPCMAudio('tts.mp3'))

# 음성 채널에 연결하여 YouTube 음악 재생
@bot.command(name='ymusic')
async def play(ctx, url):
    try:
        channel = bot.get_channel(int(VOICE_CHANNEL_ID))

        # 음성 클라이언트 생성 및 음성 채널로 이동
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)

        # YouTube URL에서 오디오 스트리밍 소스 가져오기
        audio_url, title, duration, original_url = get_youtube_audio_source(url)

        source = discord.FFmpegPCMAudio(
            audio_url,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            options='-vn -bufsize 64M'
        )

        # 오디오 재생
        ctx.voice_client.play(source, after=lambda e: print(f'오류 발생: {e}') if e else None)

        embed = discord.Embed(title=f'{title}', description=f'{original_url}', color=0x00ff56)
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {str(e)}")

# 재생 중지 명령어
@bot.command(name='stop')
async def stop(ctx):
    try:
        # 음성 채널에 연결되어 있는지 확인
        if ctx.voice_client is not None:

            # 오디오 재생 중지
            ctx.voice_client.stop()

            await ctx.send("현재 재생 중인 음악을 중지합니다.")
        else:
            await ctx.send("봇이 음성 채널에 연결되어 있지 않습니다.")
    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {str(e)}")

# 봇 작동
bot.run(TOKEN)