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

@bot.command(name='command')
async def command(ctx):
    embed = discord.Embed(title='Command List', 
                          description='''
                            !restart - Admin / 봇 재시작\n
                            !myrole - Everyone / 역할 출력\n
                            !hello - Everyone / 작동확인\n
                            !clean - Everyone / 채팅창청소\n
                            !voicein - Everyone / 보이스채널입장\n
                            !voiceout - Everyone / 보이스채널퇴장\n
                            !tts - Everyone / 네이버 TTS\n
                            !ymusic - Everyone / 유튜브 Audio 재생 (검색어 or 주소)''', color=0x00ff56)
    await ctx.send(embed=embed)

# 봇 재시작
@bot.command(name='restart')
async def restart(ctx):
    try:
        if any(role.name == str(STAFF_ROLE) for role in ctx.author.roles):
            await ctx.send("봇 재시작")

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
        await ctx.send(f"{ctx.author.mention}님은 역할이 없습니다.")

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

# ymusic
# 현재 재생 중인 노래 정보를 저장할 변수
@bot.command(name='ymusic')
async def ymusic(ctx, *, url):
    """유튜브 음악을 재생"""
    await play(ctx, bot, url, VOICE_CHANNEL_ID)

@bot.command(name='stop')
async def stop_command(ctx):
    """음악 재생을 중지"""
    await stop(ctx)

@bot.command(name='Que')
async def que_command(ctx):
    """재생 목록을 표시"""
    await show_queue(ctx)

# 봇 작동
bot.run(TOKEN)