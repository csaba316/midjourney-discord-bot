import discord
import requests
import os
import asyncio
from flask import Flask, request, jsonify
import threading

# Load environment variables (set these in Railway)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Discord bot token
MIDJOURNEY_CHANNEL_ID = int(os.getenv("MIDJOURNEY_CHANNEL_ID"))  # MidJourney channel ID
NODE_SERVER_URL = os.getenv("NODE_SERVER_URL")  # Your Node.js API for Elementor

# Set up bot intents
intents = discord.Intents.default()
intents.messages = True  # Required to listen for messages
intents.message_content = True  # Required to read messages

# Initialize bot
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')
    print("Listening for MidJourney messages and prompts...")

# Function to send `/imagine` command to MidJourney
async def send_midjourney_prompt(prompt):
    channel = client.get_channel(MIDJOURNEY_CHANNEL_ID)
    if channel:
        print(f"📩 Sending MidJourney prompt: {prompt}")
        await channel.send(f"/imagine {prompt}")
    else:
        print("❌ Error: MidJourney channel not found!")

# Detect MidJourney-generated images and forward to Node.js API
@client.event
async def on_message(message):
    if message.author.bot and message.attachments:  # Detect MidJourney bot messages
        image_url = message.attachments[0].url
        print(f"🎨 MidJourney Image Detected: {image_url}")

        # Send image URL to Node.js API
        try:
            response = requests.post(f"{NODE_SERVER_URL}/receive-image", json={"image_url": image_url})
            if response.status_code == 200:
                print("✅ Image URL sent to Node.js API:", image_url)
            else:
                print(f"❌ Failed to send image. API response: {response.text}")
        except Exception as e:
            print("❌ Error sending image to API:", e)

# Flask API to receive prompts from Elementor and send to MidJourney
app = Flask(__name__)

@app.route('/send-prompt', methods=['POST'])
def handle_prompt():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    print(f"📩 Received prompt from Elementor: {prompt}")

    # Use asyncio to send the command from the bot
    asyncio.run_coroutine_threadsafe(send_midjourney_prompt(prompt), client.loop)

    return jsonify({"message": "Prompt sent to MidJourney!"}), 200

# Run the Flask API in a separate thread
def run_api():
    app.run(host="0.0.0.0", port=5000)

api_thread = threading.Thread(target=run_api)
api_thread.start()

# Start bot
client.run(TOKEN)
