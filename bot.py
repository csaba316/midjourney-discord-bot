import discord
import requests
import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from waitress import serve
import socket  # Added for port binding test

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

@app.before_request
def log_request_info():
    print(f"🔍 Incoming request: {request.method} {request.path}")

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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Flask API is running"}), 200

@app.route('/send-prompt', methods=['OPTIONS'])
def cors_preflight():
    """Handles CORS preflight OPTIONS requests"""
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
    response.headers.add("Access-Control-Allow-Origin", "*")  # Explicitly allow all origins
    return response

# Run Flask using Waitress (Production WSGI Server)
def run_api():
    port = int(os.getenv("PORT", 5000))  # Use Railway's assigned port or default to 5000
    print(f"🚀 Starting Flask API with Waitress on port {port}...")

    # Check if port is reachable
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("0.0.0.0", port))
        print(f"✅ Port {port} is available and listening.")
    except Exception as e:
        print(f"❌ Error binding to port {port}: {e}")
    s.close()

    serve(app, host="0.0.0.0", port=port)

# Run the API in a separate thread
api_thread = threading.Thread(target=run_api, daemon=True)
api_thread.start()

# Start bot
client.run(TOKEN)
