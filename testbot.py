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
# Initialize bot with intents
# 명령어 시작부분
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user}')

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('안녕하세요')

# 봇 작동
bot.run(TOKEN)