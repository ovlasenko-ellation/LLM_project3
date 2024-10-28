import pandas as pd
import numpy as np
import os
import openai
from tqdm import tqdm
from rag import generate_question_embedding, search_es, create_context, build_prompt, llm

# Set your OpenAI API key

# Define the prompt template (ensure it matches the one used in your RAG script)
prompt_template = """
You are an assistant for skincare products and skincare routine - AI-Powered Skincare Chatbot. You are a skincare expert chatbot that answers user questions about product ingredients, routines, or skin concerns.
Answer the user QUESTION based on the CONTEXT from the ElasticSearch database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
""".strip()

def load_ground_truth(ground_truth_path):
    """
    Loads the ground truth data from the CSV file.
    """
    df = pd.read_csv(ground_truth_path)
    return df

def hit_rate(relevance_total):
    cnt = 0

    for line in relevance_total:
        if True in line:
            cnt += 1

    return cnt / len(relevance_total)

def mrr(relevance_total):
    total_score = 0.0

    for line in relevance_total:
        for rank in range(len(line)):
            if line[rank]:
                total_score += 1 / (rank + 1)
                break  # Only consider the first relevant document per query

    return total_score / len(relevance_total)

def evaluate_model(df_ground_truth):
    """
    Evaluates the model using MRR and Hit Rate metrics.
    """
    relevance_total = []  # List of lists of relevance per query

    for index, row in tqdm(df_ground_truth.iterrows(), total=df_ground_truth.shape[0], desc="Evaluating"):
        question = row['question']
        ground_truth_answer = row['answer']

        # Generate embedding for the question
        question_embedding = generate_question_embedding(question)

        # Search in ElasticSearch to get the top k documents
        hits = search_es(question_embedding, k=5)

        # Collect relevance judgments for the retrieved documents
        relevance_per_query = []

        for hit in hits:
            # Assuming the document content is in 'about' or 'description' field
            document_text = hit['_source'].get('about', '') + " " + hit['_source'].get('description', '')
            # Check if the ground truth answer is present in the document
            if ground_truth_answer.lower() in document_text.lower():
                relevance_per_query.append(True)
            else:
                relevance_per_query.append(False)

        relevance_total.append(relevance_per_query)

    # Compute MRR and Hit Rate
    mrr_score = mrr(relevance_total)
    hit_rate_score = hit_rate(relevance_total)

    return mrr_score, hit_rate_score

if __name__ == "__main__":
    # Load ground truth data
    ground_truth_path = '../Data/ground_truth.csv'
    df_ground_truth = load_ground_truth(ground_truth_path)

    # Evaluate the model
    mrr_score, hit_rate_score = evaluate_model(df_ground_truth)

    print(f"Mean Reciprocal Rank (MRR): {mrr_score}")
    print(f"Hit Rate: {hit_rate_score}")
