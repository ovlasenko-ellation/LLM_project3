import streamlit as st
import time
import os
import pandas as pd
from rag import (
    get_answer,  # Function to get the answer from the LLM
    # Ensure that get_answer returns a dictionary with keys:
    # 'answer', 'response_time', 'relevance', 'model_used', 'total_tokens', 'openai_cost'
)
from db import (
    generate_conversation_id,
    save_conversation,
    save_feedback,
    get_recent_conversations
)

# Initialize session state for feedback and conversation history
if 'feedback_history' not in st.session_state:
    st.session_state['feedback_history'] = []
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
        # Call the get_answer function from rag.py
        answer_data = get_answer(user_input)
        end_time = time.time()
        processing_time = end_time - start_time

    # Save the conversation to the database
    save_conversation(conversation_id, user_input, answer_data["answer"])

    # Display the answer
    st.subheader("Answer:")
    st.write(answer_data["answer"])

    # Display logs and monitoring information
    st.subheader("Monitoring Information")
    st.write(f"Response time: {processing_time:.2f} seconds")
    st.write(f"Relevance: {answer_data.get('relevance', 'N/A')}")
    st.write(f"Total tokens: {answer_data.get('total_tokens', 'N/A')}")

    # Append to conversation history
    st.session_state.conversation_history.append({
        'question': user_input,
        'answer': answer_data["answer"],
        'relevance': answer_data.get('relevance', 'N/A'),
        'processing_time': processing_time
    })

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

# Display Feedback Stats
if st.session_state.feedback_history:
    st.subheader("Feedback Statistics")
    total_feedback = len(st.session_state.feedback_history)
    positive_feedback = st.session_state.feedback_history.count(1)
    negative_feedback = st.session_state.feedback_history.count(-1)
    st.write(f"Total feedback received: {total_feedback}")
    st.write(f"Positive feedback: {positive_feedback}")
    st.write(f"Negative feedback: {negative_feedback}")

# Display Recent Conversations
if st.button("Refresh Conversations"):
    st.session_state.conversation_history = get_recent_conversations()

if st.session_state.conversation_history:
    st.subheader("Recent Conversations")
    relevance_filter = st.selectbox(
        "Filter by relevance:", ["All", "RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]
    )

    # Filter conversations based on relevance
    if relevance_filter != "All":
        filtered_conversations = [
            convo for convo in st.session_state.conversation_history
            if convo['feedback'] == relevance_filter
        ]
    else:
        filtered_conversations = st.session_state.conversation_history

    # Display conversations
    for convo in filtered_conversations:
        st.write(f"**Question:** {convo['question']}")
        st.write(f"**Answer:** {convo['answer']}")
        st.write(f"**Feedback:** {convo.get('feedback', 'No feedback')}")
        st.write(f"**Response time:** {convo.get('processing_time', 'N/A')}")
        st.markdown("---")
