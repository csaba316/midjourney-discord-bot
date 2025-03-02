import discord
import requests
import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from waitress import serve  # Use a production WSGI server

# Load environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
NODE_SERVER_URL = os.getenv("NODE_SERVER_URL")

# Ensure the channel ID is valid
channel_id_str = os.getenv("MIDJOURNEY_CHANNEL_ID")
if not channel_id_str or not channel_id_str.isdigit():
    raise ValueError(f"❌ Invalid MIDJOURNEY_CHANNEL_ID: {channel_id_str}")

MIDJOURNEY_CHANNEL_ID = int(channel_id_str)  # Convert to integer safely

# Set up bot intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

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

# Flask API for Elementor to send prompts
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.before_request
def handle_cors_preflight():
    """Handles CORS preflight OPTIONS requests"""
    if request.method == "OPTIONS":
        response = jsonify({"message": "CORS preflight success"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response, 200

@app.route('/send-prompt', methods=['POST'])
def handle_prompt():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    print(f"📩 Received prompt from Elementor: {prompt}")

    # Use asyncio to send the command from the bot
    asyncio.run_coroutine_threadsafe(send_midjourney_prompt(prompt), client.loop)

    response = jsonify({"message": "Prompt sent to MidJourney!"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

# Run Flask using Waitress (Production WSGI Server)
def run_api():
    print("🚀 Starting Flask API with Waitress...")
    serve(app, host="0.0.0.0", port=5000)

# Run the API in a separate thread
api_thread = threading.Thread(target=run_api, daemon=True)
api_thread.start()

# Start bot
client.run(TOKEN)
