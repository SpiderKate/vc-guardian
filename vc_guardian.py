import discord
from discord.ext import commands, app_commands
from datetime import datetime
import json
import os

TOKEN =

VOICE_CHANNEL_ID = 1018135692926271488
TEXT_CHANNEL_ID = 1018135692926271488

# optional: track a specific person
EMERGENCY_PING = "<@648240446367072266> <@1518752483458023487>"  # your ID or leave as None

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

@tree.command(name="vc", description="Show current VC members")
async def vc(interaction: discord.Interaction):
    channel = bot.get_channel(VOICE_CHANNEL_ID)
   
    if not channel:
        return await interaction.response.send_message("VC not found.", ephemeral=True)
    else: 
        members = get_real_members(channel)
    names = "\n".join(m.display_name for m in members)

    await interaction.response.send_message(
        f"VC STATUS\nMembers: {len(members)}\n\n{names or 'Empty'}",
        ephemeral=True
    )


@tree.command(name="streak", description="Show current streak")
async def streak(interaction: discord.Interaction):
    update_longest_streak()
    save_state()
    if not state["streak_start"]:
        return await interaction.response.send_message(
            "No active streak.",
            ephemeral=True
        )

    start = datetime.fromisoformat(state["streak_start"])
    duration = (datetime.now() - start).total_seconds()

    await interaction.response.send_message(
        f"Current streak: {format_duration(duration)}",
        ephemeral=True
    )


@tree.command(name="longest", description="Show longest streak")
async def longest(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Longest streak: {format_duration(state['longest_streak'])}",
        ephemeral=True
    )


@tree.command(name="stats", description="Full VC stats")
async def stats(interaction: discord.Interaction):
    update_longest_streak()
    save_state()
    if state["streak_start"]:
        start = datetime.fromisoformat(state["streak_start"])
        current = format_duration((datetime.now() - start).total_seconds())
    else:
        current = "None"

    await interaction.response.send_message(
        f"VC STATS\n"
        f"Current streak: {current}\n"
        f"Longest streak: {format_duration(state['longest_streak'])}",
        ephemeral=True
    )

# ---------------- SYNC ----------------

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")

# ---------------- RUN ----------------

bot.run(TOKEN)