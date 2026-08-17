# Chat with OpenAI

This project provides a simple web interface using Gradio to chat with an OpenAI model, utilizing the OpenRouter API. It also includes functionality to log the conversation history into an Excel file.

## Features

-   **Web Interface**: A user-friendly chat interface powered by Gradio.
-   **OpenAI Integration**: Connects to OpenAI models through the OpenRouter API.
-   **Custom System Prompt**: Allows users to provide a custom system prompt to guide the assistant's behavior.
-   **Chat Logging**: Logs the entire conversation (timestamps, system prompts, user messages, and assistant responses) to an Excel file named `chat_logs.xlsx`.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd 01_Prompt_Engineering
    ```

2.  **Install dependencies:**
    This project uses `uv` for package management. Make sure you have it installed (`pip install uv`).
    The dependencies are listed in `pyproject.toml`. You can install them using `uv`:
    ```bash
    uv pip install gradio openai python-dotenv pandas openpyxl
    ```

3.  **Set up your API key:**
    Create a `.env` file in the root directory of the project and add your OpenRouter API key:
    ```
    OPENROUTER_API_KEY="your-api-key-here"
    ```

4.  **Customize the system prompt (optional):**
    You can edit the `systemPrompt.txt` file to change the default behavior of the chat assistant.

## How to Run

To start the Gradio web interface, run the following command in your terminal:

```bash
uv run python app.py
```

This will launch a local web server, and you can access the chat interface by navigating to the provided URL in your web browser.

## Project Structure
- **app.py**: The main application file that runs the Gradio interface.
- **main.py**: An additional Python script.
- **pyproject.toml**: Project metadata and dependencies.
- **systemPrompt.txt**: Contains the default system prompt for the AI.
- **README.md**: This file.

## Dependencies

-   gradio
-   openai
-   python-dotenv
-   pandas
-   openpyxl
