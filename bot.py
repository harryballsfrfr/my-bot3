import os
import discord
from discord.ext import commands
from aiohttp import web
import asyncio

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if 'ybnba' in message.content.lower():
        try:
            await message.add_reaction('✅')
        except discord.errors.Forbidden:
            print("⚠️ Missing permission to add reactions")
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Web server (keep alive)
async def handle(request):
    return web.Response(text="Bot is alive!")

app = web.Application()
app.add_routes([web.get('/', handle)])

async def run():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8000)))
    await site.start()
    await bot.start(os.getenv("TOKEN"))

asyncio.run(run())
