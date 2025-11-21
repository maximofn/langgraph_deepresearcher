"""
Gradio Interface for Deep Researcher

This module provides a modern chat interface for the Deep Researcher system
with transparent intermediate outputs and clear final results.
"""

import gradio as gr
import asyncio
from typing import List, Tuple
import sys

sys.path.append('src')

from front.deep_researcher_wrapper import DeepResearcherWrapper


# CSS for styling the interface
CUSTOM_CSS = """
/* Main container styling */
.gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Chatbot message styling */
#chatbot {
    font-size: 14px;
}

#chatbot .message {
    padding: 12px;
    border-radius: 8px;
}

/* Button styling */
.primary-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
}
"""


class DeepResearcherUI:
    """Main UI class for the Deep Researcher Gradio interface"""

    def __init__(self):
        self.wrapper = DeepResearcherWrapper()
        self.waiting_for_clarification = False
        self.chat_history: List[Tuple[str, str]] = []

    async def process_message(self, message: str, history: List[Tuple[str, str]]):
        """
        Process a user message and yield responses as they come

        Args:
            message: User's input message
            history: Chat history

        Yields:
            Updated chat history
        """
        if not message.strip():
            yield history
            return

        # Add user message to history
        history = history + [(message, None)]
        yield history

        # Determine if this is initial research or clarification
        if self.waiting_for_clarification:
            # Continue with clarification
            response_parts = []

            async for event in self.wrapper.continue_with_clarification(message):
                response_parts.append(self._format_event(event))

                # Update the assistant's response
                history[-1] = (message, "\n\n".join(response_parts))
                yield history

            self.waiting_for_clarification = False

        else:
            # Start new research
            response_parts = []

            async for event in self.wrapper.run_research(message):
                event_html = self._format_event(event)
                response_parts.append(event_html)

                # Check if clarification is needed
                if event.get("type") == "clarification":
                    self.waiting_for_clarification = True

                # Update the assistant's response
                history[-1] = (message, "\n\n".join(response_parts))
                yield history

    def _format_event(self, event: dict) -> str:
        """
        Format an event as text for display (Gradio handles markdown internally)

        Args:
            event: Event dictionary

        Returns:
            Formatted string for the event
        """
        event_type = event.get("type", "")
        content = event.get("content", "")
        title = event.get("title", "")
        is_intermediate = event.get("is_intermediate", True)

        # Format based on event type
        if event_type == "user_message":
            return content

        elif event_type == "final_report":
            # Final report as markdown
            return f"**📋 Informe Final**\n\n{content}"

        elif event_type == "clarification":
            return f"**❓ Clarificación Necesaria**\n\n{content}"

        elif event_type == "error":
            return f"**❌ Error**\n\n{content}"

        # Intermediate outputs with transparency indicator
        elif "scope" in event_type:
            prefix = "🔵 " if is_intermediate else "✅ "
            return f"{prefix}**{title}**\n_{content}_" if is_intermediate else f"{prefix}**{title}**\n{content}"

        elif "supervisor" in event_type:
            prefix = "🟣 " if is_intermediate else "✅ "
            return f"{prefix}**{title}**\n_{content}_" if is_intermediate else f"{prefix}**{title}**\n{content}"

        elif "research" in event_type:
            prefix = "🟢 " if is_intermediate else "✅ "
            return f"{prefix}**{title}**\n_{content}_" if is_intermediate else f"{prefix}**{title}**\n{content}"

        elif "writer" in event_type:
            prefix = "🟠 " if is_intermediate else "✅ "
            return f"{prefix}**{title}**\n_{content}_" if is_intermediate else f"{prefix}**{title}**\n{content}"

        elif "compression" in event_type:
            prefix = "⚙️ " if is_intermediate else "✅ "
            return f"{prefix}**{title}**\n_{content}_" if is_intermediate else f"{prefix}**{title}**\n{content}"

        else:
            # Generic intermediate message
            prefix = "⏳ " if is_intermediate else "✅ "
            return f"{prefix}**{title}**\n_{content}_" if is_intermediate else f"{prefix}**{title}**\n{content}"


def create_interface():
    """Create and configure the Gradio interface"""

    ui = DeepResearcherUI()

    with gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Soft(), title="Deep Researcher") as app:
        gr.Markdown(
            """
            # 🔍 Deep Researcher

            Sistema de investigación profunda multi-agente. Introduce tu pregunta de investigación
            y observa cómo los diferentes agentes colaboran para generar un informe completo.
            """
        )

        chatbot = gr.Chatbot(
            value=[],
            elem_id="chatbot",
            height=600,
            bubble_full_width=False,
            show_label=False,
            type="tuples"
        )

        with gr.Row():
            msg = gr.Textbox(
                placeholder="¿Sobre qué quieres investigar?",
                show_label=False,
                scale=9
            )
            submit = gr.Button("Enviar", scale=1, variant="primary")

        gr.Markdown(
            """
            ### 💡 Cómo funciona

            1. **Scope Agent** (azul): Analiza tu pregunta y determina si necesita clarificación
            2. **Supervisor Agent** (morado): Coordina la investigación y delega tareas
            3. **Research Agents** (verde): Ejecutan investigaciones específicas en paralelo
            4. **Writer Agent** (naranja): Sintetiza los hallazgos en un informe final

            Las salidas intermedias se muestran con transparencia, mientras que
            los resultados finales se destacan claramente.
            """
        )

        # Set up event handlers
        msg.submit(ui.process_message, [msg, chatbot], [chatbot]).then(
            lambda: "", None, [msg]
        )
        submit.click(ui.process_message, [msg, chatbot], [chatbot]).then(
            lambda: "", None, [msg]
        )

    return app


if __name__ == "__main__":
    app = create_interface()
    app.queue()  # Enable queuing for streaming
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
