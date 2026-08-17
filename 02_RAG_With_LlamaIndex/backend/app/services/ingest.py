import os
from dotenv import load_dotenv  
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone


# מציאת נתיב תיקיית השורש של הפרויקט
current_file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_file_dir, "../../../"))
load_dotenv(dotenv_path=os.path.join(project_root, ".env"))

def load_parse_and_index_documents():
    # --- שלב 1: טעינה ---
    print("🤖 שלב 1: טעינת מסמכים...")
    target_dir = os.path.join(project_root, "agent_docs")
    reader = SimpleDirectoryReader(input_dir=target_dir, recursive=True, required_exts=[".md"])
    documents = reader.load_data()
    print(f"✅ נטענו {len(documents)} מסמכים.")

    # --- שלב 2: פיצול (Chunking) והוספת מטא-דאטה ---
    print("\n🤖 שלב 2: חלוקת המסמכים למקטעים...")
    parser = MarkdownNodeParser()
    nodes = parser.get_nodes_from_documents(documents)
    
    # LlamaIndex אוספת אוטומטית מטא-דאטה בסיסי (כמו file_name).
    # אם תרצי להוסיף הקשרים מותאמים אישית לכל Node:
    for node in nodes:
        # דוגמה להוספת מטא-דאטה מותאם אישית במידת הצורך
        node.metadata["project_part"] = "AI-Developer-Agent"
        
    print(f"✅ נוצרו {len(nodes)} מקטעים (Nodes) עם Metadata מועשר.")

    # --- שלב 3: הגדרת מודל ה-Embedding ---
    print("\n🤖 שלב 3: אתחול מודל ה-Embedding של Cohere...")
    embed_model = CohereEmbedding(
        model_name="embed-multilingual-v3.0",
        api_key=os.getenv("COHERE_API_KEY")
    )

    # --- שלב 4: חיבור ל-Pinecone ויצירת האינדקס הווקטורי ---
    print("\n🤖 שלב 4: התחברות ל-Pinecone ואינדוקס ה-Nodes...")
    
    # אתחול קליינט Pinecone הרשמי
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    pinecone_index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    
    # יצירת ה-Vector Store של LlamaIndex שמתווך מול Pinecone
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    
    # הגדרת ה-Storage Context עם ה-Vector Store החדש
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # בניית ה-VectorStoreIndex - הוקטורים והמטא-דאטה יישלחו ישירות לענן!
    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=embed_model
    )
    
    print("✅ המידע, הוקטורים וה-Metadata אונדקסו ונשמרו ב-Pinecone בהצלחה!")
    return index

if __name__ == "__main__":
    load_parse_and_index_documents()