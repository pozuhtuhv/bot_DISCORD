import discord
from discord.ext import commands
import os
from navertts import NaverTTS
from dotenv import load_dotenv

# .env 파일 활성화
load_dotenv()
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
VOICE_CHANNEL_ID = os.getenv('VOICE_CHANNEL_ID')
VOICE_TEXTCHANNEL_ID = os.getenv('VOICE_TEXTCHANNEL_ID')

# Define intents
intents = discord.Intents.default()
intents.message_content = True
# Initialize bot with intents
# 명령어 시작부분
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# 연결확인
@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user}')

# 인사
@bot.command(name='hello')
async def hello(ctx):
    await ctx.channel.send('생존확인')

# 메세지 삭제
@bot.command(name='clean')
async def clean(ctx, ea:int):
    await ctx.channel.purge(limit=ea)
    await ctx.channel.send(str(ea) +'개의 메시지를 삭제했습니다.')

# 보이스채널 입장
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