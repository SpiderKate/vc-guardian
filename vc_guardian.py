import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import json
import os
from pathlib import Path


def load_env_file(path=None):
    env_path = Path(path or os.path.join(os.path.dirname(__file__), ".env"))
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()

TOKEN = os.environ.get("DISCORD_TOKEN")

VOICE_CHANNEL_ID = 1018135692926271488
TEXT_CHANNEL_ID = 1018135692926271488

# optional: track a specific person
EMERGENCY_PING = os.environ.get("EMERGENCY_PING")  # your ID or leave as None

STATE_FILE = "state.json"

# ---------------- STATE ----------------

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "streak_start": None,
            "longest_streak": 0,
            "last_count": 0,
            "warned_2": False,
            "warned_1": False
        }

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


state = load_state()


# ---------------- HELPERS ----------------

def get_real_members(channel):
    return [m for m in channel.members if not m.bot]


def format_duration(seconds):
    seconds = int(seconds)
    days = seconds // 86400
    seconds %= 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    parts = []
    if days: parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")

    return " ".join(parts)


def update_longest_streak():
    if state["streak_start"] is None:
        return

    start = datetime.fromisoformat(state["streak_start"])
    duration = (datetime.now() - start).total_seconds()

    if duration > state["longest_streak"]:
        state["longest_streak"] = int(duration)


# ---------------- BOT ----------------

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_voice_state_update(member, before, after):
    global state

    if member.bot:
        return

    channel = bot.get_channel(VOICE_CHANNEL_ID)
    text_channel = bot.get_channel(TEXT_CHANNEL_ID)

    if not channel or not text_channel:
        return

    members = get_real_members(channel)
    count = len(members)

    # start streak
    if count > 0 and not state["streak_start"]:
        state["streak_start"] = datetime.now().isoformat()
        state["warned_1"] = False
        state["warned_2"] = False

    # reset warnings
    if count > 2:
        state["warned_1"] = False
        state["warned_2"] = False

    # warnings
    if count == 2 and not state["warned_2"]:
        state["warned_2"] = True
        await text_channel.send("⚠ Only 2 people remain in VC!")

    elif count == 1 and not state["warned_1"]:
        state["warned_1"] = True
        await text_channel.send(f"⚠⚠ Only 1 person remains in VC! \n{EMERGENCY_PING}")

    # VC empty
    elif count == 0:
        await text_channel.send("VC has ended...")

        update_longest_streak()

        state["streak_start"] = None
        state["warned_1"] = False
        state["warned_2"] = False

    state["last_count"] = count
    save_state()


# ---------------- COMMANDS ----------------

async def _send_message(send_func, message, *, ephemeral=False):
    if ephemeral:
        await send_func(message, ephemeral=True)
    else:
        await send_func(message)


async def _show_vc_status(send_func, *, ephemeral=False):
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        return await _send_message(send_func, "VC not found.", ephemeral=ephemeral)

    members = get_real_members(channel)
    names = "\n".join(m.display_name for m in members)
    await _send_message(
        send_func,
        f"VC STATUS\nMembers: {len(members)}\n\n{names or 'Empty'}",
        ephemeral=ephemeral,
    )


async def _show_streak(send_func, *, ephemeral=False):
    update_longest_streak()
    save_state()
    if not state["streak_start"]:
        return await _send_message(send_func, "No active streak.", ephemeral=ephemeral)

    start = datetime.fromisoformat(state["streak_start"])
    duration = (datetime.now() - start).total_seconds()
    await _send_message(send_func, f"Current streak: {format_duration(duration)}", ephemeral=ephemeral)


async def _show_longest(send_func, *, ephemeral=False):
    await _send_message(send_func, f"Longest streak: {format_duration(state['longest_streak'])}", ephemeral=ephemeral)


async def _show_stats(send_func, *, ephemeral=False):
    update_longest_streak()
    save_state()
    if state["streak_start"]:
        start = datetime.fromisoformat(state["streak_start"])
        current = format_duration((datetime.now() - start).total_seconds())
    else:
        current = "None"

    await _send_message(
        send_func,
        f"VC STATS\nCurrent streak: {current}\nLongest streak: {format_duration(state['longest_streak'])}",
        ephemeral=ephemeral,
    )


@tree.command(name="vc", description="Show current VC members")
async def vc(interaction: discord.Interaction):
    await _show_vc_status(interaction.response.send_message, ephemeral=True)


@bot.command(name="vc")
async def vc_prefix(ctx):
    await _show_vc_status(ctx.send)


@tree.command(name="streak", description="Show current streak")
async def streak(interaction: discord.Interaction):
    await _show_streak(interaction.response.send_message, ephemeral=True)


@bot.command(name="streak")
async def streak_prefix(ctx):
    await _show_streak(ctx.send)


@tree.command(name="longest", description="Show longest streak")
async def longest(interaction: discord.Interaction):
    await _show_longest(interaction.response.send_message, ephemeral=True)


@bot.command(name="longest")
async def longest_prefix(ctx):
    await _show_longest(ctx.send)


@tree.command(name="stats", description="Full VC stats")
async def stats(interaction: discord.Interaction):
    await _show_stats(interaction.response.send_message, ephemeral=True)


@bot.command(name="stats")
async def stats_prefix(ctx):
    await _show_stats(ctx.send)

# ---------------- SYNC ----------------

@bot.event
async def on_ready():
    try:
        await tree.sync()
    except Exception as e:
        print(f"Slash command sync failed: {e}")
    print(f"Logged in as {bot.user}")

# ---------------- RUN ----------------

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set. Add it to .env or your environment.")
    bot.run(TOKEN)