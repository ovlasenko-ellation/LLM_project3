# db.py
import psycopg2
from psycopg2.extras import RealDictCursor, DictCursor
import uuid
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database connection configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'my_database')
DB_USER = os.getenv('DB_USER', 'db_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'db_password')

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise e  # Re-raise the exception

def create_tables():
    """
    Generates tables for conversations and feedback.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        create_conversations_query = """
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                model_used TEXT NOT NULL,
                response_time FLOAT NOT NULL,
                relevance TEXT NOT NULL,
                total_tokens INTEGER NOT NULL,
                openai_cost FLOAT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """
        create_feedback_query = """
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id SERIAL PRIMARY KEY,
            conversation_id TEXT REFERENCES conversations(conversation_id),
            feedback VARCHAR(20) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_conversations_query)
        cursor.execute(create_feedback_query)
        conn.commit()
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        conn.rollback()
        raise e  # Re-raise the exception
    finally:
        cursor.close()
        conn.close()

def generate_conversation_id():
    """
    Generates a unique UUID for each conversation.
    """
    return str(uuid.uuid4())

def save_conversation(conversation_id, question, answer_data):
    """
    Saves the question and answer to the conversations table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now()
    try:
        insert_query = """
        INSERT INTO conversations 
        (conversation_id, question, answer, model_used, response_time, relevance, 
         total_tokens, openai_cost, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query,
                       (
                           conversation_id,
                           question,
                           answer_data.get("answer", ""),
                           answer_data.get("model_used", "Unknown"),
                           float(answer_data.get("response_time", 0.0)),
                           str(answer_data.get("relevance", "N/A")),
                           int(answer_data.get("total_tokens", 0)),
                           float(answer_data.get("openai_cost", 0.0)),
                           timestamp,
                       ),
                   )
        conn.commit()
        logging.info(f"Conversation {conversation_id} saved successfully.")
    except Exception as e:
        logging.error(f"Error saving conversation: {e}")
        conn.rollback()
        raise e  # Re-raise the exception
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
        logging.info(f"Feedback for conversation {conversation_id} saved successfully.")
    except Exception as e:
        logging.error(f"Error saving feedback: {e}")
        conn.rollback()
        raise e  # Re-raise the exception
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
            # Use INNER JOIN to only get conversations with feedback
            select_query = """
            SELECT c.*, f.feedback
            FROM conversations c
            INNER JOIN feedback f ON c.conversation_id = f.conversation_id
            WHERE f.feedback = %s
            ORDER BY c.timestamp DESC
            LIMIT %s
            """
            cursor.execute(select_query, (relevance_filter, limit))
        else:
            select_query = """
            SELECT c.*, f.feedback
            FROM conversations c
            LEFT JOIN feedback f ON c.conversation_id = f.conversation_id
            ORDER BY c.timestamp DESC
            LIMIT %s
            """
            cursor.execute(select_query, (limit,))
        conversations = cursor.fetchall()
        return conversations
    except Exception as e:
        logging.error(f"Error retrieving conversations: {e}")
        raise e  # Re-raise the exception
    finally:
        cursor.close()
        conn.close()

def get_feedback_stats():
    """
    Retrieves feedback statistics.
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                    SELECT 
                        COALESCE(SUM(CASE WHEN feedback = 'RELEVANT' THEN 1 ELSE 0 END), 0) as thumbs_up,
                        COALESCE(SUM(CASE WHEN feedback = 'NON_RELEVANT' THEN 1 ELSE 0 END), 0) as thumbs_down
                    FROM feedback
                """)
            stats = cur.fetchone()
            return stats
    except Exception as e:
        logging.error(f"Error retrieving feedback statistics: {e}")
        raise e  # Re-raise the exception
    finally:
        conn.close()
