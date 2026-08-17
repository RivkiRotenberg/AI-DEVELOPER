import os
from langchain_groq import ChatGroq
# חזרנו לייבוא המקורי שעבד אצלך, פשוט נתעלם מהאזהרה של ווינדוס
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

# =====================================================================
# 1. הגדרת מפתחות ה-API ישירות בקוד
# =====================================================================
os.environ["GROQ_API_KEY"] = "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"
# ⚠️ ודאי שכאן מופיע המפתח האמיתי שלך מ-Tavily:
os.environ["TAVILY_API_KEY"] = "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"

# =====================================================================

# 2. הגדרת כלי החיפוש של Tavily
search_tool = TavilySearchResults(max_results=5)
tools = [search_tool]

# 3. הגדרת מודל השפה (LLM) באמצעות Groq
model = ChatGroq(model="llama3-70b-8192", temperature=0)

# 4. ניסוח ה-System Prompt (ההנחיות לסוכן)
system_message = (
    "אתה סוכן איסוף מידע מומחה, המהווה חלק ממערכת NotebookLM. "
    "תפקידך הוא לחפש באינטרנט מקורות מידע איכותיים ומגוונים על הנושא שהמשתמש יבקש. "
    "עליך להשתמש בכלי החיפוש העומד לרשותך, לאסוף את הקישורים והמידע, "
    "ולהציג למשתמש רשימה מסודרת של המקורות שמצאת עם תקציר קצר לכל מקור. "
    "תקשר תמיד בעברית בלבד."
)

# 5. יצירת ה-Agent עם הפרמטר prompt המעודכן
agent_app = create_react_agent(model, tools, prompt=system_message)


# 6. פונקציה להרצת הסוכן ובדיקה בטרמינל
def test_agent():
    query = input("📝 הזן נושא לחיפוש (לדוגמה: פיתוחים באנרגיה ירוקה): ")
    inputs = {"messages": [("user", query)]}

    print("\n🤖 הסוכן מתחיל לעבוד ולחפש...")

    # הרצת הסוכן והדפסת השלבים שהוא מבצע
    for event in agent_app.stream(inputs, stream_mode="values"):
        # מדפיס את ההודעה האחרונה שנוספה לצ'אט
        event["messages"][-1].pretty_print()


if __name__ == "__main__":
    test_agent()