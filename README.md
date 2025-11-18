# 👋 Welcome to Discute: Your AI Language Companion!

Discute is an innovative, open-source language learning application designed
to help users practice and perfect their speaking skills in a new language.
By leveraging the power of AI, Discute simulates realistic conversations,
making language practice accessible and engaging.

## 🚀 Features

- Real-time voice transcription using Whisper for accuracy in various languages.
- Conversation simulation and language corrections powered by Groq LLM models.
- Personalized feedback through voice cloning with the Kokoro model.
- Intuitive and accessible user interface built with Streamlit.

## 🛠️ Technologies Used

- Python
- Groq for language models
- Streamlit for frontend
- SQLite for database management
- Whisper for speech-to-text (STT)
- Kokoro for text-to-speech (TTS)

## 📦 Setup and Installation

To get "Discute" running locally:

1. Clone the repository: `git clone https://github.com/5uru/Discute.git`
2. Change directory: `cd Discute`
3. Install required dependencies: `pip install -r requirements.txt`
4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your Groq API key: `GROQ_API_KEY=your_actual_api_key_here`
   - Alternatively, you can enter the API key directly in the app (not recommended for security)
5. Run the Streamlit application: `streamlit run app.py`

## 🧩 System Requirements

- Python 3.8 or higher
- Minimum 4GB RAM (8GB recommended)
- Stable internet connection for AI models
- Working microphone for voice input
- Valid Groq API key

## 🔒 Security Best Practices

- API keys are securely stored in environment variables using a `.env` file
- Never commit `.env` files to version control; they are automatically ignored by `.gitignore`
- If you prefer not to use `.env`, you can enter the API key directly in the app, but this is less secure for repeated use

##  Usage Guide

1. **Initial Setup**:
     - Launch the application with `streamlit run app.py`
     - If you configured the `.env` file with your Groq API key, it will be loaded automatically
     - Otherwise, enter your Groq API key in the provided field

2. **Context Generation**:
    - Describe a situation or use the random generator
    - Click "Generate Context" to create a conversation scenario

3. **Conversation**:
    - Select a voice from the dropdown menu
    - Record your voice message using the audio input
    - Send your message with the "Send" button
    - Listen to the AI-generated response via Kokoro TTS

4. **Review**:
    - Use "Review and Correct" to get feedback on your language skills
    - View corrections and improvement suggestions
