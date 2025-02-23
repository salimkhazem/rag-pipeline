import os
import sys
import pdfplumber
from rag_pipeline import RAGPipeline

sys.path.append(".")

# Initialize the pipeline with your Azure OpenAI credentials
pipeline = RAGPipeline(
    api_key="your_api_key",
    azure_endpoint="Your_endpoint",
    api_version="your_api_version",
    embedding_deployment="text-embedding-ada-002",
    completion_deployment="gpt-4o-mini",
)


# Function to load documents from files (supports .txt and .pdf)
def load_documents_from_directory(directory):
    documents = []
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist. Creating it.")
        os.makedirs(directory)
        return documents

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            continue
        try:
            if filename.endswith(".txt"):
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                    if text:
                        documents.append({"text": text, "filename": filename})
                        print(f"Loaded text file: {filename}")
            elif filename.endswith(".pdf"):
                with pdfplumber.open(filepath) as pdf:
                    text = "".join(
                        page.extract_text() or "" for page in pdf.pages
                    ).strip()
                    if text:
                        documents.append({"text": text, "filename": filename})
                        print(f"Loaded PDF file: {filename}")
        except Exception as e:
            print(f"Error loading {filename}: {str(e)}")
    return documents


# Main test function
def run_test():
    # Check for directory argument
    if len(sys.argv) < 2:
        print("Usage: python test_summarize.py <directory_path>")
        sys.exit(1)

    test_directory = sys.argv[1]
    documents = load_documents_from_directory(test_directory)

    if not documents:
        print(
            f"No valid documents found in \ 
        '{test_directory}'. Please add some .txt or .pdf files."
        )
        return

    print(f"Loaded {len(documents)} document(s) for summarization.")

    # Summarize each document
    print("\nGenerating summaries:")
    for doc in documents:
        try:
            summary = pipeline.summarize(
                doc["text"], max_length=50
            )  # Adjust max_length as needed
            print(f"\nFile: {doc['filename']}")
            print(f"Summary: {summary}")
        except Exception as e:
            print(f"Error summarizing {doc['filename']}: {str(e)}")


# Run the test
if __name__ == "__main__":
    print("Starting RAG pipeline summarization test...")
    run_test()
    print("Test completed!")
