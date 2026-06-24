# VC Guardian Bot (public-ready skeleton)
# Requires: discord.py>=2.4, python-dotenv

import os, json
from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
STATE_FILE = "state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"guilds": {}}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

state = load_state()

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

def guild_cfg(guild_id):
    gid = str(guild_id)
    if gid not in state["guilds"]:
        state["guilds"][gid] = {
            "voice_channel_id": None,
            "text_channel_id": None,
            "emergency_ping": None,
            "streak_start": None,
            "longest_streak": 0,
            "warned_1": False,
            "warned_2": False
        }
    return state["guilds"][gid]

@tree.command(name="settings", description="Show configuration")
async def settings(interaction: discord.Interaction):
    cfg = guild_cfg(interaction.guild_id)
    await interaction.response.send_message(str(cfg), ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
