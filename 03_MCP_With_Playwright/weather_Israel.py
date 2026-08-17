import asyncio
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

# יצירת מופע של השרת
mcp = FastMCP("WeatherIsrael")

# משתנים גלובליים לניהול הדפדפן
browser_context = {
    "browser": None,
    "page": None,
    "playwright": None
}


async def get_page():
    """פונקציית עזר להבטחת קיום דף פעיל בדפדפן"""
    if browser_context["page"] is None:
        browser_context["playwright"] = await async_playwright().start()
        # headless=False מאפשר לראות את פעולת הדפדפן בלייב
        browser_context["browser"] = await browser_context["playwright"].chromium.launch(headless=False)
        browser_context["page"] = await browser_context["browser"].new_page()
    return browser_context["page"]


@mcp.tool()
async def open_weather_forecast_israel():
    """פותח את הדפדפן ומנווט לאתר תחזית מזג האוויר."""
    page = await get_page()
    await page.goto("https://www.weather2day.co.il/forecast", wait_until="networkidle")
    return "האתר נפתח בהצלחה."


@mcp.tool()
async def enter_weather_forecast_city_israel(city_name: str):
    """מזין את שם העיר בשדה החיפוש באתר."""
    page = await get_page()
    # שימוש בסלקטורים מגוונים למקרה שאחד ישתנה
    search_selectors = ["input#search-input", "input[name='q']", "input[type='search']"]

    found = False
    for selector in search_selectors:
        try:
            await page.wait_for_selector(selector, timeout=5000)
            await page.fill(selector, city_name)
            found = True
            break
        except:
            continue

    if found:
        return f"העיר {city_name} הוזנה בשדה החיפוש."
    else:
        return "שגיאה: לא הצלחתי למצוא את שדה החיפוש בדף."


@mcp.tool()
async def select_weather_forecast_city_israel():
    """בוחר את התוצאה הראשונה שמופיעה ברשימת הערים."""
    page = await get_page()
    try:
        # המתנה לרשימת ההצעות שתופיע
        suggestion_selector = ".autocomplete-suggestion, .search-results a, .ui-menu-item"
        await page.wait_for_selector(suggestion_selector, timeout=7000)
        await page.click(suggestion_selector)
        return "העיר נבחרה בהצלחה מהרשימה."
    except Exception as e:
        # אם הרשימה לא מופיעה, ננסה ללחוץ אנטר בחיפוש
        await page.keyboard.press("Enter")
        return "הרשימה לא הופיעה, בוצע ניסיון חיפוש באמצעות מקש Enter."


@mcp.tool()
async def extract_weather_data():
    """מחלץ את נתוני מזג האוויר מהדף הנוכחי."""
    page = await get_page()
    await page.wait_for_load_state("networkidle")

    # שליפת הטקסט המרכזי של הדף
    content = await page.evaluate("() => document.body.innerText")

    # ניקוי בסיסי
    clean_content = " ".join(content.split())

    return f"נתונים שחולצו: {clean_content[:2000]}"


if __name__ == "__main__":
    mcp.run()