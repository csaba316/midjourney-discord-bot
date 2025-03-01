import discord
import requests
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Use Railway Environment Variable
NODE_SERVER_URL = os.getenv("NODE_SERVER_URL")  # Use Railway Env Variable

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author.bot and message.attachments:  # Detect MidJourney's response
        image_url = message.attachments[0].url

        # Send image URL to Node.js API
        requests.post(f"{NODE_SERVER_URL}/receive-image", json={"image_url": image_url})
        print(f"Image sent to Node.js API: {image_url}")

client.run(TOKEN)
