# app.py
import sys
import os
import streamlit as st
import time
# Get the directory containing app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (project root)
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to sys.path
sys.path.append(parent_dir)

from Scripts.rag import get_answer
from db import (
    generate_conversation_id,
    save_conversation,
    save_feedback,
    get_recent_conversations
)

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []

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

    # Save the conversation to the database
    save_conversation(conversation_id, user_input, answer_data["answer"])

    # Display the answer
    st.subheader("Answer:")
    st.write(answer_data["answer"])

    # Display monitoring information
    st.subheader("Monitoring Information")
    st.write(f"Response time: {processing_time:.2f} seconds")
    st.write(f"Relevance: {answer_data.get('relevance', 'N/A')}")
    st.write(f"Model used: {answer_data.get('model_used', 'N/A')}")
    st.write(f"Total tokens: {answer_data.get('total_tokens', 'N/A')}")
    if answer_data.get("openai_cost", 0) > 0:
        st.write(f"OpenAI cost: ${answer_data['openai_cost']:.4f}")

    # Feedback Buttons
    st.subheader("Was this answer helpful?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Yes"):
            save_feedback(conversation_id, "RELEVANT")
            st.success("Thank you for your feedback!")
    with col2:
        if st.button("👎 No"):
            save_feedback(conversation_id, "NON_RELEVANT")
            st.success("Thank you for your feedback!")

    # Append to conversation history
    st.session_state.conversation_history.append({
        'conversation_id': conversation_id,
        'question': user_input,
        'answer': answer_data["answer"],
        'relevance': answer_data.get('relevance', 'N/A'),
        'processing_time': processing_time,
        'feedback': None  # Will be updated upon feedback
    })

# Display Recent Conversations
if st.session_state.conversation_history:
    st.subheader("Recent Conversations")
    relevance_filter = st.selectbox(
        "Filter by relevance:", ["All", "RELEVANT", "NON_RELEVANT"]
    )

    # Retrieve conversations from the database
    recent_conversations = get_recent_conversations(relevance_filter=relevance_filter)

    # Display conversations
    for convo in recent_conversations:
        st.write(f"**Question:** {convo['question']}")
        st.write(f"**Answer:** {convo['answer']}")
        st.write(f"**Feedback:** {convo.get('feedback', 'No feedback')}")
        st.write(f"**Response time:** {convo.get('processing_time', 'N/A')}")
        st.markdown("---")
