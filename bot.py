import discord
import requests
import os
import asyncio
from discord.ext import commands

# Load environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MIDJOURNEY_CHANNEL_ID = int(os.getenv("MIDJOURNEY_CHANNEL_ID"))
APPLICATION_ID = os.getenv("DISCORD_APPLICATION_ID")  # Add MidJourney's App ID

# Set up bot intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    print("Listening for MidJourney prompts...")

# Function to trigger `/imagine` as an API interaction
async def send_midjourney_prompt(prompt):
    channel = bot.get_channel(MIDJOURNEY_CHANNEL_ID)
    if not channel:
        print("❌ Error: MidJourney channel not found!")
        return

    print(f"📩 Sending MidJourney prompt: {prompt}")

    # API URL for Discord interactions
    url = f"https://discord.com/api/v10/interactions"

    # Construct payload for slash command
    payload = {
        "type": 2,  # Type 2 = Application Command
        "application_id": APPLICATION_ID,
        "guild_id": str(channel.guild.id),
        "channel_id": str(channel.id),
        "session_id": "midjourney-bot",  # Arbitrary session ID
        "data": {
            "name": "imagine",
            "type": 1,
            "options": [{"name": "prompt", "type": 3, "value": prompt}]
        }
    }

    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 204:
            print("✅ Successfully sent `/imagine` command!")
        else:
            print(f"❌ Error sending command: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

# Flask API will call this function
async def handle_prompt_request(prompt):
    await send_midjourney_prompt(prompt)

# Run the bot
bot.run(TOKEN)
