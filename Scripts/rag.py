from openai import OpenAI
from sentence_transformers import SentenceTransformer
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from elasticsearch import Elasticsearch
import numpy as np
import logging
import time

# Set up logging for debugging and tracking
logging.basicConfig(level=logging.INFO)

# Set your OpenAI API key securely using an environment variable
#if not openai.api_key:
#    raise ValueError("OpenAI API key not set. Please set it in your environment variables.")

# Elasticsearch client configuration
es = Elasticsearch(['http://localhost:9200'])  # Adjust the host and port as needed

# Load the SentenceTransformer model globally
model_name = 'all-MiniLM-L6-v2'  # or any other compatible model
embedding_model = SentenceTransformer(model_name)

def get_user_question():
    """
    Function to accept user question.
    """
    question = input("Please enter your skincare question: ")
    logging.info(f"User question: {question}")
    return question

def generate_question_embedding(question):
    """
    Generates vector embedding for the user question using SentenceTransformer.
    """
    if not question:
        logging.warning("Warning: No question provided for embedding.")
        return [0.0] * 384  # Return a zero vector if no question is provided

    try:
        # Generate embedding using the SentenceTransformer model
        embedding = embedding_model.encode(question).tolist()
        logging.info(f"Generated embedding for the question: {embedding}")
        return embedding
    except Exception as e:
        logging.error(f"Error generating embedding: {e}")
        return [0.0] * 384  # Return a zero vector in case of an error

def search_es(embedding, index_name='cosmetics_index', k=5):
    """
    Searches in Elasticsearch for the closest elements using vector similarity.
    """
    query = {
       "size": k,
       "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": embedding}
                }
            }
        }
    }
    print(len(embedding))
    try:
        response = es.search(index=index_name, body=query)
        hits = response['hits']['hits']
        print(hits)
        return hits
    except Exception as e:
        logging.error(f"Error searching Elasticsearch: {e}")
        return []

def create_context(hits):
    """
    Creates context by concatenating the first 5 descriptions from search results.
    """
    contexts = [hit['_source'].get('text', 'No description available') for hit in hits]
    context = "\n\n".join(contexts)
    return context

def build_prompt(question, context):
    """
    Creates a prompt for the LLM using the context and question.
    """
    # Prompt template
    prompt_template = """
    You are an assistant for skincare products and skincare routine - AI-Powered Skincare Chatbot. You are a skincare expert chatbot that answers user questions about product ingredients, routines, or skin concerns.
    Answer the user QUESTION based on the CONTEXT from the ElasticSearch database.
    Use only the facts from the CONTEXT when answering the QUESTION.

    QUESTION: {question}

    CONTEXT:
    {context}
    """.strip()
    prompt = prompt_template.format(question=question, context=context)
    return prompt

def llm(prompt, model_choice='gpt-4o-mini'):
    """
    Calls the LLM with the prompt using OpenAI's ChatCompletion API.
    """
    print(100*'-')
    print(prompt)
    print(100 * '-')
    try:
        response = client.chat.completions.create(model=model_choice,
        messages=[{"role": "user", "content": prompt}])
        answer = response.choices[0].message.content
        # Get token usage
        usage = response.usage
        total_tokens = response.usage.total_tokens
        # Calculate OpenAI cost
        openai_cost = calculate_openai_cost(usage, model_choice)
        return answer, model_choice, total_tokens, openai_cost
    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")
        return "I'm sorry, but I couldn't retrieve a response at this time."


def calculate_openai_cost(usage, model_choice):
    """
    Calculates the cost of the OpenAI API call based on the model used and tokens consumed.
    """
    # Pricing as of September 2023 (update with current pricing)
    if model_choice == 'gpt-4o-mini':
        # $0.000150 per 1K input tokens (prompt)
        # $0.000600 per 1K output tokens (completion)
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        prompt_cost = (prompt_tokens / 1000) * 0.000150
        completion_cost = (completion_tokens / 1000) * 0.000600
        total_cost = prompt_cost + completion_cost
    else:
        total_cost = 0.0
    return total_cost


def evaluate_relevance(question, answer):
    """
    Evaluates the relevance of the response using cosine similarity.
    """
    question_embedding = generate_question_embedding(question)
    answer_embedding = generate_question_embedding(answer)

    # Check if embeddings are valid
    if question_embedding is None or answer_embedding is None:
        logging.error("Error generating embeddings for relevance evaluation.")
        return None

    norm_q = np.linalg.norm(question_embedding)
    norm_a = np.linalg.norm(answer_embedding)

    # Avoid division by zero
    if norm_q == 0 or norm_a == 0:
        logging.error("One of the embeddings is a zero vector.")
        return None

    cosine_similarity = np.dot(question_embedding, answer_embedding) / (norm_q * norm_a)
    return cosine_similarity

def get_answer(question):
    """
    Gets the reply from the LLM and evaluates relevance.
    Accepts a user's question and returns a dictionary with the answer and monitoring information.
    """
    start_time = time.time()
    answer_data = {}
    try:
        # Generate embedding for the question
        question_embedding = generate_question_embedding(question)

        if question_embedding is None:
            error_msg = "Error generating embedding for the question. Please try again."
            print(error_msg)
            answer_data = {
                'answer': error_msg,
                'response_time': time.time() - start_time,
                'relevance': "N/A",
                'model_used': "N/A",
                'total_tokens': 0,
                'openai_cost': 0.0
            }
            return answer_data

        # Search in ElasticSearch to get the top k documents
        hits = search_es(question_embedding)

        if not hits:
            error_msg = "No relevant information found in Elasticsearch. Please try again later."
            print(error_msg)
            answer_data = {
                'answer': error_msg,
                'response_time': time.time() - start_time,
                'relevance': "N/A",
                'model_used': "N/A",
                'total_tokens': 0,
                'openai_cost': 0.0
            }
            return answer_data

        # Create context from the retrieved documents
        context = create_context(hits)

        # Build the prompt
        prompt = build_prompt(question, context)

        # Get the LLM's answer and additional info
        answer, model_used, total_tokens, openai_cost = llm(prompt)

        # Evaluate the relevance of the answer
        relevance_score = evaluate_relevance(question, answer)
        if relevance_score is None:
            relevance_score = "N/A"

        # Calculate response time
        response_time = time.time() - start_time

        # Prepare the answer data dictionary
        answer_data = {
            'answer': answer,
            'response_time': response_time,
            'relevance': relevance_score,
            'model_used': model_used,
            'total_tokens': total_tokens,
            'openai_cost': openai_cost
        }

        return answer_data

    except Exception as e:
        print(f"An error occurred: {e}")
        answer_data = {
            'answer': f"An error occurred: {e}",
            'response_time': time.time() - start_time,
            'relevance': "N/A",
            'model_used': "N/A",
            'total_tokens': 0,
            'openai_cost': 0.0
        }
        return answer_data


if __name__ == "__main__":
    question = get_user_question()
    answer_data = get_answer(question)
    print(f"Answer: {answer_data['answer']}")
    print(f"Relevance: {answer_data['relevance']}")
    print(f"Response Time: {answer_data['response_time']:.2f} seconds")
    print(f"Model Used: {answer_data['model_used']}")
    print(f"Total Tokens: {answer_data['total_tokens']}")
    if answer_data['openai_cost'] > 0:
        print(f"OpenAI Cost: ${answer_data['openai_cost']:.4f}")
