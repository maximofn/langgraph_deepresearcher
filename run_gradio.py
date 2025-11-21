#!/usr/bin/env python3
"""
Launch script for Deep Researcher Gradio Interface

This script provides an easy way to launch the Gradio interface
for the Deep Researcher system.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from front.gradio_app import create_interface


def main():
    """Launch the Gradio interface"""
    print("🚀 Launching Deep Researcher Gradio Interface...")
    print("=" * 60)
    print()

    # Create and launch the interface
    app = create_interface()
    app.queue()  # Enable queuing for streaming

    print("✓ Interface ready!")
    print()
    print("📡 Server will start at: http://localhost:7860")
    print("🛑 Press Ctrl+C to stop the server")
    print()

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()
