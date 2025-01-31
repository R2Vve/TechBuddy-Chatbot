# -*- coding: utf-8 -*-
"""Chatbot.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qEEzpFWUG58xLuR2mvyE0AbAhjTlJ7o2
"""

!pip install flask flask-cors openai==0.28.0 pyngrok python-dotenv nest-asyncio

from google.colab import userdata
import nest_asyncio
from pyngrok import ngrok
import openai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import secrets
import os
from functools import wraps
from typing import List, Dict
import time
import random
from datetime import datetime, timezone


nest_asyncio.apply()


OPENAI_API_KEY = userdata.get('OPENAI_API_KEY2')
NGROK_AUTH_TOKEN = userdata.get('NGROK_AUTH_TOKEN')

if not OPENAI_API_KEY:
    raise ValueError("Please add OPENAI_API_KEY2 to your Colab secrets!")
if not NGROK_AUTH_TOKEN:
    raise ValueError("Please add NGROK_AUTH_TOKEN to your Colab secrets!")


openai.api_key = OPENAI_API_KEY
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

print("✅ Initial setup completed!")

class PersonalizedChatbot:
    def __init__(self, api_key):
        """Initialize chatbot with API key and KPI tracking"""
        try:
            self.api_key = api_key
            self.start_time = datetime.now(timezone.utc)

            # Chatbot personality and configuration
            self.personality = {
                "role": "customer_service",
                "tone": "friendly and professional",
                "expertise": "tech support",
                "name": "TechBuddy"
            }

            # Initialize KPI tracking
            self.kpis = {
                "satisfaction_score": [],
                "response_times": [],
                "resolved_queries": 0,
                "total_queries": 0,
                "current_survey": None,
                "session_start": self.start_time,
                "user_engagement": []
            }

            # Define surveys for feedback
            self.surveys = {
                "satisfaction": {
                    "question": "How satisfied are you with our service? (1-5)",
                    "type": "rating",
                    "options": range(1, 6)
                },
                "improvement": {
                    "question": "What area should we improve? (Type the number)\n1. Response Time\n2. Answer Quality\n3. User Interface\n4. Other",
                    "type": "choice",
                    "options": range(1, 5)
                },
                "resolution": {
                    "question": "Was your issue resolved? (yes/no)",
                    "type": "boolean",
                    "options": ["yes", "no"]
                }
            }

            # Conversation history
            self.conversation_history = []

            # System message
            self.system_message = f"""
                        You are {self.personality['name']}, a {self.personality['tone']} chatbot specialized in {self.personality['expertise']}.
            Current time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
            Current user: R2Vve

            When providing product listings:
            1. Always include detailed descriptions
            2. Use clear separators between product name and description (use '-' or ':')
            3. Break down features with proper punctuation
            4. Include price if available
            5. List at least 3 options when comparing products
            6. Format specifications in clear, separate points

            Example format:
            1. Product Name - Main description. Feature one. Feature two. Feature three.
            2. Product Name - Main description. Feature one. Feature two. Feature three.

            Your goal is to provide helpful, accurate, and efficient support while maintaining a consistent personality.
            """

            print(f"✅ {self.personality['name']} initialized successfully!")

        except Exception as e:
            print(f"❌ Error initializing chatbot: {str(e)}")
            raise

    def handle_survey_response(self, response, survey_type):
        """Process survey responses and update KPIs"""
        current_time = datetime.now(timezone.utc)

        if survey_type == "satisfaction":
            score = int(response)
            self.kpis["satisfaction_score"].append({
                "score": score,
                "timestamp": current_time
            })
            return {
                "response": "Thank you for your feedback! Would you like to share what we could improve?",
                "type": "survey_followup",
                "next_survey": "improvement"
            }

        elif survey_type == "improvement":
            improvement_areas = ["Response Time", "Answer Quality", "User Interface", "Other"]
            area = improvement_areas[int(response) - 1]
            self.kpis["user_engagement"].append({
                "type": "improvement_feedback",
                "area": area,
                "timestamp": current_time
            })
            return {
                "response": f"Thank you for suggesting we improve our {area}. Was your issue resolved?",
                "type": "survey_followup",
                "next_survey": "resolution"
            }

        elif survey_type == "resolution":
            if response.lower() == "yes":
                self.kpis["resolved_queries"] += 1
            return {
                "response": "Thank you for your feedback! Your input helps us improve our service.",
                "type": "survey_complete"
            }

    def generate_response(self, user_input: str) -> dict:
        """Generate response with KPI tracking and surveys"""
        start_time = time.time()
        current_time = datetime.now(timezone.utc)

        try:
            # Handle active survey
            if self.kpis["current_survey"]:
                survey = self.kpis["current_survey"]
                if user_input.lower() in [str(opt) for opt in self.surveys[survey]["options"]]:
                    response_data = self.handle_survey_response(user_input, survey)
                    self.kpis["current_survey"] = response_data.get("next_survey")
                    return response_data
                else:
                    return {
                        "response": f"Please provide a valid response for {self.surveys[survey]['question']}",
                        "type": "survey_error"
                    }

            # Generate chat response
            messages = [{"role": "system", "content": self.system_message}]
            for message in self.conversation_history[-5:]:
                messages.append(message)
            messages.append({"role": "user", "content": user_input})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )

            bot_response = response.choices[0].message['content']

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": bot_response})

            # Update KPIs
            self.kpis["total_queries"] += 1
            self.kpis["response_times"].append({
                "time": time.time() - start_time,
                "timestamp": current_time
            })

            # Randomly trigger satisfaction survey (20% chance)
            if random.random() < 0.2 and len(self.conversation_history) > 4:
                self.kpis["current_survey"] = "satisfaction"
                return {
                    "response": bot_response,
                    "follow_up": self.surveys["satisfaction"]["question"],
                    "type": "survey_request"
                }

            return {
                "response": bot_response,
                "type": "chat"
            }

        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "type": "error"
            }

    def get_kpi_metrics(self):
        """Calculate and return current KPI metrics"""
        current_time = datetime.now(timezone.utc)
        session_duration = (current_time - self.kpis["session_start"]).total_seconds() / 60  # in minutes

        # Calculate satisfaction score
        if self.kpis["satisfaction_score"]:
            avg_satisfaction = sum(item["score"] for item in self.kpis["satisfaction_score"]) / len(self.kpis["satisfaction_score"])
        else:
            avg_satisfaction = 0

        # Calculate response time
        if self.kpis["response_times"]:
            avg_response_time = sum(item["time"] for item in self.kpis["response_times"]) / len(self.kpis["response_times"])
        else:
            avg_response_time = 0

        return {
            "average_satisfaction": round(avg_satisfaction, 2),
            "average_response_time": round(avg_response_time, 2),
            "total_queries": self.kpis["total_queries"],
            "resolved_queries": self.kpis["resolved_queries"],
            "session_duration_minutes": round(session_duration, 2),
            "response_rate": round(self.kpis["total_queries"] / session_duration, 2) if session_duration > 0 else 0,
            "resolution_rate": round(self.kpis["resolved_queries"] / self.kpis["total_queries"] * 100, 2) if self.kpis["total_queries"] > 0 else 0,
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S UTC")
        }

print("✅ Chatbot class created!")

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Generate API key
API_KEY = secrets.token_hex(32)

# Initialize chatbot
chatbot = PersonalizedChatbot(OPENAI_API_KEY)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    """Add the missing status endpoint"""
    return jsonify({
        'status': 'online',
        'url': os.getenv('NGROK_URL', ''),
        'api_key': API_KEY,
        'server_time': '2025-01-23 03:40:31',
        'user': 'R2Vve'
    })

@app.route('/chat', methods=['POST'])
@require_api_key
def chat():
    try:
        data = request.get_json()
        message = data.get('message')

        if not message:
            return jsonify({'error': 'No message provided'}), 400

        response_data = chatbot.generate_response(message)
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/kpi-metrics')
@require_api_key
def get_metrics():
    return jsonify(chatbot.get_kpi_metrics())

# Add error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({'error': 'Unauthorized'}), 401

print("✅ Flask application created!")

!mkdir -p templates


html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TechBuddy Chat | Active User: R2Vve</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        /* Base Chat Icon Styles */
        .chat-icon {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #4F46E5;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            transform-origin: center;
            z-index: 1000;
        }

        .chat-icon:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0,0,0,0.2);
            background: #4338CA;
        }

        .chat-icon.active {
            transform: rotate(360deg) scale(0.9);
            background: #4338CA;
        }

        /* Chat Window Styles */
        .chat-window {
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 380px;
            height: 600px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            transform: translateY(20px) scale(0.95);
            opacity: 0;
            visibility: hidden;
            display: flex;
            flex-direction: column;
            z-index: 999;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .chat-window.active {
            transform: translateY(0) scale(1);
            opacity: 1;
            visibility: visible;
        }

        /* Message Styles */
        .message-bubble {
            animation: slideIn 0.3s ease-out forwards;
            transition: all 0.3s ease;
        }

        .message-bubble:hover {
            transform: translateY(-2px);
        }

        .message-bubble.new {
            animation: pulse 0.5s ease-out;
        }

        /* Typing Indicator */
        .typing-indicator {
            display: flex;
            padding: 8px;
            gap: 4px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: #4F46E5;
            border-radius: 50%;
            animation: typing 1s infinite ease-in-out;
        }

        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }

        /* KPI Display */
        .kpi-card {
            background: rgba(79, 70, 229, 0.1);
            border-radius: 8px;
            padding: 8px;
            margin: 4px 0;
            transition: all 0.3s ease;
        }

        .kpi-card:hover {
            background: rgba(79, 70, 229, 0.15);
            transform: translateY(-2px);
        }

        /* Animations */
        @keyframes typing {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-6px); }
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        /* Survey Styles */
        .survey-options {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 8px;
            margin-top: 8px;
        }

        .survey-option {
            padding: 8px;
            text-align: center;
            background: #EEF2FF;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .survey-option:hover {
            background: #E0E7FF;
            transform: translateY(-2px);
        }
    </style>
</head>
<body class="bg-gray-100">
    <!-- Chat Icon -->
    <div class="chat-icon" id="chat-icon">
        <i class="fas fa-comment-dots text-white text-2xl"></i>
    </div>

    <!-- Chat Window -->
    <div class="chat-window" id="chat-window">
        <!-- Header -->
        <div class="bg-indigo-600 text-white p-4 rounded-t-lg">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-xl font-bold">TechBuddy Support</h1>
                    <p class="text-sm opacity-90">Welcome, R2Vve!</p>
                    <p class="text-xs opacity-75" id="chat-time">Session started: 2025-01-23 03:36:37 UTC</p>
                </div>
                <button id="close-chat" class="text-white hover:bg-indigo-700 rounded-full p-2 transition-colors">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <p id="connection-status" class="text-sm mt-2 flex items-center">
                <i class="fas fa-circle text-xs mr-2"></i>
                Connecting...
            </p>
            <div id="kpi-display" class="mt-2 text-xs bg-indigo-700/50 p-2 rounded hidden"></div>
        </div>

        <!-- Messages Container -->
        <div id="chat-messages" class="flex-grow p-4 overflow-y-auto space-y-4 bg-gray-50">
            <!-- Messages will be inserted here -->
        </div>

        <!-- Input Area -->
        <div class="border-t p-4 bg-white">
            <div class="flex space-x-3">
                <input type="text" id="user-input"
                    class="flex-grow rounded-lg border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="Type your message here..."
                    disabled>
                <button id="send-button"
                    class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors disabled:opacity-50"
                    disabled>
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>

    <script>
        // Constants
        const CURRENT_USER = 'R2Vve';
        const CURRENT_UTC_TIME = '2025-01-23 03:36:37';
        const CHAT_URL = window.location.origin;
        let API_KEY = '';

        // Chat UI Handler
        class ChatUI {
            static toggleChat() {
                const chatIcon = document.getElementById('chat-icon');
                const chatWindow = document.getElementById('chat-window');
                chatIcon.classList.toggle('active');
                chatWindow.classList.toggle('active');

                if (chatWindow.classList.contains('active')) {
                    document.getElementById('user-input').focus();
                    this.updateKPIMetrics();
                }
            }

            static addMessage(content, isUser, type = 'chat') {
                const messagesContainer = document.getElementById('chat-messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;

                const messageBubble = document.createElement('div');
                messageBubble.className = `message-bubble max-w-[70%] rounded-lg p-3 ${
                    isUser ? 'bg-indigo-600 text-white' : 'bg-white text-gray-800 shadow-sm'
                }`;

                if (type === 'kpi' || type === 'survey_request') {
                    messageBubble.innerHTML = content;
                    messageBubble.classList.add('kpi-card');
                } else {
                    messageBubble.textContent = content;
                }

                messageDiv.appendChild(messageBubble);
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;

                // Add pulse animation
                messageBubble.classList.add('new');
                setTimeout(() => messageBubble.classList.remove('new'), 500);
            }

            static showTypingIndicator() {
                const indicator = document.createElement('div');
                indicator.className = 'typing-indicator';
                for (let i = 0; i < 3; i++) {
                    const dot = document.createElement('div');
                    dot.className = 'typing-dot';
                    indicator.appendChild(dot);
                }
                return indicator;
            }

            static async updateKPIMetrics() {
                try {
                    const response = await fetch(`${CHAT_URL}/kpi-metrics`, {
                        headers: { 'X-API-Key': API_KEY }
                    });
                    const metrics = await response.json();

                    const kpiDisplay = document.getElementById('kpi-display');
                    kpiDisplay.innerHTML = `
                        <div class="grid grid-cols-2 gap-2">
                            <div class="kpi-card">
                                <div class="font-bold">⭐ Satisfaction</div>
                                <div class="text-lg">${metrics.average_satisfaction}/5</div>
                            </div>
                            <div class="kpi-card">
                                <div class="font-bold">⏱️ Response Time</div>
                                <div class="text-lg">${metrics.average_response_time.toFixed(1)}s</div>
                            </div>
                            <div class="kpi-card">
                                <div class="font-bold">📝 Queries</div>
                                <div class="text-lg">${metrics.total_queries}</div>
                            </div>
                            <div class="kpi-card">
                                <div class="font-bold">✅ Resolution Rate</div>
                                <div class="text-lg">${metrics.resolution_rate}%</div>
                            </div>
                        </div>
                    `;
                    kpiDisplay.classList.remove('hidden');
                } catch (error) {
                    console.error('Error updating KPI metrics:', error);
                }
            }
        }

        // Chat Logic
       async function initializeApp() {
    try {
        const response = await fetch(`${CHAT_URL}/status`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (data.api_key) {
            API_KEY = data.api_key;
            console.log('Successfully obtained API key');
            updateConnectionStatus('Connected', 'success');
            enableInput();
            ChatUI.addMessage(`Welcome, ${CURRENT_USER}! 👋 How can I help you today?`, false);
            await ChatUI.updateKPIMetrics(); // Use await here
        } else {
            throw new Error('No API key received');
        }
    } catch (error) {
        console.error('Connection error:', error);
        updateConnectionStatus(`Failed to connect: ${error.message}`, 'error');
    }
}

        function updateConnectionStatus(message, status) {
            const statusElement = document.getElementById('connection-status');
            const statusIcon = statusElement.querySelector('i');

            statusElement.textContent = message;
            statusElement.prepend(statusIcon);

            switch(status) {
                case 'success':
                    statusIcon.className = 'fas fa-circle text-xs mr-2 text-green-400';
                    break;
                case 'error':
                    statusIcon.className = 'fas fa-circle text-xs mr-2 text-red-400';
                    break;
                default:
                    statusIcon.className = 'fas fa-circle text-xs mr-2 text-yellow-400';
            }
        }

        function enableInput() {
            document.getElementById('user-input').disabled = false;
            document.getElementById('send-button').disabled = false;
        }

        async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    if (!message) return;

    userInput.disabled = true;
    document.getElementById('send-button').disabled = true;

    ChatUI.addMessage(message, true);
    userInput.value = '';

    const typingIndicator = ChatUI.showTypingIndicator();
    document.getElementById('chat-messages').appendChild(typingIndicator);

    try {
        const response = await fetch(`${CHAT_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        typingIndicator.remove();

        if (data.error) {
            ChatUI.addMessage(`Error: ${data.error}`, false, 'error');
        } else {
            ChatUI.addMessage(data.response, false, data.type);

            if (data.type === 'survey_request' && data.follow_up) {
                setTimeout(() => {
                    ChatUI.addMessage(data.follow_up, false, 'survey');
                }, 1000);
            }

            ChatUI.updateKPIMetrics();
        }
    } catch (error) {
        console.error('Error sending message:', error);
        typingIndicator.remove();
        ChatUI.addMessage(`Error: ${error.message}`, false, 'error');
    } finally {
        userInput.disabled = false;
        document.getElementById('send-button').disabled = false;
        userInput.focus();
    }
}

        // Event Listeners
        document.getElementById('chat-icon').addEventListener('click', () => ChatUI.toggleChat());
        document.getElementById('close-chat').addEventListener('click', () => ChatUI.toggleChat());
        document.getElementById('user-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.target.disabled) {
                sendMessage();
            }
        });
        document.getElementById('send-button').addEventListener('click', sendMessage);

        // Start the application
        initializeApp();
    </script>
</body>
</html>
'''

# Write the HTML content to a file
with open('templates/index.html', 'w') as f:
    f.write(html_content)

# Kill any existing processes
!killall ngrok 2>/dev/null || true
!pkill flask 2>/dev/null || true

try:
    # Start ngrok and run the Flask app
    ngrok_tunnel = ngrok.connect(5000)
    print(f'✅ Public URL: {ngrok_tunnel.public_url}')

    # Store ngrok URL
    os.environ['NGROK_URL'] = str(ngrok_tunnel.public_url)

    # Run the Flask app
    app.run(port=5000)
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nPlease make sure you:")
    print("1. Have added your ngrok authtoken to Colab secrets as 'NGROK_AUTH_TOKEN'")
    print("2. Your authtoken is correct and valid")
    print("3. You have a working internet connection")


    f.write('secrets.json\n')  # Ignore any secrets file
