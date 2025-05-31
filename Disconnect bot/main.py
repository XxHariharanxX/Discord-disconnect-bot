import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import timedelta
from discord.utils import utcnow
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    # Schedule the task daily at midnight UTC (adjust hour, minute as needed)
    scheduler.add_job(timeout_or_disconnect_role_members, "cron", hour=15, minute=10)
    scheduler.start()

async def timeout_or_disconnect_role_members():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("Warning: Guild not found.")
        return

    role = guild.get_role(ROLE_ID)
    if not role:
        print("Warning: Role not found.")
        return

    timeout_until = utcnow() + timedelta(hours=8)

    for member in guild.members:
        if member.bot:
            continue
        if role in member.roles and member.voice and member.voice.channel:
            try:
                await member.timeout(timeout_until, reason="Auto timeout for role at 12 AM UTC")
                print(f"Timed out {member.display_name}")
            except discord.Forbidden:
                # Timeout failed - try disconnect
                try:
                    await member.edit(voice_channel=None, reason="Timeout failed, disconnected instead")
                    print(f"Timeout failed, disconnected {member.display_name} instead")
                except Exception as e:
                    print(f"Failed to disconnect {member.display_name}: {e}")
            except Exception as e:
                print(f"Failed to timeout {member.display_name}: {e}")

bot.run(BOT_TOKEN)
