import os
from typing import List
from datetime import datetime, timezone
from dotenv import load_dotenv
from llama_index.llms.cohere import Cohere
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core import SimpleDirectoryReader

# ייבוא הסכמה מהקובץ בעל השם הייחודי
from project_schemas import ProjectStructuredData, DecisionItem, RuleItem, WarningItem

load_dotenv()

def extract_structured_data_from_docs(directory_path: str) -> ProjectStructuredData:
    """
    סורקת תיקיית מסמכים ומחלצת מתוכם מידע מובנה קובץ אחר קובץ
    כדי למנוע בעיות Timeout וגודל Context.
    """
    # 1. טעינת המסמכים מתוך התיקייה
    reader = SimpleDirectoryReader(
        input_dir=directory_path, 
        required_exts=[".md"],
        recursive=True
    )
    documents = reader.load_data()
    
    # אובייקט ריק שבו נרכז את כל הממצאים
    final_data = ProjectStructuredData(
        schema_version="1.0",
        generated_at=datetime.now(timezone.utc),
        decisions=[],
        rules=[],
        warnings=[]
    )

    if not documents:
        print("לא נמצאו קבצי תיעוד (md) בתיקייה המבוקשת.")
        return final_data

    # 2. הגדרת מודל השפה
    llm = Cohere(
        api_key=os.getenv("COHERE_API_KEY"), 
        model="command-r-08-2024"
    )

    # 3. הגדרת פרומפט ממוקד עבור קובץ בודד
    prompt_template_str = """
    הנך אנליסט מערכות מומחה. תפקידך הוא לסרוק את קובץ התיעוד הבא ולחלץ מתוכו מידע מובנה ומדויק בלבד.
    
    עליך למצוא ולחלץ את סוגי הפריטים הבאים:
    1. Decisions: החלטות ארכיטקטורה וטכנולוגיה חשובות שהתקבלו.
    2. Rules: כללי פיתוח, הנחיות קוד קשיחות או דרישות ממשק (כמו RTL, ניהול סטייט).
    3. Warnings: אזהרות קריטיות, נקודות רגישות במערכת או רכיבים שאסור לשנות.
    
    שם הקובץ הנוכחי שנסרק: {file_name}
    
    תוכן הקובץ:
    ---------------------------------
    {document_text}
    ---------------------------------
    
    אם אין פריטים מתאימים בקובץ זה עבור קטגוריה מסוימת, החזר מערך ריק עבורה.
    """

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=ProjectStructuredData,
        prompt_template_str=prompt_template_str,
        llm=llm,
        verbose=False
    )

    print(f"נמצאו {len(documents)} דפי תיעוד לעיבוד. מתחיל חילוץ סדרתי...")

    # 4. לולאה המעבדת כל מסמך בנפרד
    for idx, doc in enumerate(documents, 1):
        file_name = doc.metadata.get("file_name", f"file_{idx}.md")
        print(f"[{idx}/{len(documents)}] מעבד את הקובץ: {file_name}...")
        
        try:
            # הרצת החילוץ על הקובץ הנוכחי
            extracted_chunk = program(document_text=doc.text, file_name=file_name)
            
            # עדכון שם הקובץ האמיתי במטה-דאטה של כל פריט שנמצא
            for item in extracted_chunk.decisions:
                item.source.file_path = file_name
                final_data.decisions.append(item)
                
            for item in extracted_chunk.rules:
                item.source.file_path = file_name
                final_data.rules.append(item)
                
            for item in extracted_chunk.warnings:
                item.source.file_path = file_name
                final_data.warnings.append(item)
                
        except Exception as e:
            print(f"⚠️ שגיאה בעיבוד הקובץ {file_name}: {e}")
            continue

    print(f"החילוץ הסדרתי הושלם! סה\"כ נמצאו: {len(final_data.decisions)} החלטות, {len(final_data.rules)} כללים, {len(final_data.warnings)} אזהרות.")
    return final_data

# ----------------------------------------------------
# הרצה עצמאית לבדיקה ושמירת התוצאות לקובץ JSON
# ----------------------------------------------------
if __name__ == "__main__":
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.abspath(os.path.join(current_file_dir, "../../agent_docs"))
    
    print(f"מחפש מסמכים בנתיב: {docs_dir}")
    
    if os.path.exists(docs_dir):
        result = extract_structured_data_from_docs(docs_dir)
        
        # שמירה לקובץ JSON מאוחד בהתאם לתקן Pydantic V2
        output_json_path = os.path.join(current_file_dir, "project_data.json")
        with open(output_json_path, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))
            
        print(f"✅ הנתונים המובנים נשמרו בהצלחה בקובץ: {output_json_path}")
    else:
        print(f"❌ שגיאה: התיקייה לא קיימת בנתיב המבוקש.")