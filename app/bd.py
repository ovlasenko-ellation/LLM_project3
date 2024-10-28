import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import os

# Database connection configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'skincare_chatbot')
DB_USER = os.getenv('DB_USER', 'your_db_username')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_db_password')

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def generate_conversation_id():
    """
    Generates a unique UUID for each conversation.
    """
    return str(uuid.uuid4())

def save_conversation(conversation_id, question, answer):
    """
    Saves the question and answer to the conversations table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        insert_query = """
        INSERT INTO conversations (conversation_id, question, answer)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (conversation_id, question, answer))
        conn.commit()
    except Exception as e:
        print(f"Error saving conversation: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def save_feedback(conversation_id, feedback):
    """
    Saves the user feedback to the feedback table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        insert_query = """
        INSERT INTO feedback (conversation_id, feedback)
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (conversation_id, feedback))
        conn.commit()
    except Exception as e:
        print(f"Error saving feedback: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_recent_conversations(limit=10, relevance_filter=None):
    """
    Retrieves recent conversations with an optional relevance filter.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if relevance_filter and relevance_filter != "All":
            select_query = """
            SELECT c.*, f.feedback
            FROM conversations c
            LEFT JOIN feedback f ON c.conversation_id = f.conversation_id
            WHERE f.feedback = %s
            ORDER BY c.created_at DESC
            LIMIT %s
            """
            cursor.execute(select_query, (relevance_filter, limit))
        else:
            select_query = """
            SELECT c.*, f.feedback
            FROM conversations c
            LEFT JOIN feedback f ON c.conversation_id = f.conversation_id
            ORDER BY c.created_at DESC
            LIMIT %s
            """
            cursor.execute(select_query, (limit,))
        conversations = cursor.fetchall()
        return conversations
    except Exception as e:
        print(f"Error retrieving conversations: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
