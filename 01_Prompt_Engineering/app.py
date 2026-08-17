import os
import pandas as pd
from datetime import datetime
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
from sandbox import run_command_in_ubuntu_sandbox

load_dotenv()

LOG_FILE = "chat_logs.xlsx"

def log_to_excel(system_prompt, user_message, assistant_response, sandbox_output=""):
    new_log = pd.DataFrame([{
        "Timestamp": datetime.now(),
        "System Prompt": system_prompt,
        "User Message": user_message,
        "Assistant Response (Command)": assistant_response,
        "Sandbox Output": sandbox_output
    }])
    
    try:
        if os.path.exists(LOG_FILE):
            with pd.ExcelWriter(LOG_FILE, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                if 'Chats' in writer.sheets:
                    startrow = writer.sheets['Chats'].max_row
                    new_log.to_excel(writer, index=False, header=False, sheet_name='Chats', startrow=startrow)
                else:
                    # If the sheet exists but is empty, or we are creating a new file
                    new_log.to_excel(writer, index=False, sheet_name='Chats')
        else:
            new_log.to_excel(LOG_FILE, index=False, sheet_name='Chats')
    except Exception as e:
        print(f"Failed to log to Excel: {e}")

try:
    with open("systemPrompt.txt", "r", encoding="utf-8") as f:
        DEFAULT_SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    DEFAULT_SYSTEM_PROMPT = "You are an expert at translating natural language to Linux shell commands. Respond with only the shell command. No explanations."

api_key = os.getenv("OPENROUTER_API_KEY")
client = (
    OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    if api_key
    else None
)

def get_command_from_ai(message, history, system_prompt):
    if not api_key or not client:
        return "API key not configured.", ""

    # --- NEW: Add a wrapper to the user's message ---
    # This clarifies the target environment for the AI without changing the system prompt file.
    wrapped_message = f"Translate the following request into a single, valid Linux bash command: '{message}'"

    messages = [{"role": "system", "content": system_prompt}]
    # We don't need chat history for this task, as each command is independent.
    messages.append({"role": "user", "content": wrapped_message})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages,
        )
        command = response.choices[0].message.content or ""
        return None, command.strip()
    except Exception as e:
        return f"Error getting command from AI: {e}", ""

def chat_and_execute(message, history, system_prompt=DEFAULT_SYSTEM_PROMPT):
    # Step 1: Get the command from the AI
    error, command = get_command_from_ai(message, history, system_prompt)
    if error:
        log_to_excel(system_prompt, message, "AI_ERROR", error)
        return error
    
    if not command:
        no_command_message = "The AI did not return a command. Please try rephrasing your request."
        log_to_excel(system_prompt, message, "NO_COMMAND", no_command_message)
        return no_command_message

    # Step 2: Run the command in the sandbox
    sandbox_output = run_command_in_ubuntu_sandbox(command)
    
    # Step 3: Log the results
    log_to_excel(system_prompt, message, command, sandbox_output)
    
    # Step 4: Format and return the output for the user
    formatted_output = f"▶️ Command:\n`{command}`\n\n✅ Sandbox Output:\n```\n{sandbox_output}\n```"
    return formatted_output

with gr.Blocks(css="stylsheet.css") as demo:
    gr.Markdown("# Command Sandbox")
    gr.Markdown("Enter a natural language request, and the AI will translate it into a Linux command and run it in a secure sandbox.")
    gr.ChatInterface(
        fn=chat_and_execute,
        additional_inputs=[gr.Textbox(DEFAULT_SYSTEM_PROMPT, label="System Prompt", lines=10)],
        examples=[
            ["list all files and folders in the root directory with details"],
            ["show the current date and time"],
            ["print the phrase 'hello world' to the console"],
        ]
    )

if __name__ == "__main__":
    demo.launch()
