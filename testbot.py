import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
# .env 파일 활성화
load_dotenv()
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Define intents
intents = discord.Intents.default()
# intents.guild_voice_states = True  # 음성 상태 변경 인텐트 활성화
# Initialize bot with intents
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user}')

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('안녕하세요')

# 따라하기
@bot.command(name='!') # !!
async def hello(ctx, text:str=None):
    await ctx.send(text)

# 봇 작동
bot.run(TOKEN)