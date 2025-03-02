import discord
import requests
import os
import asyncio
from flask import Flask, jsonify
from flask_cors import CORS
import threading
from waitress import serve

# Load environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MIDJOURNEY_CHANNEL_ID = int(os.getenv("MIDJOURNEY_CHANNEL_ID"))
NODE_SERVER_URL = os.getenv("NODE_SERVER_URL")  # Where images will be forwarded

# Set up bot intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Ensure this is enabled in Discord Developer Portal

# Initialize bot
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    print("Listening for MidJourney image messages...")

@bot.event
async def on_message(message):
    """Detects images in the MidJourney Discord channel and forwards them"""
    if message.channel.id == MIDJOURNEY_CHANNEL_ID and message.attachments:
        for attachment in message.attachments:
            image_url = attachment.url
            print(f"📥 Detected image: {image_url}")

            if NODE_SERVER_URL:
                send_image_to_server(image_url)
            else:
                print("⚠️ NODE_SERVER_URL is not set. Image will not be forwarded.")

def send_image_to_server(image_url):
    """Forwards the MidJourney image URL to the Node.js server"""
    payload = {"image_url": image_url}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(NODE_SERVER_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"✅ Image successfully forwarded: {image_url}")
        else:
            print(f"❌ Failed to forward image: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error forwarding image: {e}")

# Flask API Setup
app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Flask API is running"}), 200

# Run Flask using Waitress
def run_api():
    port = int(os.getenv("PORT", 5000))  # Use Railway's assigned port
    print(f"🚀 Starting Flask API with Waitress on port {port}...")
    serve(app, host="0.0.0.0", port=port, threads=4)


# Run the API in a separate thread
api_thread = threading.Thread(target=run_api, daemon=True)
api_thread.start()

# Start bot
bot.run(TOKEN)
