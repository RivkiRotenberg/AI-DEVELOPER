# 🤖 AI-Developer-Agent (Event-Driven Hybrid RAG)

מערכת RAG (Retrieval-Augmented Generation) מתקדמת ומבוססת אירועים (LlamaIndex Workflows) המאפשרת תשאול אינטליגנטי בשפה חופשית על גבי מסמכי תיעוד טכניים וקובצי נתונים מובנים. המערכת משלבת ניתוב דינמי (Router), בסיס נתונים וקטורי (Pinecone), דירוג מחדש (Cohere Rerank), ושליפת נתונים מובנים מ-JSON.

---

## 📐 1. תרשים זרימה של המערכת (Workflow Architecture)

flowchart TD
    Start([🚀 StartEvent: שאלת המשתמש]) --> RouteQuery{🧭 route_query}
    
    %% מסלול שליפה מובנית
    RouteQuery -- "מילות מפתח (החלטות / כללים / אזהרות)" --> StructuredEvent[📦 StructuredDataEvent]
    StructuredEvent --> ProcessJSON[📄 process_structured_data: שליפה מ-JSON]
    ProcessJSON --> LLMStructured[🧠 achat: ניסוח תשובה ע"י Cohere LLM]
    LLMStructured --> EndStructured([🏁 StopEvent: תשובה למשתמש])

    %% מסלול חיפוש סמנטי
    RouteQuery -- "שאלה פתוחה" --> QueryEvent[🔍 QueryEvent]
    QueryEvent --> Retrieve[📚 retrieve: שליפה וקטורית מ-Pinecone]
    Retrieve --> RetrievalEvent[📥 RetrievalEvent]
    RetrievalEvent --> Validate[⚖️ validate: Cohere Rerank & סינון]
    
    Validate -- "score >= 0.0" --> ValidationEvent[✅ ValidationEvent]
    Validate -- "אין מידע רלוונטי" --> EndNoData([🏁 StopEvent: הודעת חסימה])
    
    ValidationEvent --> Synthesize[🧩 synthesize: סינתזת תשובה ע"י LLM]
    Synthesize --> EndSemantic([🏁 StopEvent: תשובה למשתמש])

---

## 🚀 2. תכונות מרכזיות (Features)

1. ניתוב שאילתות דינמי (Routing): זיהוי אוטומטי של כוונת השאילתה - ניתוב לשליפה מובנית מ-JSON או לחיפוש וקטורי סמנטי ב-Pinecone.
2. שליפת נתונים מובנים (Structured Data Extraction): שליפה ישירה של החלטות, כללים ואזהרות מתוך קובץ project_data.json ועיבוד התשובה ע"י ה-LLM.
3. חיפוש סמנטי מבוסס Pinecone: אחזור מהיר של מקטעי טקסט סמנטיים מתוך התיעוד הטכני.
4. מנגנון Reranking & Postprocessing מתקדם: שימוש ב-CohereRerank לסינון ודירוג מחדש של מקטעי המידע כדי למנוע הזיות (Hallucinations) ולחסוך בעלויות tokens.
5. ארכיטקטורה מונעת אירועים (Event-Driven Workflows): ניהול הצינור באמצעות LlamaIndex Workflows לביצועים מהירים ואסינכרוניים.
6. ממשק משתמש אינטראקטיבי: צ'אט בוט מבוסס Gradio התומך בשיחה אסינכרונית.

---

## 🛠️ 3. טכנולוגיות בשימוש (Tech Stack)

* Framework: LlamaIndex Workflows
* LLM & Embeddings Provider: Cohere (command-r-08-2024, embed-multilingual-v3.0, CohereRerank)
* Vector Database: Pinecone
* UI Framework: Gradio
* Language & Runtime: Python 3.10+

---

## 💻 4. התקנה והרצה

1. התקנת החבילות הנדרשות:
pip install llama-index llama-index-vector-stores-pinecone llama-index-llms-cohere llama-index-embeddings-cohere llama-index-postprocessor-cohere-rerank pinecone-client gradio python-dotenv

2. הגדרת משתני הסביבה בקובץ .env:
COHERE_API_KEY=your_cohere_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_INDEX_NAME=your_pinecone_index_name

3. הרצת השרת והממשק:
python app.py
(לאחר ההרצה, תתקבל הכתובת הגישה המקומית: http://127.0.0.1:7860)

---

## 💡 5. דוגמאות לשימוש

| סוג השאילתה | דוגמה לשאלה | נתיב הטיפול במערכת |
| :--- | :--- | :--- |
| נתונים מובנים (החלטות) | "תן לי את החלטות הפרויקט" | ניתוב ל-JSON ➔ חילוץ שדות ➔ ניסוח ב-LLM |
| נתונים מובנים (כללים) | "מהם כללי הפיתוח שנקבעו?" | ניתוב ל-JSON ➔ חילוץ שדות ➔ ניסוח ב-LLM |
| נתונים מובנים (אזהרות) | "מהן אזהרות המערכת בפרויקט?" | ניתוב ל-JSON ➔ חילוץ שדות ➔ ניסוח ב-LLM |
| חיפוש סמנטי פתוח | "כיצד מיושם ניהול המצב (State Management)?" | חיפוש וקטורי ב-Pinecone ➔ Cohere Rerank ➔ ניסוח ב-LLM |
| שאלה לא רלוונטית | "מה המרחק לירח?" | סינון בשלב ה-Validate ➔ מחזיר הודעת חסימה מבוקרת |

##תרשים זרימה ##
02_RAG_With_LlamaIndex/backend/workflow_graph.html