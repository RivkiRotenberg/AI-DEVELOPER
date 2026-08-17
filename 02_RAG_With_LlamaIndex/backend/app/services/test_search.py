import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

current_file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_file_dir, "../../../"))
load_dotenv(dotenv_path=os.path.join(project_root, ".env"))

def test_pinecone_retrieval():
    print("🔄 טוען את מודל ה-Embedding של Cohere...")
    embed_model = CohereEmbedding(
        model_name="embed-multilingual-v3.0",
        api_key=os.getenv("COHERE_API_KEY")
    )
    
    print("🔄 מתחבר ל-Pinecone לשליפת מידע...")
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    pinecone_index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    
    # טעינת האינדקס ישירות מתוך ה-Vector Store בענן
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)
    
    retriever = index.as_retriever(similarity_top_k=2)
    
    search_query = "agent" 
    print(f"\n🔍 מריץ חיפוש סמנטי בענן עבור: '{search_query}'...")
    results = retriever.retrieve(search_query)
    
    print(f"✅ נמצאו {len(results)} מקטעים רלוונטיים מ-Pinecone:")
    for i, match in enumerate(results, 1):
        print(f"\n--- תוצאה {i} (ציון התאמה: {match.score:.4f}) ---")
        print(f"מקור (Metadata): {match.node.metadata.get('file_name')}")
        print(f"פרויקט (Metadata): {match.node.metadata.get('project_part')}")
        print(f"תוכן: {match.node.get_content()[:150]}...")

if __name__ == "__main__":
    test_pinecone_retrieval()