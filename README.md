# AI-Powered Skincare Chatbot

An intelligent chatbot that provides expert advice on skincare products, routines, and skin concerns by leveraging a knowledge base and advanced language models.

## Table of Contents

- [Problem Description](#problem-description)
- [Solution Overview](#solution-overview)
- [Retrieval-Augmented Generation (RAG) Flow](#retrieval-augmented-generation-rag-flow)
- [Retrieval Evaluation](#retrieval-evaluation)
- [RAG Evaluation](#rag-evaluation)
- [Ingestion Pipeline](#ingestion-pipeline)
- [User Interface](#user-interface)
- [Monitoring and Feedback](#monitoring-and-feedback)
- [Containerization](#containerization)
- [Reproducibility](#reproducibility)
- [Getting Started](#getting-started)
- [License](#license)

## Problem Description

Skincare can be complex and overwhelming, with countless products, ingredients, and routines available. Many individuals struggle to find reliable, personalized advice for their specific skin concerns. This project aims to solve this problem by providing an AI-powered chatbot that delivers expert skincare guidance based on a rich knowledge base and advanced language models.

## Solution Overview

The AI-Powered Skincare Chatbot combines a comprehensive knowledge base of skincare information with cutting-edge language models to deliver accurate and personalized responses to user queries. The chatbot answers questions about product ingredients, recommends routines, and addresses specific skin concerns by retrieving relevant information from the knowledge base and generating context-aware responses.

## Dataset
The dataset used in this project is the Sephora dataset [Sephora_all_423.csv](https://www.kaggle.com/datasets/autumndyer/skincare-products-and-ingredients?select=Sephora_all_423.csv) containing 2179 unique values for products, ingredients, price, recommendations, feedbacks. Dataset has been analyzed and prepared by the notebooks.

## Technologies 
- Python 3.12: The primary programming language
- Elasticsearch: for storing, indexing the dataset and vectors 
- OpenAI: used for LLM 
- Docker and Docker Compose: For containerization
- Grafana: For monitoring and visualization.
- PostgreSQL: for storing, querying and retrieving models usage data
- Streamlit: for user interface app

## Retrieval-Augmented Generation (RAG) Flow

This project utilizes a Retrieval-Augmented Generation (RAG) flow that integrates both a knowledge base and a Large Language Model (LLM):

- **Knowledge Base**: An Elasticsearch database containing curated skincare information.
- **LLM**: An advanced language model that generates responses based on the retrieved context.

## Ingestion Pipeline

An automated ingestion pipeline was developed using Python scripts to streamline the process of importing data into the Elasticsearch knowledge base:

- **Data Parsing**: Extracts and preprocesses data from source files.
- **Indexing**: Automates the indexing of documents into Elasticsearch.


## Retrieval Evaluation

Multiple retrieval approaches were evaluated to optimize the chatbot's performance:

1. **BM25 Retrieval**: Baseline retrieval using the Okapi BM25 algorithm.
2. **TF-IDF Retrieval**: Evaluated for comparison with BM25.
3. **Dense Vector Retrieval**: Implemented using embeddings for semantic search.

After thorough testing, Dense Vector Retrieval was selected for its superior ability to capture semantic relationships and provide the most relevant context to the LLM.

## RAG Evaluation

Various RAG approaches were tested to enhance the quality of the chatbot's responses:

1. **Prompt Engineering**: Experimented with different prompt structures to guide the LLM effectively.
2. **Context Window Sizes**: Adjusted the amount of context provided to the LLM for optimal performance.
3. **Response Refinement**: Implemented iterative generation and refinement techniques.

The best-performing approach combined an optimized prompt with an ideal context window size, resulting in accurate and concise answers.



## User Interface

The chatbot features an interactive web interface built with Streamlit:

- **User-Friendly Design**: Intuitive layout for easy interaction.
- **Real-Time Responses**: Provides immediate answers to user queries.
- **Feedback Mechanism**: Allows users to rate responses for continuous improvement.

## Monitoring and Feedback

To ensure the chatbot's effectiveness and facilitate continuous improvement, monitoring and feedback mechanisms are in place:

- **User Feedback Collection**: Users can indicate the relevance of responses.
- **Monitoring Dashboard**: A comprehensive dashboard with over five charts displays metrics such as:

  - **User Engagement**: Number of queries over time.
  - **Response Accuracy**: Percentage of relevant feedback.
  - **Popular Topics**: Frequently asked questions or concerns.
  - **System Performance**: Response times and uptime.
  - **Error Tracking**: Logs and alerts for any issues.

## Containerization

The entire application and its dependencies are containerized using Docker Compose:

- **Docker Compose Configuration**: All services, including the Streamlit app, Elasticsearch, and monitoring tools, are defined in a single `docker-compose.yml` file.
- **Isolation and Portability**: Ensures consistent environments across different systems.
- **Easy Deployment**: Simplifies the setup process for development and production.

## Reproducibility

The project is designed for easy reproducibility:

- **Clear Instructions**: Step-by-step guide provided in the [Getting Started](#getting-started) section.
- **Accessible Dataset**: Instructions on how to access and prepare the dataset.
- **Dependency Management**: All dependencies are specified with exact versions in `requirements.txt`.
- **Automated Setup**: Scripts automate environment setup and data ingestion.

## Getting Started

Follow these instructions to set up and run the AI-Powered Skincare Chatbot on your local machine.

### Prerequisites

- **Docker and Docker Compose**: Ensure that Docker and Docker Compose are installed.
- **Git**: To clone the repository.

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/ovlasenko-ellation/LLM_project3.git
   cd LLM_project3
    ```
2. **Access the Dataset**
3. **Build and Run the Containers**
4. **Initialize the Knowledge Base**
5. **Access the Application**