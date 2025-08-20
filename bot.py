import os
import discord
from discord.ext import commands
from aiohttp import web
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Needed for server info and stats

bot = commands.Bot(command_prefix=',', intents=intents)

# ----------------- Bot Events -----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

# ----------------- Commands -----------------
@bot.command()
async def si(ctx):
    """Server Info: thin embed, pings owner, member count"""
    embed = discord.Embed(title="Server Info", color=0x1abc9c)
    embed.add_field(name="Server Name", value=ctx.guild.name, inline=True)
    embed.add_field(name="Members", value=ctx.guild.member_count, inline=True)
    owner = ctx.guild.owner
    await ctx.send(f"{owner.mention}", embed=embed)

@bot.command()
async def stats(ctx, timeframe="today"):
    """Example stats command; counts messages per user"""
    await ctx.send(f"Stats for {timeframe} are not implemented yet.")

# ----------------- Moderation -----------------
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"✅ Kicked {member.mention}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"✅ Banned {member.mention}")

@bot.command()
@commands.has_permissions(timeout_members=True)
async def timeout(ctx, member: discord.Member, seconds: int):
    await member.timeout(duration=discord.utils.timedelta(seconds=seconds))
    await ctx.send(f"⏱ {member.mention} timed out for {seconds} seconds")

# ----------------- Keep-Alive Web Server -----------------
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
