import os
import sys
import pdfplumber
from rag_pipeline import RAGPipeline

sys.path.append(".")


# Function to load documents from files (supports .txt and .pdf)
def load_documents_from_directory(directory):
    documents = []
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist. Creating it.")
        os.makedirs(directory)
        return documents  # Return empty list if directory didn't exist

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            continue  # Skip directories or non-files

        try:
            if filename.endswith(".txt"):
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                    if text:  # Only add non-empty documents
                        documents.append({"text": text})
                        print(f"Loaded text file: {filename}")

            elif filename.endswith(".pdf"):
                with pdfplumber.open(filepath) as pdf:
                    text = "".join(
                        page.extract_text() or "" for page in pdf.pages
                    ).strip()
                    if text:  # Only add non-empty documents
                        documents.append({"text": text})
                        print(f"Loaded PDF file: {filename}")

        except Exception as e:
            print(f"Error during indexing: {str(e)}")
    return documents


pipeline = RAGPipeline(
    azure_endpoint="your_azure_endpoint",
    api_key="your_api_key",
    api_version="your_api_version",
    embedding_deployment="text-embedding-ada-002",
    completion_deployment="gpt-4o-mini",
)


# Main test function
def run_test():
    # Directory containing test files
    test_directory = sys.argv[1]

    # Load documents
    documents = load_documents_from_directory(test_directory)

    # Check if any documents were loaded
    if not documents:
        print(f"No valid documents found in '{test_directory}'. Please add some .txt or .pdf files.")
        return

    print(f"Loaded {len(documents)} document(s) for indexing.")

    # Index the documents
    try:
        pipeline.index_documents(documents)
        print("Indexing completed successfully!")
    except Exception as e:
        print(f"Error during indexing: {str(e)}")


# Run the test
if __name__ == "__main__":
    print("Starting RAG pipeline test...")
    run_test()
    print("Test completed!")
