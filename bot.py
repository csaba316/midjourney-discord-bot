import discord
import requests
import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import threading
from waitress import serve

# Load environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MIDJOURNEY_CHANNEL_ID = int(os.getenv("MIDJOURNEY_CHANNEL_ID"))
APPLICATION_ID = os.getenv("DISCORD_APPLICATION_ID")  # MidJourney App ID

# Set up bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    print("Listening for MidJourney prompts...")

# Flask API Setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 🔥 Allow CORS for all routes

@app.before_request
def log_request_info():
    """Log all incoming requests for debugging"""
    print(f"🔍 Incoming request: {request.method} {request.path}")

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
    asyncio.run_coroutine_threadsafe(send_midjourney_prompt(prompt), bot.loop)

    response = jsonify({"message": "Prompt sent to MidJourney!"})
    response.headers.add("Access-Control-Allow-Origin", "*")  # 🔥 Allow all origins
    return response

# Function to trigger `/imagine` properly
async def send_midjourney_prompt(prompt):
    channel = bot.get_channel(MIDJOURNEY_CHANNEL_ID)
    if not channel:
        print("❌ Error: MidJourney channel not found!")
        return

    print(f"📩 Sending MidJourney prompt: {prompt}")

    url = "https://discord.com/api/v10/interactions"
    payload = {
        "type": 2,  # Type 2 = Application Command
        "application_id": APPLICATION_ID,
        "guild_id": str(channel.guild.id),
        "channel_id": str(channel.id),
        "session_id": "midjourney-bot",
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
