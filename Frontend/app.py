"""
CodeLens — Gradio Frontend Application.

A simple Gradio UI for:
  Tab 1: Repository Ingestion (enter GitHub URL → ingest)
  Tab 2: Chat (ask questions about the codebase → get cited answers)

Communicates with the FastAPI backend via HTTP.
"""
import gradio as gr
import httpx
import json

# Backend API base URL
API_BASE = "http://localhost:8000"
TIMEOUT = 600.0  # 10 minutes — ingestion can be slow


# ─── API Client Functions ────────────────────────────────────────────────────


def call_ingest(repo_url: str) -> tuple[str, str, bool]:
    """Call the backend ingestion endpoint.
    Returns (status_markdown, selected_tab_id, button_interactive).
    """
    if not repo_url.strip():
        return "❌ Please enter a GitHub repository URL.", "ingest", True

    try:
        response = httpx.post(
            f"{API_BASE}/repo/ingest",
            json={"repo_url": repo_url.strip()},
            timeout=TIMEOUT,
        )
        data = response.json()

        if data.get("status") == "success":
            status = (
                f"✅ **Ingestion Complete!**\n\n"
                f"📦 **Repository:** `{data['repo_name']}`\n"
                f"📄 **Files processed:** {data['files_count']}\n"
                f"🧩 **Chunks created:** {data['chunks_count']}\n\n"
                f"💬 Switching to **Ask Questions** tab..."
            )
            return status, "chat", True  # switch to chat tab
        else:
            return f"❌ **Ingestion Failed**\n\n{data.get('message', 'Unknown error')}", "ingest", True

    except httpx.ConnectError:
        return (
            "❌ **Cannot connect to backend.**\n\n"
            "Make sure the FastAPI server is running:\n"
            "```\ncd Backend\nuvicorn app.main:app --reload --port 8000\n```"
        ), "ingest", True
    except Exception as e:
        return f"❌ **Error:** {str(e)}", "ingest", True


def call_ask(message: str, history: list[dict]) -> tuple[list[dict], str]:
    """Call the backend chat endpoint and return updated history + citations."""
    if not message.strip():
        return history, ""

    # Add user message to history
    history = history + [{"role": "user", "content": message}]

    try:
        # Build API history (exclude the latest user message, it goes in 'question')
        api_history = []
        for msg in history[:-1]:
            api_history.append({"role": msg["role"], "content": msg["content"]})

        response = httpx.post(
            f"{API_BASE}/chat/ask",
            json={
                "question": message.strip(),
                "history": api_history,
            },
            timeout=TIMEOUT,
        )
        data = response.json()

        answer = data.get("answer", "No answer received.")
        citations = data.get("citations", [])

        # Add assistant response to history
        history = history + [{"role": "assistant", "content": answer}]

        # Format citations panel
        citations_md = format_citations(citations)

        return history, citations_md

    except httpx.ConnectError:
        error_msg = (
            "Cannot connect to backend. Make sure the FastAPI server is running on port 8000."
        )
        history = history + [{"role": "assistant", "content": f"❌ {error_msg}"}]
        return history, ""

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        history = history + [{"role": "assistant", "content": f"❌ {error_msg}"}]
        return history, ""


def format_citations(citations: list[dict]) -> str:
    """Format citations as a rich Markdown panel."""
    if not citations:
        return "*No citations available yet. Ask a question!*"

    result = "## 📂 Source Files\n\n"
    for i, cite in enumerate(citations, 1):
        lang = cite.get("language", "").lower()
        file_path = cite.get("file_path", "unknown")
        file_name = cite.get("file_name", "unknown")
        snippet = cite.get("snippet", "")

        # Language badge color
        lang_display = cite.get("language", "Unknown")

        result += f"### {i}. `{file_path}`\n"
        result += f"**Language:** {lang_display}\n\n"

        if snippet:
            # Use appropriate syntax highlighting
            code_lang = lang if lang in {
                "python", "javascript", "typescript", "java", "go",
                "rust", "ruby", "php", "c", "cpp", "csharp", "shell",
                "sql", "html", "css", "json", "yaml", "toml", "markdown",
            } else ""
            result += f"```{code_lang}\n{snippet}\n```\n\n"

        result += "---\n\n"

    return result


# ─── Gradio UI ───────────────────────────────────────────────────────────────


def build_ui():
    """Build and return the Gradio Blocks interface."""

    with gr.Blocks(
        title="CodeLens — Code Intelligence",
    ) as ui:

        gr.Markdown(
            "# 🔍 CodeLens\n"
            "### Code Intelligence Assistant — Understand any codebase instantly",
            elem_classes=["main-title"],
        )

        with gr.Tabs() as tabs:

            # ── Tab 1: Ingest Repository ─────────────────────────────────
            with gr.Tab("📦 Ingest Repository", id="ingest"):
                gr.Markdown(
                    "Enter a public GitHub repository URL to ingest. "
                    "CodeLens will clone it, parse the source files, "
                    "create intelligent code chunks, and index them for search."
                )

                with gr.Row():
                    with gr.Column(scale=4):
                        repo_url_input = gr.Textbox(
                            label="GitHub Repository URL",
                            placeholder="https://github.com/user/repo",
                            show_label=True,
                            lines=1,
                        )
                    with gr.Column(scale=1, min_width=120):
                        ingest_btn = gr.Button(
                            "🚀 Ingest",
                            variant="primary",
                            size="lg",
                        )

                ingest_output = gr.Markdown(
                    value="*Enter a repository URL above and click Ingest to begin.*",
                    label="Status",
                )

                gr.Markdown(
                    "---\n"
                    "**⚠️ Note:** Ingestion can take several minutes for larger repositories "
                    "due to LLM-based chunking and API rate limits. Please be patient."
                )

                # Show processing state, then run ingestion
                def show_processing():
                    """Immediately show a processing indicator and disable the button."""
                    return (
                        "⏳ **Processing...** Cloning repo, parsing files, "
                        "creating chunks & embeddings.\n\n"
                        "This may take several minutes. Please wait...",
                        gr.update(value="⏳ Processing...", interactive=False),
                    )

                def run_ingest_and_restore(repo_url):
                    """Run ingestion and restore the button when done."""
                    status, tab_id, _ = call_ingest(repo_url)
                    return (
                        status,
                        gr.update(value="🚀 Ingest", interactive=True),
                        gr.Tabs(selected=tab_id),
                    )

                ingest_btn.click(
                    fn=show_processing,
                    inputs=[],
                    outputs=[ingest_output, ingest_btn],
                ).then(
                    fn=run_ingest_and_restore,
                    inputs=[repo_url_input],
                    outputs=[ingest_output, ingest_btn, tabs],
                )

            # ── Tab 2: Ask Questions ─────────────────────────────────────
            with gr.Tab("💬 Ask Questions", id="chat"):
                with gr.Row():
                    # Left: Chat
                    with gr.Column(scale=1):
                        chatbot = gr.Chatbot(
                            label="Conversation",
                            height=550,
                            placeholder="Ask a question about the ingested codebase...",
                        )

                        with gr.Row():
                            question_input = gr.Textbox(
                                label="Your Question",
                                placeholder="Where is authentication handled?",
                                show_label=False,
                                lines=1,
                                scale=5,
                            )
                            ask_btn = gr.Button(
                                "Ask",
                                variant="primary",
                                scale=1,
                                min_width=80,
                            )

                        clear_btn = gr.Button("🗑️ Clear Chat", size="sm")

                    # Right: Citations
                    with gr.Column(scale=1):
                        citations_panel = gr.Markdown(
                            value="*Source file citations will appear here after you ask a question.*",
                            label="📚 Source Citations",
                            show_label=True,
                        )

                # Wire up chat
                def submit_question(message, history):
                    if not message.strip():
                        return "", history, ""
                    new_history, citations = call_ask(message, history)
                    return "", new_history, citations

                question_input.submit(
                    fn=submit_question,
                    inputs=[question_input, chatbot],
                    outputs=[question_input, chatbot, citations_panel],
                )
                ask_btn.click(
                    fn=submit_question,
                    inputs=[question_input, chatbot],
                    outputs=[question_input, chatbot, citations_panel],
                )
                clear_btn.click(
                    fn=lambda: ([], "*Source file citations will appear here after you ask a question.*"),
                    outputs=[chatbot, citations_panel],
                )

    return ui


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    )
    
    css = """
    .main-title { text-align: center; margin-bottom: 0.5em; }
    .subtitle { text-align: center; color: #666; margin-bottom: 1.5em; }
    """

    ui = build_ui()
    ui.launch(inbrowser=True, server_port=7860, theme=theme, css=css)
