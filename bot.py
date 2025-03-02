import discord
import requests
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Ensure this is set in Railway
NODE_SERVER_URL = os.getenv("NODE_SERVER_URL")  # Your Node.js API
MIDJOURNEY_CHANNEL_ID = int(os.getenv("MIDJOURNEY_CHANNEL_ID"))  # MidJourney channel ID

intents = discord.Intents.default()
intents.messages = True  # Required to listen for messages
intents.message_content = True  # Required to read messages

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')
    print("Listening for MidJourney messages and prompts...")

# Command to send prompt to MidJourney
async def send_midjourney_prompt(prompt):
    channel = client.get_channel(MIDJOURNEY_CHANNEL_ID)
    if channel:
        print(f"📩 Sending MidJourney prompt: {prompt}")
        await channel.send(f"/imagine {prompt}")
    else:
        print("❌ Error: MidJourney channel not found!")

# Handle messages (detect MidJourney images)
@client.event
async def on_message(message):
    # Ignore bot messages that are not from MidJourney
    if message.author.bot and message.attachments:
        image_url = message.attachments[0].url
        print(f"🎨 MidJourney Image Detected: {image_url}")

        # Send image URL to Node.js API
        try:
            response = requests.post(f"{NODE_SERVER_URL}/receive-image", json={"image_url": image_url})
            print("✅ Image URL sent to Node.js API:", image_url)
        except Exception as e:
            print("❌ Failed to send image:", e)

# Start bot
client.run(TOKEN)
