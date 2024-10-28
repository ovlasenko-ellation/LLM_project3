import pandas as pd
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import csv
import time
import logging
from tqdm import tqdm  # For the progress bar

# Set up OpenAI API key from environment variables

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Prompt template
prompt_template = """
You are an AI-Powered Skincare Chatbot. 
Your Objective: a skincare expert chatbot that answerimport pandas as pd
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import csv
import time
import logging
from tqdm import tqdm  # For the progress bar

# Set up OpenAI API key from environment variables

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Prompt template
prompt_template = """
You are an AI-Powered Skincare Chatbot.
Your Objective: a skincare expert chatbot that answers user questions about product ingredients, routines, or skin concerns, recommending products, or suggesting routines.
Formulate 5 questions a user might ask about the following skincare product, and provide relevant answers using information from the product details. The questions should be complete and not too short.

Product Details:
{product_info}

Provide the output in CSV format with two columns: question, answer.
""".strip()


def load_source_data(csv_url):
    """
    Loads the source data from the provided CSV URL.
    """
    logging.info("Loading source data from CSV URL.")
    df = pd.read_csv(csv_url)
    logging.info("Source data loaded successfully.")
    return df


def generate_ground_truth(df):
    """
    Generates ground truth data by creating question-answer pairs for each product.
    """
    logging.info("Starting to generate ground truth data.")
    ground_truth = []

    # Using tqdm for a progress bar
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing products"):
        product_info = f"""
Brand Name: {row.get('brand_name', '')}
Cosmetic Name: {row.get('cosmetic_name', '')}
Price: {row.get('price', '')}
Ingredients: {row.get('ingredients', '')}
About: {row.get('about', '')}
Reviews: {row.get('reviews', '')}
Recommended: {row.get('recommended', '')}
Cosmetic Link: {row.get('cosmetic_link', '')}
""".strip()
        prompt = prompt_template.format(product_info=product_info)

        # Call OpenAI API to generate question-answer pairs
        try:
            response = client.chat.completions.create(model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are an AI language model assistant.'},
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
            n=1)
            output = response.choices[0].message.content

            # Parse the output CSV
            reader = csv.reader(output.strip().split('\n'))
            for qa_row in reader:
                if len(qa_row) == 2:
                    question, answer = qa_row
                    ground_truth.append({'question': question.strip(), 'answer': answer.strip()})
        except Exception as e:
            logging.error(f"Error generating ground truth for product index {index}: {e}")
            time.sleep(1)  # Sleep to handle rate limits
            continue

    logging.info("Ground truth data generation completed.")
    return pd.DataFrame(ground_truth)


def save_ground_truth(df_ground_truth, output_path):
    """
    Saves the ground truth DataFrame to a CSV file in the specified directory.
    """
    logging.info(f"Saving ground truth data to {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_ground_truth.to_csv(output_path, index=False)
    logging.info(f"Ground truth data saved successfully to {output_path}")


if __name__ == "__main__":
    # Load source data
    csv_url = 'https://raw.githubusercontent.com/ovlasenko-ellation/LLM_project3/refs/heads/main/Data/Sephora_all.csv'
    df = load_source_data(csv_url)

    # Optionally, process a subset of the data for testing
    # df = df.head(10)

    # Generate ground truth
    df_ground_truth = generate_ground_truth(df)

    # Save ground truth data
    output_path = './Data/ground_truth.csv'
    save_ground_truth(df_ground_truth, output_path)
s user questions about product ingredients, routines, or skin concerns, recommending products, or suggesting routines.
Formulate 5 questions a user might ask about the following skincare product, and provide relevant answers using information from the product details. The questions should be complete and not too short.

Product Details:
{product_info}

Provide the output in CSV format with two columns: question, answer.
""".strip()


def load_source_data(csv_url):
    """
    Loads the source data from the provided CSV URL.
    """
    logging.info("Loading source data from CSV URL.")
    df = pd.read_csv(csv_url)
    logging.info("Source data loaded successfully.")
    return df


def generate_ground_truth(df):
    """
    Generates ground truth data by creating question-answer pairs for each product.
    """
    logging.info("Starting to generate ground truth data.")
    ground_truth = []

    # Using tqdm for a progress bar
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing products"):
        product_info = f"""
Brand Name: {row.get('brand_name', '')}
Cosmetic Name: {row.get('cosmetic_name', '')}
Price: {row.get('price', '')}
Ingredients: {row.get('ingredients', '')}
About: {row.get('about', '')}
Reviews: {row.get('reviews', '')}
Recommended: {row.get('recommended', '')}
Cosmetic Link: {row.get('cosmetic_link', '')}
""".strip()
        prompt = prompt_template.format(product_info=product_info)

        # Call OpenAI API to generate question-answer pairs
        try:
            response = client.chat.completions.create(model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are an AI language model assistant.'},
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
            n=1)
            output = response.choices[0].message.content

            # Parse the output CSV
            reader = csv.reader(output.strip().split('\n'))
            for qa_row in reader:
                if len(qa_row) == 2:
                    question, answer = qa_row
                    ground_truth.append({'question': question.strip(), 'answer': answer.strip()})
        except Exception as e:
            logging.error(f"Error generating ground truth for product index {index}: {e}")
            time.sleep(1)  # Sleep to handle rate limits
            continue

    logging.info("Ground truth data generation completed.")
    return pd.DataFrame(ground_truth)


def save_ground_truth(df_ground_truth, output_path):
    """
    Saves the ground truth DataFrame to a CSV file in the specified directory.
    """
    logging.info(f"Saving ground truth data to {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_ground_truth.to_csv(output_path, index=False)
    logging.info(f"Ground truth data saved successfully to {output_path}")


if __name__ == "__main__":
    # Load source data
    csv_url = 'https://raw.githubusercontent.com/ovlasenko-ellation/LLM_project3/refs/heads/main/Data/Sephora_all.csv'
    df = load_source_data(csv_url)

    # Optionally, process a subset of the data for testing
    # df = df.head(10)

    # Generate ground truth
    df_ground_truth = generate_ground_truth(df)

    # Save ground truth data
    output_path = './Data/ground_truth.csv'
    save_ground_truth(df_ground_truth, output_path)
