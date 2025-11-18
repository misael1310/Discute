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
4. Obtain a Groq API key from https://console.groq.com/home
5. **Initialize the prompt database:** `python db_setup.py`
   - This creates `prompts.db` and populates it with CEFR-level categorized prompts
6. Run the Streamlit application: `streamlit run app.py`

## 🏗️ Architecture Overview

Discute uses a modular architecture with SQLite database-driven prompt management:

- **Database Layer**: SQLite database (`prompts.db`) stores CEFR-categorized prompts
- **PromptManager**: Database interface for retrieving and formatting prompts
- **Streamlit UI**: User interface for level/program selection and conversation
- **AI Integration**: Groq API for language model interactions

### Database Schema
- `cefr_levels`: CEFR proficiency levels (A1-C2)
- `prompt_programs`: Conversation scenarios mapped to CEFR levels with tags and metadata

## 🧩 System Requirements

- Python 3.8 or higher
- Minimum 4GB RAM (8GB recommended)
- Stable internet connection for AI models
- Working microphone for voice input
- Valid Groq API key
- SQLite (built-in with Python)

## 📚 Usage Guide

1. **Initial Setup**:
     - Launch the application with `streamlit run app.py`
     - Enter your Groq API key in the dedicated field

2. **Language Learning Settings**:
     - Select your CEFR level (A1-C2) from the dropdown
     - Choose a conversation program appropriate for your level
     - Each program includes difficulty rating and description

3. **Conversation**:
     - Record your voice message using the audio input
     - Send your message with the "Send" button
     - The AI responds using the selected conversation program
     - Continue the conversation to practice the chosen scenario

4. **Review and Feedback**:
     - Use "Review and Correct" to get personalized feedback
     - Feedback is tailored to your selected CEFR level
     - View corrections, level assessment, and improvement suggestions

### Available Programs by Level
- **A1-A2**: Basic greetings, ordering food, simple interactions
- **B1-B2**: Travel scenarios, job interviews, complex conversations
- **C1-C2**: Academic discussions, debates, professional scenarios
