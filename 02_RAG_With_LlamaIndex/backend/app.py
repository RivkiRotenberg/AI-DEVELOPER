import os
import json
import asyncio
from dotenv import load_dotenv
import gradio as gr

from llama_index.utils.workflow import draw_all_possible_flows
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.cohere import Cohere
from llama_index.embeddings.cohere import CohereEmbedding 
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import get_response_synthesizer
from llama_index.postprocessor.cohere_rerank import CohereRerank
from pinecone import Pinecone

from llama_index.core.workflow import (
    Workflow, 
    Event, 
    StartEvent, 
    StopEvent, 
    step, 
    Context
)
from llama_index.core.schema import NodeWithScore

load_dotenv()

if not os.getenv("COHERE_API_KEY"):
    raise ValueError("אנא ודאי ש-COHERE_API_KEY מוגדר בקובץ .env")

# 1. הגדרת ה-LLM וה-Embedding
llm = Cohere(
    api_key=os.getenv("COHERE_API_KEY"), 
    model="command-r-08-2024"
)
Settings.llm = llm

Settings.embed_model = CohereEmbedding(
    cohere_api_key=os.getenv("COHERE_API_KEY"),
    model_name="embed-multilingual-v3.0",
    input_type="search_query"
)

# אתחול חיבור ל-Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME")
pinecone_index = pc.Index(name=index_name)

vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)


# ----------------------------------------------------
# 1. הגדרת האירועים (Events)
# ----------------------------------------------------
class QueryEvent(Event):
    query: str

class StructuredDataEvent(Event):
    query: str
    category: str

class RetrievalEvent(Event):
    nodes: list[NodeWithScore]
    query: str

class ValidationEvent(Event):
    nodes: list[NodeWithScore]
    query: str


# ----------------------------------------------------
# 2. ה-Workflow
# ----------------------------------------------------
class RAGWorkflow(Workflow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # טעינת נתוני ה-JSON המובנים
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "project_data.json")
        if not os.path.exists(json_path):
            json_path = os.path.join(current_dir, "app", "project_data.json")

        self.structured_data = {}
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                self.structured_data = json.load(f)

    @step
    async def route_query(self, ctx: Context, ev: StartEvent) -> QueryEvent | StructuredDataEvent | StopEvent:
        """שלב Routing: החלטה אם לבצע שליפה מובנית או חיפוש סמנטי"""
        query = ev.get("query")
        if not query or query.strip() == "":
            return StopEvent(result="נא להזין שאלה תקינה.")

        query_lower = query.lower()

        # ניתוח כוונת המשתמש לקטגוריות המובנות
        if any(keyword in query_lower for keyword in ["החלטות", "decisions", "מה הוחלט"]):
            return StructuredDataEvent(query=query, category="decisions")
        elif any(keyword in query_lower for keyword in ["כללים", "rules", "הנחיות", "כללי פיתוח"]):
            return StructuredDataEvent(query=query, category="rules")
        elif any(keyword in query_lower for keyword in ["אזהרות", "warnings", "רגישות", "סכנות"]):
            return StructuredDataEvent(query=query, category="warnings")

        return QueryEvent(query=query)

    @step
    async def process_structured_data(self, ctx: Context, ev: StructuredDataEvent) -> StopEvent:
        """שליפת הנתונים המובנים מה-JSON וניסוח תשובה ע"י ה-LLM המעודכן"""
        category = ev.category
        items = self.structured_data.get(category, [])

        if not items:
            return StopEvent(result=f"לא נמצאו פריטים בקטגוריית {category}.")

        # 1. עיבוד וזיהוי גמיש של שדות האובייקטים
        extracted_text = f"להלן הנתונים שחולצו מקטגוריית {category}:\n"
        for idx, item in enumerate(items, 1):
            title = item.get("title") or item.get("warning") or item.get("rule") or item.get("name") or "ללא כותרת"
            desc = (
                item.get("summary") 
                or item.get("description") 
                or item.get("details") 
                or item.get("text") 
                or item.get("content") 
                or ""
            )
            source = item.get("source", {}).get("file_path", "לא ידוע")
            extracted_text += f"{idx}. כותרת: {title} | תיאור: {desc} | מקור: {source}\n"

        # 2. שליחה ל-LLM בעזרת Chat API
        from llama_index.core.llms import ChatMessage, MessageRole

        messages = [
            ChatMessage(
                role=MessageRole.USER,
                content=(
                    f"המשתמש שאל: {ev.query}\n\n"
                    f"להלן הנתונים המובנים שנשלפו עבור בקשתו:\n{extracted_text}\n\n"
                    f"אנא סכם וענה למשתמש בצורה ברורה, מסודרת ומקצועית בעברית על בסיס הנתונים הללו בלבד."
                )
            )
        ]

        chat_response = await llm.achat(messages)
        return StopEvent(result=str(chat_response.message.content))

    @step
    async def retrieve(self, ctx: Context, ev: QueryEvent) -> RetrievalEvent | StopEvent:
        """שליפה וקטורית מ-Pinecone עבור שאלות סמנטיות פתוחות"""
        query = ev.query
        retriever = index.as_retriever(similarity_top_k=5)
        nodes = retriever.retrieve(query)
        
        return RetrievalEvent(nodes=nodes, query=query)

    @step
    async def validate(self, ctx: Context, ev: RetrievalEvent) -> ValidationEvent | StopEvent:
        """דירוג מחדש (Reranking) וסינון סמנטי"""
        nodes = ev.nodes
        query = ev.query
        
        if not nodes:
            return StopEvent(result="לא נמצא מידע רלוונטי במסמכים עבור שאלה זו.")

        reranker = CohereRerank(api_key=os.getenv("COHERE_API_KEY"), top_n=3)
        reranked_nodes = reranker.postprocess_nodes(nodes=nodes, query_str=query)

        # הורדת הסף ל-0.0 כדי לוודא שתוצאות רלוונטיות לא נחסמות
        filtered_nodes = [node for node in reranked_nodes if node.score is not None and node.score >= 0.0]
        
        if not filtered_nodes:
            return StopEvent(result="לא נמצא מידע בעל רמת מובהקות מספקת כדי לענות על השאלה.")
            
        return ValidationEvent(nodes=filtered_nodes, query=query)

    @step
    async def synthesize(self, ctx: Context, ev: ValidationEvent) -> StopEvent:
        """ניסוח התשובה הסופית עבור חיפוש סמנטי בעזרת ה-LLM"""
        query = ev.query
        filtered_nodes = ev.nodes
        
        synthesizer = get_response_synthesizer(response_mode="compact")
        response = synthesizer.synthesize(query=query, nodes=filtered_nodes)
        
        return StopEvent(result=str(response))

# אתחול ה-Workflow
rag_workflow = RAGWorkflow(timeout=30.0, verbose=True)


# ----------------------------------------------------
# 3. ממשק ה-Gradio
# ----------------------------------------------------

async def RAG_chat_interface(message, history):
    try:
        result = await rag_workflow.run(query=message)
        return result
    except Exception as e:
        return f"התרחשה שגיאה במהלך הרצת ה-Workflow: {str(e)}"

with gr.Blocks(title="AI Developer Agent - Hybrid RAG") as demo:
    gr.Markdown("# 🤖 Event-Driven AI Developer Agent")
    gr.Markdown("צינור RAG היברידי המשלב ניתוב (Router), שליפת נתונים מובנים (JSON) וחיפוש סמנטי.")
    
    gr.ChatInterface(
        fn=RAG_chat_interface,
        textbox=gr.Textbox(placeholder="הקלידי את השאלה שלך כאן...", container=False, scale=7)
    )

# יצירת מפת הזרימה של ה-Workflow ושמירתה כקובץ HTML אינטראקטיבי
draw_all_possible_flows(RAGWorkflow, filename="workflow_graph.html")

print("הקובץ workflow_graph.html נוצר בהצלחה! פתחי אותו בדפדפן.")

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)