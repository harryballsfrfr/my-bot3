import os
import discord
from discord.ext import commands
from aiohttp import web
import asyncio
import datetime
from collections import defaultdict

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=',', intents=intents)

# -----------------
# Message tracking for stats
# -----------------
message_log = defaultdict(list)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Track messages for stats
    message_log[message.author.id].append(datetime.datetime.utcnow())

    # Keep only messages from last 7 days
    week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    message_log[message.author.id] = [t for t in message_log[message.author.id] if t >= week_ago]

    await bot.process_commands(message)

# -----------------
# Ready Event
# -----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# -----------------
# Server Info Command
# -----------------
@bot.command()
async def si(ctx):
    owner = ctx.guild.owner
    embed = discord.Embed(
        title=f"Server Info - {ctx.guild.name}",
        description=f"👑 Owner: {owner.mention}\n🧑 Members: {ctx.guild.member_count}",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Server Info")
    await ctx.send(embed=embed)

# -----------------
# Stats Command
# -----------------
@bot.command()
async def stats(ctx):
    now = datetime.datetime.utcnow()
    today = now - datetime.timedelta(days=1)
    last3d = now - datetime.timedelta(days=3)
    last7d = now - datetime.timedelta(days=7)

    embed = discord.Embed(
        title=f"📊 Message Stats - {ctx.guild.name}",
        color=discord.Color.green()
    )

    for member in ctx.guild.members:
        if member.bot:
            continue
        msgs = message_log.get(member.id, [])
        count_today = sum(1 for t in msgs if t >= today)
        count_3d = sum(1 for t in msgs if t >= last3d)
        count_7d = sum(1 for t in msgs if t >= last7d)
        if count_today + count_3d + count_7d > 0:
            embed.add_field(
                name=member.display_name,
                value=f"Today: {count_today}\n3d: {count_3d}\nWeek: {count_7d}",
                inline=True
            )

    await ctx.send(embed=embed)

# -----------------
# Moderation Commands
# -----------------
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, seconds: int):
    try:
        await member.timeout(duration=discord.utils.timedelta(seconds=seconds))
        await ctx.send(f"⏱️ {member.mention} has been timed out for {seconds} seconds.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.mention} has been kicked.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    try:
        await member.ban(reason=reason)
        await ctx.send(f"⛔ {member.mention} has been banned.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")

# -----------------
# Keep-alive Web Server
# -----------------
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

# === Procfile ===
worker: python bot.py
