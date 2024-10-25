import pandas as pd
import hashlib
from elasticsearch import Elasticsearch, ConnectionError, TransportError
from elasticsearch.helpers import bulk
from sentence_transformers import SentenceTransformer
import json

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")
index_name = "cosmetics_index"

# Check Elasticsearch connection
try:
    if not es.ping():
        print("Cannot connect to Elasticsearch. Check if the service is running.")
except ConnectionError as e:
    print(f"Elasticsearch connection error: {e}")
    exit()

# Load a pre-trained embedding model to be globally accessible
model_name = 'all-MiniLM-L6-v2'
embedding_model = SentenceTransformer(model_name)


def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        print("Data loaded successfully.")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on failure


def generate_hashed_id(row):
    """Generate a unique hash ID based on the row data."""
    try:
        row_str = str(row.to_dict())
        return hashlib.md5(row_str.encode()).hexdigest()
    except Exception as e:
        print(f"Error generating hash ID: {e}")
        return None


def concatenate_columns(row):
    """Concatenate text columns into a single string."""
    columns_to_concat = [
        'cosmetic_link', 'brand_name', 'cosmetic_name', 'num_customer',
        'price', 'ingredients', 'about', 'reviews', 'recommended'
    ]
    try:
        return ' '.join(str(row[col]) for col in columns_to_concat if pd.notnull(row[col]))
    except KeyError as e:
        print(f"Missing column for concatenation: {e}")
        return ''


def create_elasticsearch_index(es_client, index_name):
    """Create index in Elasticsearch with settings for text and vector fields."""
    index_body = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "text": {"type": "text"},
                "embedding": {"type": "dense_vector", "dims": 384}
            }
        }
    }
    try:
        if not es_client.indices.exists(index=index_name):
            es_client.indices.create(index=index_name, body=index_body)
            print(f"Index '{index_name}' created.")
        else:
            print(f"Index '{index_name}' already exists.")
    except TransportError as e:
        print(f"Error creating index: {e}")


def generate_embedding(text):
    """Generate vector embedding using SentenceTransformer."""
    if not text:
        print("Warning: No text provided for embedding.")
        return [0.0] * 384  # Return a zero vector if no text is provided

    try:
        # Generate embedding
        embedding = embedding_model.encode(text).tolist()
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return [0.0] * 384  # Return zero vector in case of error


def transform_data(df):
    """Transform the DataFrame to include hashed ID, concatenated text, and embedding."""
    try:
        df['id'] = df.apply(generate_hashed_id, axis=1)
        df['text'] = df.apply(concatenate_columns, axis=1)
        df['embedding'] = df['text'].apply(generate_embedding)
        return df
    except Exception as e:
        print(f"Error transforming data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on failure


def load_data_to_elasticsearch(es_client, df, index_name):
    """Load data into Elasticsearch."""
    if df.empty:
        print("No data to load into Elasticsearch.")
        return
    actions = [
        {
            "_index": index_name,
            "_id": row['id'],
            "_source": {
                "id": row['id'],
                "text": row['text'],
                "embedding": row['embedding']
            }
        }
        for _, row in df.iterrows() if row['id'] is not None
    ]
    try:
        bulk(es_client, actions)
        print(f"Loaded {len(actions)} documents into Elasticsearch.")
    except TransportError as e:
        print(f"Error loading data to Elasticsearch: {e}")


if __name__ == "__main__":
    # Define file path and load data
    file_path = 'https://raw.githubusercontent.com/ovlasenko-ellation/LLM_project3/refs/heads/main/Data/Sephora_all.csv'
    df = load_data(file_path)

    # Ensure data loaded successfully before continuing
    if not df.empty:
        # Transform data
        transformed_df = transform_data(df)

        # Set up Elasticsearch index
        create_elasticsearch_index(es, index_name)

        # Load transformed data to Elasticsearch
        load_data_to_elasticsearch(es, transformed_df, index_name)
    else:
        print("Data loading failed, exiting script.")
