from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import requests
from elasticsearch import Elasticsearch
import numpy as np
import logging

# Set up logging for debugging and tracking
logging.basicConfig(level=logging.INFO)

# Set your OpenAI API key securely using an environment variable
#if not openai.api_key:
#    raise ValueError("OpenAI API key not set. Please set it in your environment variables.")

# Elasticsearch client configuration
es = Elasticsearch(['http://localhost:9200'])  # Adjust the host and port as needed

def get_user_question():
    """
    Function to accept user question.
    """
    question = input("Please enter your skincare question: ")
    logging.info(f"User question: {question}")
    return question

def generate_question_embedding(question):
    """
    Generates vector embedding for the user question using OpenAI's API.
    """
    try:
        response = client.embeddings.create(input=question, model='text-embedding-ada-002')
        embedding = response.data[0].embedding
        logging.info(f"Generated embedding for the question: {embedding}")
        return embedding
    except Exception as e:
        logging.error(f"Error generating embedding: {e}")
        return None

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
        hits = response.hits.hits
        return hits
    except Exception as e:
        logging.error(f"Error searching Elasticsearch: {e}")
        return []

def create_context(hits):
    """
    Creates context by concatenating the first 5 descriptions from search results.
    """
    contexts = [hit['_source'].get('description', 'No description available') for hit in hits]
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

def llm(prompt, model_choice='gpt-3.5-turbo'):
    """
    Calls the LLM with the prompt using OpenAI's ChatCompletion API.
    """
    try:
        response = client.chat.completions.create(model=model_choice,
        messages=[{"role": "user", "content": prompt}])
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")
        return "I'm sorry, but I couldn't retrieve a response at this time."

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

def get_answer():
    """
    Gets the reply from the LLM and evaluates relevance.
    """
    question = get_user_question()
    question_embedding = generate_question_embedding(question)

    if question_embedding is None:
        print("Error generating embedding for the question. Please try again.")
        return

    # Display the embedding to the user for verification purposes
    print(f"Generated Embedding for the Question:\n{question_embedding}\n")

    hits = search_es(question_embedding)

    if not hits:
        print("No relevant information found in Elasticsearch. Please try again later.")
        return

    context = create_context(hits)
    prompt = build_prompt(question, context)
    answer = llm(prompt)

    relevance_score = evaluate_relevance(question, answer)
    if relevance_score is None:
        relevance_score = "N/A"

    print(f"Answer:\n{answer}\n")
    print(f"Relevance Score: {relevance_score}")

if __name__ == "__main__":
    get_answer()
