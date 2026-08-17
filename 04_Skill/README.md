# File Browser Agent עם תמיכה ב-Skills

זהו יישום שולחני (Electron) שמאפשר דפדוף בקבצים יחד עם צ'אט סמכותי שמבין את סביבת הקבצים, בוחר קבצים/תיקיות, קורא/כותב מידע ומפעיל Skills מותאמים למשימות.

היישום כולל עכשיו מנגנון מלא של Discovery ו-Tool Calling עבור Skills:

- גילוי אוטומטי של קבצי SKILL.md מתיקיית ה-Skills
- יצירת קטלוג Skills שמועבר למודל
- כלי activate_skill שמאפשר למודל לטעון הנחיות מלאות של Skill רלוונטי
- טעינה של ה-Skills בזמן ההפעלה וה-IPC לצורך עדכון רשימה

---

## דרישות מערכת

- Node.js 18+
- Windows
- מפתח Anthropic API Key

---

## התקנה והרצה

```powershell
npm i
node node_modules/electron/install.js
npm run dev
```

אם ברצונך להגדיר מיקום מותאם אישית של Skills, צור קובץ .env עם:

```env
FILE_BROWSER_SKILLS_DIR=C:\Users\<username>\.file-browser-agent\skills
ANTHROPIC_API_KEY=sk-ant-...
```

---

## תיקיית Skills

ברירת המחדל היא:

```powershell
C:\Users\<username>\.file-browser-agent\skills
```

ניתן ליצור אותה כך:

```powershell
mkdir "$env:USERPROFILE\.file-browser-agent\skills"
```

כל Skill הוא תיקייה שמכילה קובץ SKILL.md. הדוגמה הבאה תופעל על ידי המודל כאשר המשימה תתאים לה:

```md
---
name: summarize_folder
description: Summarize the contents of a selected folder and list important files.
---

When the user asks for a summary of a folder, inspect the directory contents,
list the main files, and provide a concise report in Hebrew.
```

---

## איך זה עובד

1. האפליקציה סורקת את תיקיית ה-Skills ומטענת את כל ה-SKILL.md.
2. היא יוצרת קטלוג Skills עם שם ותיאור.
3. המודל מקבל את הקטלוג דרך system prompt ודרך כלי activate_skill.
4. כאשר המשימה מתאימה ל-Skill, המודל מפעיל activate_skill ומקבל את ההנחיות המלאות.

---

## סקריפטים זמינים

```powershell
npm run dev
npm run build
npm run typecheck
```
