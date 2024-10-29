import pandas as pd
import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from rag import (
    get_user_question,
    search_es,
    create_context,
    build_prompt,
    llm
)  # Import functions directly from rag.py
import os
import logging
from sentence_transformers import SentenceTransformer

# Set up OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model_name = 'all-MiniLM-L6-v2'  # or any other compatible model
embedding_model = SentenceTransformer(model_name)

def load_ground_truth_data(url, num_rows=1000):
    """
    Load the ground truth data and get the first num_rows.
    """
    df = pd.read_csv(url).head(num_rows)
    return df


def compute_cosine_similarity(v1, v2):
    """
    Compute cosine similarity between two vectors.
    """
    v1, v2 = np.array(v1).reshape(1, -1), np.array(v2).reshape(1, -1)
    return cosine_similarity(v1, v2)[0][0]


def hit_rate(relevance_total):
    """
    Calculate the Hit Rate given relevance data.
    """
    cnt = 0
    for line in relevance_total:
        if True in line:
            cnt += 1
    return cnt / len(relevance_total) if relevance_total else 0


def mrr(relevance_total):
    """
    Calculate Mean Reciprocal Rank (MRR) given relevance data.
    """
    total_score = 0.0
    for line in relevance_total:
        for rank, is_relevant in enumerate(line):
            if is_relevant:
                total_score += 1 / (rank + 1)
                break  # Stop after finding the first relevant answer
    return total_score / len(relevance_total) if relevance_total else 0


def evaluate_llm_against_ground_truth(df):
    """
    Evaluate the LLM against ground truth data based on a single user question.
    """

    v_llm = []
    v_orig = []
    relevance_total = []
    cosine_similarities = []

    for idx, row in df.iterrows():
        question = row['question']
        question_embedding = embedding_model.encode(question).tolist()
        logging.info(f"Generated embedding for the question : {question_embedding}")

        # Elasticsearch retrieval and context creation based on the single question embedding
        hits = search_es(question_embedding)
        context = create_context(hits)

        # Construct the prompt using the retrieved context and the actual user question
        prompt = build_prompt(question, context)
        llm_answer = llm(prompt)[0]  # Call LLM to get an answer based on the single question

        # Embedding for LLM answer, which will be compared to each ground truth answer
        v_llm_embedding = embedding_model.encode(llm_answer).tolist()

        ground_truth_answer = row['answer']

        # Generate embedding for the ground truth answer
        v_orig_embedding = embedding_model.encode(ground_truth_answer).tolist()

        # Store answers for similarity comparisons
        v_llm.append(llm_answer)
        v_orig.append(ground_truth_answer)

        # Calculate cosine similarity between LLM and ground truth answer
        similarity_score = compute_cosine_similarity(v_llm_embedding, v_orig_embedding)
        cosine_similarities.append(similarity_score)

        # Determine relevance (similarity > threshold implies relevance)
        is_relevant = similarity_score > 0.5  # Define a relevance threshold
        relevance_total.append([is_relevant])

    # Compute MRR and Hit Rate
    mrr_score = mrr(relevance_total)
    hit_rate_score = hit_rate(relevance_total)

    print(f"MRR Score: {mrr_score}")
    print(f"Hit Rate: {hit_rate_score}")
    return v_llm, v_orig, mrr_score, hit_rate_score, cosine_similarities


if __name__ == "__main__":
    # Load ground truth data
    ground_truth_url = "https://raw.githubusercontent.com/ovlasenko-ellation/LLM_project3/refs/heads/main/Data/ground_truth.csv"
    df_ground_truth = load_ground_truth_data(ground_truth_url)

    # Evaluate LLM and print results
    v_llm, v_orig, mrr_score, hit_rate_score, cosine_similarities = evaluate_llm_against_ground_truth(df_ground_truth)

    # Display cosine similarities for verification
    print("Cosine Similarities between LLM answers and ground truth:", cosine_similarities)
