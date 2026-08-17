import asyncio
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp.server.fastmcp import FastMCP
from weather_Israel import mcp as weather_israel_mcp


async def run_chat():
    # יצירת מופע של ה-LLM (כאן אנחנו משתמשים ב-FastMCP כמתווך פשוט לבדיקה)
    # בגרסה המלאה, כאן מתבצע החיבור ל-Anthropic או OpenAI
    print("--- מערכת מזג האוויר של ישראל מוכנה ---")
    print("צייני שם של עיר כדי לבדוק את התחזית (או 'exit' ליציאה):")

    while True:
        user_input = input("\nהשאלה שלך: ")
        if user_input.lower() == 'exit':
            break

        # הרצת השרת המקומי ובדיקת הכלים
        # הערה: בסביבת פיתוח אמיתית, ה-Host שולח את השאלה ל-LLM
        # וה-LLM מחליט איזה כלי להפעיל מה-weather_Israel.py

        print(f"מפעיל חיפוש עבור: {user_input}...")

        # כאן אנחנו מדמים את הקריאות שה-LLM היה עושה
        try:
            await weather_israel_mcp.call_tool("open_weather_forecast_israel", {})
            await weather_israel_mcp.call_tool("enter_weather_forecast_city_israel", {"city_name": user_input})
            await weather_israel_mcp.call_tool("select_weather_forecast_city_israel", {})
            result = await weather_israel_mcp.call_tool("extract_weather_data", {})

            print("\n--- תוצאות מהאתר ---")
            print(result)
        except Exception as e:
            print(f"קרתה שגיאה: {e}")


if __name__ == "__main__":
    asyncio.run(run_chat())