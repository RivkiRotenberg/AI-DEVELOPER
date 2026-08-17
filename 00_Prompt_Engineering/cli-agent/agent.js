const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
//גירסה 1
//מחזיר הזהרה גם על מחיקת דברים לגיטמיים
// const SYSTEM_PROMPT = `
// אתה מומחה לפקודות טרמינל.
// תפקידך: לקבל הוראה בעברית ולהחזיר פקודת CLI בלבד.

// חוקים:
// 1. החזר אך ורק את הפקודה עצמה
// 2. אם הבקשה מסוכנת — החזר: DANGER: תיאור הסכנה
// 3. הפקודה תואמת למערכת ההפעלה שצוינה

// דוגמאות:
// - "מה כתובת ה-IP שלי" → ipconfig
// - "הצג תהליכים פעילים" → tasklist
// - "מחק קבצי tmp" → del downloads\\*.tmp
// - "סדר קבצים לפי גודל" → dir /o-s
// `;

//גירסה 2
const SYSTEM_PROMPT = `
אתה מומחה לפקודות טרמינל.
תפקידך: לקבל הוראה בעברית ולהחזיר פקודת CLI בלבד.

חוקים:
1. החזר אך ורק את הפקודה עצמה
2. החזר DANGER רק אם הבקשה עלולה לפגוע במערכת ההפעלה עצמה, 
   כגון: מחיקת System32, פורמט כונן, מחיקת קבצי boot.
   מחיקת קבצי פרויקט כמו node_modules היא לגיטימית לחלוטין!
3. הפקודה תואמת למערכת ההפעלה שצוינה
// גירסה 3
4. אם הבקשה עמומה מדי ואי אפשר להחזיר פקודה מדויקת — 
   החזר: UNCLEAR: שאל את המשתמש מה בדיוק הוא רוצה

דוגמאות:
- "מה כתובת ה-IP שלי" → ipconfig
- "הצג תהליכים פעילים" → tasklist
- "מחק קבצי tmp" → del downloads\\*.tmp
- "סדר קבצים לפי גודל" → dir /o-s

דוגמאות של DANGER אמיתי:
- "מחק System32" → DANGER
- "פרמט את הכונן" → DANGER

דוגמאות לגיטימיות לחלוטין:
- "מחק node_modules" → rd /s /q node_modules
- "נקה את הפרויקט" → rd /s /q node_modules && npm cache clean --force
- "התחל React מחדש" → rd /s /q node_modules && del package-lock.json && npm install
`;

const history = [];

async function convertToCommand(userText, os) {
    const fullMessage = `מערכת הפעלה: ${os}\nהבקשה: ${userText}`;
    history.push({ role: "user", content: fullMessage });

    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
            "HTTP-Referer": "http://localhost:5500",
            "X-Title": "CLI Agent"
        },
        body: JSON.stringify({
            model: "openrouter/auto",
            messages: [
                { role: "system", content: SYSTEM_PROMPT },
                ...history
            ]
        })
    });

    const data = await response.json();
    console.log("תשובה:", JSON.stringify(data));

    if (!data.choices || data.choices.length === 0) {
        throw new Error("לא התקבלה תשובה: " + JSON.stringify(data));
    }

    const command = data.choices[0].message.content.trim();
    history.push({ role: "assistant", content: command });
    return command;
}

function getSelectedOS() {
    return document.querySelector('input[name="os"]:checked').value;
}

function showResult(command) {
  const resultBox = document.getElementById("resultBox");
  const commandOutput = document.getElementById("commandOutput");
  const warningBox = document.getElementById("warningBox");

  if (command.startsWith("DANGER:")) {
    // אדום — מסוכן
    warningBox.textContent = "⚠️ " + command.replace("DANGER:", "").trim();
    warningBox.style.background = "#2d1a1a";
    warningBox.style.borderColor = "#dc2626";
    warningBox.style.color = "#f87171";
    warningBox.classList.remove("hidden");
    resultBox.classList.add("hidden");

  } else if (command.startsWith("UNCLEAR:")) {
    // כחול — צריך הבהרה
    warningBox.textContent = "❓ " + command.replace("UNCLEAR:", "").trim();
    warningBox.style.background = "#1a1a2d";
    warningBox.style.borderColor = "#3b82f6";
    warningBox.style.color = "#93c5fd";
    warningBox.classList.remove("hidden");
    resultBox.classList.add("hidden");

  } else {
    // ירוק — פקודה תקינה
    warningBox.classList.add("hidden");
    commandOutput.textContent = command;
    resultBox.classList.remove("hidden");
  }
}

function addToHistory(userText, command) {
    const historyDiv = document.getElementById("history");
    if (command.startsWith("DANGER:")) return;
    const item = document.createElement("div");
    item.className = "history-item";
    item.innerHTML = `<span class="user-text">"${userText}"</span><code>${command}</code>`;
    historyDiv.prepend(item);
}

function setLoading(isLoading) {
    const btn = document.getElementById("convertBtn");
    btn.disabled = isLoading;
    btn.textContent = isLoading ? "ממיר... ⏳" : "המר לפקודה ⚡";
}

document.getElementById("convertBtn").addEventListener("click", async () => {
    const userInput = document.getElementById("userInput");
    const userText = userInput.value.trim();
    if (!userText) return;
    setLoading(true);
    try {
        const command = await convertToCommand(userText, getSelectedOS());
        showResult(command);
        addToHistory(userText, command);
    } catch (error) {
        alert("שגיאה: " + error.message);
    } finally {
        setLoading(false);
    }
});

document.getElementById("userInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") document.getElementById("convertBtn").click();
});

document.getElementById("copyBtn").addEventListener("click", () => {
    navigator.clipboard.writeText(document.getElementById("commandOutput").textContent);
    const btn = document.getElementById("copyBtn");
    btn.textContent = "✅ הועתק!";
    setTimeout(() => { btn.textContent = "📋 העתק"; }, 2000);
}); 