# app.py
import sys
import os
import streamlit as st
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Scripts.rag import get_answer
from db import (
    generate_conversation_id,
    save_conversation,
    save_feedback,
    get_recent_conversations,
    get_feedback_stats
)

# Initialize session state variables
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []
if 'last_conversation_id' not in st.session_state:
    st.session_state['last_conversation_id'] = None
if 'last_answer' not in st.session_state:
    st.session_state['last_answer'] = None
if 'last_processing_time' not in st.session_state:
    st.session_state['last_processing_time'] = None
if 'last_relevance' not in st.session_state:
    st.session_state['last_relevance'] = None
if 'last_model_used' not in st.session_state:
    st.session_state['last_model_used'] = None
if 'last_total_tokens' not in st.session_state:
    st.session_state['last_total_tokens'] = None
if 'last_openai_cost' not in st.session_state:
    st.session_state['last_openai_cost'] = 0.0

# Title
st.title("AI-Powered Skincare Chatbot")

# User Input
user_input = st.text_input("Enter your question:")
ask_button = st.button("Ask")

if ask_button and user_input:
    with st.spinner('Processing your question...'):
        start_time = time.time()
        # Generate a unique conversation ID
        conversation_id = generate_conversation_id()
        # Get the answer from the LLM
        answer_data = get_answer(user_input)
        end_time = time.time()
        processing_time = end_time - start_time

    # Debug: Display answer_data contents
    logging.info(f"answer_data: {answer_data}")

    # Ensure all required keys are present in answer_data
    required_keys = ["answer", "model_used", "response_time", "relevance", "total_tokens", "openai_cost"]
    for key in required_keys:
        if key not in answer_data or answer_data[key] is None:
            if key in ["response_time", "openai_cost"]:
                answer_data[key] = 0.0
            elif key == "total_tokens":
                answer_data[key] = 0
            else:
                answer_data[key] = "N/A"

    # Convert numerical values to native Python types
    answer_data["response_time"] = float(answer_data["response_time"])
    answer_data["total_tokens"] = int(answer_data["total_tokens"])
    answer_data["openai_cost"] = float(answer_data["openai_cost"])

    # Ensure 'relevance' and 'model_used' are strings
    answer_data["relevance"] = str(answer_data.get("relevance", "N/A"))
    answer_data["model_used"] = str(answer_data.get("model_used", "Unknown"))

    # Save the conversation to the database
    try:
        save_conversation(conversation_id, user_input, answer_data)
        # Store the conversation_id and other data in session state
        st.session_state['last_conversation_id'] = conversation_id
        st.session_state['last_answer'] = answer_data["answer"]
        st.session_state['last_processing_time'] = processing_time
        st.session_state['last_relevance'] = answer_data.get('relevance', 'N/A')
        st.session_state['last_model_used'] = answer_data.get('model_used', 'N/A')
        st.session_state['last_total_tokens'] = answer_data.get('total_tokens', 'N/A')
        st.session_state['last_openai_cost'] = answer_data.get('openai_cost', 0.0)
    except Exception as e:
        st.error(f"Error saving conversation: {e}")
        logging.error(f"Error saving conversation: {e}")

    # Append to conversation history
    st.session_state.conversation_history.append({
        'conversation_id': conversation_id,
        'question': user_input,
        'answer': answer_data["answer"],
        'relevance': answer_data.get('relevance', 'N/A'),
        'processing_time': processing_time,
        'feedback': None  # Will be updated upon feedback
    })

# Display the answer and feedback buttons if a conversation exists
if st.session_state.get('last_conversation_id', None):
    # Display the answer
    st.subheader("Answer:")
    st.write(st.session_state['last_answer'])

    # Display monitoring information
    st.subheader("Monitoring Information")
    st.write(f"Response time: {st.session_state['last_processing_time']:.2f} seconds")
    st.write(f"Relevance: {st.session_state['last_relevance']}")
    st.write(f"Model used: {st.session_state['last_model_used']}")
    st.write(f"Total tokens: {st.session_state['last_total_tokens']}")
    if st.session_state['last_openai_cost'] > 0:
        st.write(f"OpenAI cost: ${st.session_state['last_openai_cost']:.4f}")

    # Feedback Buttons
    st.subheader("Was this answer helpful?")
    col1, col2 = st.columns(2)

    last_conversation_id = st.session_state['last_conversation_id']
    with col1:
        if st.button("👍 Yes", key="yes_button"):
            try:
                save_feedback(last_conversation_id, "RELEVANT")
                st.success("Thank you for your feedback!")
                # Update feedback in conversation history
                for convo in st.session_state.conversation_history:
                    if convo['conversation_id'] == last_conversation_id:
                        convo['feedback'] = "RELEVANT"
            except Exception as e:
                st.error(f"Error saving feedback: {e}")
                logging.error(f"Error saving feedback: {e}")
    with col2:
        if st.button("👎 No", key="no_button"):
            try:
                save_feedback(last_conversation_id, "NON_RELEVANT")
                st.success("Thank you for your feedback!")
                # Update feedback in conversation history
                for convo in st.session_state.conversation_history:
                    if convo['conversation_id'] == last_conversation_id:
                        convo['feedback'] = "NON_RELEVANT"
            except Exception as e:
                st.error(f"Error saving feedback: {e}")
                logging.error(f"Error saving feedback: {e}")
else:
    st.write("Please ask a question to get started.")

# Display Recent Conversations
try:
    st.subheader("Recent Conversations")
    relevance_filter = st.selectbox(
        "Filter by relevance:", ["All", "RELEVANT", "NON_RELEVANT"]
    )

    # Retrieve conversations from the database
    try:
        recent_conversations = get_recent_conversations(relevance_filter=relevance_filter)
    except Exception as e:
        st.error(f"Error retrieving recent conversations: {e}")
        logging.error(f"Error retrieving recent conversations: {e}")
        recent_conversations = []

    # Display conversations
    for convo in recent_conversations:
        st.write(f"**Question:** {convo['question']}")
        st.write(f"**Answer:** {convo['answer']}")
        st.write(f"**Feedback:** {convo.get('feedback', 'No feedback')}")
        st.write(f"**Response time:** {convo.get('response_time', 'N/A')}")
        st.markdown("---")

    # Display feedback stats
    feedback_stats = get_feedback_stats()
    st.subheader("Feedback Statistics")
    st.write(f"Thumbs up: {feedback_stats['thumbs_up'] or 0}")
    st.write(f"Thumbs down: {feedback_stats['thumbs_down'] or 0}")
except Exception as e:
    st.error(f"Error retrieving data: {e}")
    logging.error(f"Error retrieving data: {e}")
