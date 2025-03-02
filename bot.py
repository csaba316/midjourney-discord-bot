import discord
import requests
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
NODE_SERVER_URL = os.getenv("NODE_SERVER_URL")

# Ensure the bot has the right intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # REQUIRED for message reading

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')
    print("Listening for MidJourney messages...")

@client.event
async def on_message(message):
    print(f"📩 Message received in {message.channel}: {message.content}")

    # Detect MidJourney image
    if message.author.bot and message.attachments:
        image_url = message.attachments[0].url
        print(f"🎨 MidJourney Image Detected: {image_url}")

        # Send the image URL to Node.js API
        try:
            response = requests.post(f"{NODE_SERVER_URL}/receive-image", json={"image_url": image_url})
            print("✅ Image URL sent:", image_url)
        except Exception as e:
            print("❌ Failed to send image:", e)

client.run(TOKEN)
