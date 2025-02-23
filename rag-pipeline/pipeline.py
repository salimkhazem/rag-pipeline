# rag_pipeline/pipeline.py

import openai
import numpy as np
from .vector_stores import FaissVectorStore
from .utils import split_into_passages


class RAGPipeline:
    """
    A pipeline for Retrieval-Augmented Generation using Azure OpenAI and FAISS.
    """

    def __init__(
        self,
        azure_endpoint,
        api_key,
        embedding_deployment,
        completion_deployment,
        chunk_size=500,
        overlap=50,
    ):
        """
        Initialize the RAG pipeline.

        Args:
            azure_endpoint (str): Azure OpenAI endpoint URL.
            api_key (str): Azure OpenAI API key.
            embedding_deployment (str): Name of the embedding model deployment.
            completion_deployment (str): Name of the completion model deployment.
            chunk_size (int): Size of each passage in words.
            overlap (int): Overlap between passages in words.
        """
        # Configure Azure OpenAI
        openai.api_type = "azure"
        openai.api_base = azure_endpoint
        openai.api_version = "2023-05-15"  # Adjust based on your Azure version
        openai.api_key = api_key

        self.embedding_deployment = embedding_deployment
        self.completion_deployment = completion_deployment
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.vector_store = None

    def get_embedding(self, text):
        """
        Generate an embedding for the given text using Azure OpenAI.

        Args:
            text (str): The text to embed.

        Returns:
            np.ndarray: The embedding vector.
        """
        response = openai.Embedding.create(
            input=text, engine=self.embedding_deployment)
        return np.array(response["data"][0]["embedding"])

    def index_documents(self, documents):
        """
        Index a list of documents by splitting them into passages and storing embeddings.

        Args:
            documents (list): List of document strings.
        """
        passages = []
        for doc in documents:
            doc_passages = split_into_passages(
                doc, self.chunk_size, self.overlap)
            passages.extend(doc_passages)

        embeddings = np.array([self.get_embedding(p) for p in passages])
        if self.vector_store is None:
            self.vector_store = FaissVectorStore(
                embedding_dim=embeddings.shape[1])
        self.vector_store.add(embeddings, passages)

    def query(self, question, top_k=5):
        """
        Query the pipeline with a question and get an answer.

        Args:
            question (str): The question to answer.
            top_k (int): Number of passages to retrieve.

        Returns:
            str: The generated answer.
        """
        query_embedding = self.get_embedding(question)
        retrieved_passages = self.vector_store.search(query_embedding, top_k)
        system_message = (
            "You are a helpful assistant. Use the following information to answer the question:\n\n"
            + "\n\n".join(retrieved_passages)
        )

        response = openai.ChatCompletion.create(
            engine=self.completion_deployment,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": question},
            ],
            max_tokens=150,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"]
