import discord
from discord.ext import commands, tasks
import os
from navertts import NaverTTS
from dotenv import load_dotenv
import time
import sys
from function import ymusic

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
    channel = bot.get_channel(int(VOICE_CHANNEL_ID))
    await channel.connect()
    print(f'Logged in as: {bot.user}')

# 봇 재시작
@bot.command(name='restart')
async def restart(ctx):
    """봇을 재시작합니다."""
    try:
        await ctx.send("봇을 재시작합니다...")

        # 봇을 종료하고 프로세스를 다시 시작
        await bot.close()

        # Python 스크립트를 다시 실행
        os.execl(sys.executable, sys.executable, *sys.argv)

    except Exception as e:
        await ctx.send(f"재시작 도중 오류가 발생했습니다: {str(e)}")

# test
progress_message = None  # 이전 메시지를 저장
start_time = None  # 노래 시작 시점
current_task = None # 진행중인 노래
current_video_url = None # 비디오 영상 주소

# 음성 채널에 연결하여 YouTube 음악 재생
@bot.command(name='ymusic')
async def play(ctx, url):
    global start_time
    try:
        channel = bot.get_channel(int(VOICE_CHANNEL_ID))

        # 음성 클라이언트 생성 및 음성 채널로 이동
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)

        # YouTube URL에서 오디오 스트리밍 소스 가져오기
        audio_url, title, duration, original_url = ymusic.get_youtube_audio_source(url)

        # source = discord.FFmpegPCMAudio(audio_url, options='-vn -bufsize 64M -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')

        source = discord.FFmpegPCMAudio(
            audio_url,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            options='-vn -bufsize 64M'
        )

        # 오디오 재생
        start_time = time.time()
        ctx.voice_client.play(source, after=lambda e: print(f'오류 발생: {e}') if e else None)

        await ctx.send(f'<{original_url}> :notes: 재생중')

        # 재생바 업데이트를 위한 루프 시작
        # 이전 메시지 초기화
        progress_message = None
        start_time = time.time()  # 시작 시간 갱신
        update_progress_bar.start(ctx, title, duration)

    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {str(e)}")

@tasks.loop(seconds=2)
async def update_progress_bar(ctx, title, duration):
    """2초마다 재생바 업데이트"""
    global progress_message, start_time
    if ctx.voice_client and ctx.voice_client.is_playing():
        elapsed = time.time() - start_time  # 경과 시간 계산
        progress_bar = ymusic.create_progress_bar(elapsed, duration)
        
        # 이전 메시지 업데이트
        if progress_message is None:
            progress_message = await ctx.send(f"{progress_bar} - `{title}`")
        else:
            await progress_message.edit(content=f"{progress_bar} - `{title}`")

# 재생 중지 명령어
@bot.command(name='stop')
async def stop(ctx):
    global current_task
    
    try:
        # 음성 채널에 연결되어 있는지 확인
        if ctx.voice_client is not None:
            # 현재 진행 중인 Task가 있는 경우 취소
            if current_task is not None and not current_task.done():
                current_task.cancel()
                await ctx.send("현재 재생 중인 음악을 중지하고 음성 채널에서 나갑니다.")

            # 음성 채널 연결 해제
            await ctx.voice_client.disconnect()
            
            # Task를 None으로 초기화
            current_task = None
            await ctx.send("재생을 중지하고 음성 채널에서 나갔습니다.")
        else:
            await ctx.send("봇이 음성 채널에 연결되어 있지 않습니다.")
    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {str(e)}")

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