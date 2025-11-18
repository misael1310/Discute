import streamlit as st

from main import transcribe_audio, generate_response
from prompt_managements import pm

# Constants
MODEL_CONTEXT = "openai/gpt-oss-20b"
MODEL_CHAT = "openai/gpt-oss-20b"

def init_session_state() -> None:
    """Initialize session state variables if they don't exist"""
    if "context" not in st.session_state:
        st.session_state.context = ""
    if "chat" not in st.session_state:
        st.session_state.chat = []
    if "selected_level" not in st.session_state:
        st.session_state.selected_level = "A1"  # Default to beginner
    if "selected_program" not in st.session_state:
        st.session_state.selected_program = pm.get_default_program("A1") or ""

def display_chat_history() -> None:
    """Display the chat history with audio playback"""
    for msg in st.session_state.chat:
        with st.container(border=True):
            role_label = "**Me**" if msg["role"] == "me" else "**Assistant**"
            st.write(role_label)
            if role_label == "**Me**":
                if "audio" in msg:
                    st.audio(msg["audio"], format="audio/wav")
                else:
                    st.caption("Audio unavailable for this message")
            with st.expander("Show details", expanded=False):
                st.write(f"**Message:** {msg['content']}")

def format_chat_history() -> str:
    """Format the chat history for prompt context"""
    return "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in st.session_state.chat
    )

def main():
    """Main application function"""
    # App header
    st.write("# Discute")
    st.caption("Demo application for chatting with an AI assistant.")

    # API key input
    groq_api_key = st.text_input("Enter your Groq API key [Link](https://console.groq.com/home)", type="password")

    # Initialize session state
    init_session_state()

    # CEFR Level and Program Selection
    st.write("## Language Learning Settings")

    col1, col2 = st.columns(2)

    with col1:
        cefr_levels = pm.get_cefr_levels()
        selected_level = st.selectbox(
            "Select your CEFR level:",
            options=cefr_levels,
            index=cefr_levels.index(st.session_state.selected_level) if st.session_state.selected_level in cefr_levels else 0,
            help="Choose your current English proficiency level"
        )
        st.session_state.selected_level = selected_level

    with col2:
        program_options = pm.get_program_names_by_level(selected_level)
        if program_options:
            selected_program = st.selectbox(
                "Select a conversation program:",
                options=program_options,
                index=program_options.index(st.session_state.selected_program) if st.session_state.selected_program in program_options else 0,
                help="Choose a scenario to practice"
            )
            st.session_state.selected_program = selected_program

            # Display program description
            program_info = pm.get_program_info(selected_program)
            if program_info:
                st.caption(f"**{program_info['description']}** (Difficulty: {program_info['difficulty']})")
        else:
            st.warning("No programs available for this level yet.")
            st.session_state.selected_program = ""

    st.divider()

    # Display the current context
    if st.session_state.context:
        st.write("**Context:**")
        st.info(st.session_state.context)

    # Display chat history
    display_chat_history()

    # Audio input section
    audio_col, btn_col = st.columns([3, 1])

    with audio_col:
        audio_value = st.audio_input("Record a voice message")

    with btn_col:
        # Add vertical spacing
        st.write("")
        st.write("")
        st.write("")
        if st.button("Send", use_container_width=True):
            if not audio_value:
                st.error("Please record a voice message before sending.")
            elif not groq_api_key:
                st.error("Please enter your Groq API key before sending.")
            else:
                # Process user audio
                audio_bytes = audio_value.read()
                text = transcribe_audio(audio_bytes)
                st.session_state.chat.append({"role": "me", "content": text, "audio": audio_bytes})

                # Generate AI response
                chat_history = format_chat_history()
                prompt_vars = {
                        "Context": st.session_state.context,
                        "ChatHistory": chat_history
                }

                # Use selected program for chat prompt
                if st.session_state.selected_program:
                    chat_prompt = pm.get_prompt(st.session_state.selected_program, variables=prompt_vars)
                else:
                    # Fallback to default if no program selected
                    default_program = pm.get_default_program(st.session_state.selected_level)
                    if default_program:
                        chat_prompt = pm.get_prompt(default_program, variables=prompt_vars)
                    else:
                        st.error("No conversation programs available. Please check database setup.")
                        st.stop()

                ai_response = generate_response(chat_prompt, MODEL_CHAT, groq_api_key)

                # Add to chat history
                st.session_state.chat.append({
                        "role": "you",
                        "content": ai_response,
                })

                # Refresh the page
                st.rerun()

    # Coach review section
    st.write("**AI Coach Review**")

    if st.button("Review and Correct", use_container_width=True):
        if not st.session_state.chat:
            st.error("No conversation to review yet.")
        elif not groq_api_key:
            st.error("Please enter your Groq API key for the review.")
        else:
            conversation = format_chat_history()
            coach_vars = {
                    "context": st.session_state.context,
                    "conversation": conversation
            }

            # Use level-appropriate coach prompt
            coach_prompt = pm.get_coach_prompt(st.session_state.selected_level, variables=coach_vars)
            review = generate_response(coach_prompt, MODEL_CHAT, groq_api_key)

            st.write("**Coach Review:**")
            st.info(review)

if __name__ == "__main__":
    main()