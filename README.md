# AI-Powered Skincare Chatbot

An intelligent chatbot that provides expert advice on skincare products, routines, and skin concerns by leveraging a knowledge base and advanced language models.

## Table of Contents

- [Problem Description](#problem-description)
- [Solution Overview](#solution-overview)
- [Dataset](#dataset)
- [Technologies](#technologies-)
- [Retrieval-Augmented Generation (RAG) Flow](#retrieval-augmented-generation-rag-flow)
- [Ingestion Pipeline](#ingestion-pipeline)
- [Retrieval Evaluation](#retrieval-evaluation)
- [RAG Evaluation](#rag-evaluation)
- [User Interface](#user-interface)
- [Monitoring and Feedback](#monitoring-and-feedback)
- [Containerization](#containerization)
- [Reproducibility](#reproducibility)
- [Getting Started](#getting-started)

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
- **Ground Truth Dataset**: A dataset used for RAG evaluation
- **LLM evaluation**: A script having RAG evaluation metrics - MRR, hit rate, cosine similarity

## Ingestion Pipeline

An automated ingestion pipeline was developed using Python scripts to streamline the process of importing data into the Elasticsearch knowledge base:

- **Data Parsing**: Extracts and preprocesses data from source files, transforms source data and adds vector embeddings
- **Indexing**: Automates the indexing of documents into Elasticsearch.

Data ingestion is done by the [data_preprocessing.py](https://github.com/ovlasenko-ellation/LLM_project3/blob/main/Scripts/data_preprocessing.py)

## Retrieval Evaluation

The created RAG model is operating using the script [rag.py](https://github.com/ovlasenko-ellation/LLM_project3/blob/main/Scripts/rag.py) that contains:
- getting user question 
- providing embedding for the user question 
- searching in Elasticsearch using vector
- building context and promt
- actual Skincare LLM
- evaluation using cosine similarity 
- calculation of openAI cost
- returning answer with various parameters from openAI and created LLM 

Retrieval evaluation is done using cosine similarity method.

## RAG Evaluation

For RAG retrieval evaluation Ground truth dataset was created using the script [generate_ground_truth.py](https://github.com/ovlasenko-ellation/LLM_project3/blob/main/Scripts/generate_ground_truth.py)
Based on ground truth data the following metrics were calculated for evaluation:
- MRR
- Hit Rate
- Cosine Similarity

## User Interface

The chatbot features an interactive web interface built with Streamlit:

- **User-Friendly Design**: Contains forms for user question, ask button, feedback buttons, recent conversaiton filter and feedback stats.
- **Real-Time Responses**: Provides immediate answers to user queries.
- **Feedback Mechanism**: Allows users to rate responses for continuous improvement.

## Monitoring and Feedback

To ensure the chatbot's effectiveness and facilitate continuous improvement, monitoring and feedback mechanisms are in place:

- **User Feedback Collection**: Users can indicate the relevance of responses.
- **Grafana Dashboard**: A comprehensive dashboard with 6 charts displays metrics such as:

  - **Response Time**: Response time for each conversation within the selected time range
  - **Relevance Distribution**: Number of conversations for each relevance type within the selected time range.
  - **Token Usage**: Average token usage over time, grouped by Grafana's automatically calculated interval.
  - **OpenAI Cost**: Total OpenAI cost over time
  - **Recent Conversations**: 5 most recent conversations within the selected time range.
  - **Feedback Statistics**: Total number of positive and negative feedback within the selected time range

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
2. **Build and Run the Containers**
Run the command to build the containers for the whole Architecture
   ```bash
   docker-compose up --build
   ```
3. **Start Ingestion pipeline and Initialize the Knowledgebase**
Dataset needs to be loaded to ElasticSearch, for this run the script
   ```bash
   python Scripts/data_processing.py
    ```
4. **Initialize the Data Base**
In order to get the tables created in Postgres run the command 
   ```bash
   python app/db_prep.py
   ```
5. **Access the Application**
Open your web browser and navigate to http://localhost:8501 to interact with the chatbot

6. **Monitor in Grafana**
Access the monitoring dashboard at http://localhost:3000.
Import the [dashboard.json](https://github.com/ovlasenko-ellation/LLM_project3/blob/main/Grafana/dashboard.json)

![dashboard1](https://github.com/ovlasenko-ellation/LLM_project3/blob/main/Grafana/dashboard1.png)
more pictures
![dashboard2](https://github.com/ovlasenko-ellation/LLM_project3/blob/main/Grafana/dasboard2.png)