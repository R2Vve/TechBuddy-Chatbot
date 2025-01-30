# 🤖 TechBuddy Chatbot

TechBuddy is a friendly and professional chatbot specialized in tech support. It provides efficient and accurate responses to user queries while maintaining a consistent personality.

## ✨ Features

- **Personalized Responses**: Tailored responses based on user input.
- **KPI Tracking**: Tracks key performance indicators like response time, satisfaction score, and resolution rate.
- **Surveys**: Collects user feedback to improve service quality.
- **Real-time Metrics**: Displays real-time KPI metrics during the chat session.

## 🛠️ Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git
- Ngrok

### Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/TechBuddy-Chatbot.git
    cd TechBuddy-Chatbot
    ```

2. Install the required Python packages:

    ```bash
    pip install flask flask-cors openai==0.28.0 pyngrok python-dotenv nest-asyncio
    ```

3. Set up your environment variables:
    - Add your `OPENAI_API_KEY2` and `NGROK_AUTH_TOKEN` to your environment variables or Colab secrets.

## 🚀 Usage

1. **Run the Flask App**:
    ```bash
    python scripts/main.py
    ```

2. **Access the Chatbot**:
    - Use the public URL provided by Ngrok to interact with the chatbot.

## 📁 Files and Directories

- `scripts/`: Contains the main script for running the chatbot.
- `data/`: Directory for storing data files.
- `templates/`: HTML templates for the Flask app.
- `README.md`: This file.

## 🤝 Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## 📜 License

This project is licensed under the MIT License.
