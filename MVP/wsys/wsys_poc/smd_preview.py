#!/usr/bin/env python3
"""
SMD Preview: Terminal-friendly Markdown renderer for WSYS.
Integrates with docs/ files – run after editing.
"""

import sys
import markdown
from markdown.extensions import extra, fenced_code
from bs4 import BeautifulSoup

def shell_md(file_path):
    """Render Markdown as plain text in terminal."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            md_content = file.read()

        # Convert to HTML
        html_content = markdown.markdown(md_content, extensions=[extra, fenced_code])

        # Strip to plain text
        soup = BeautifulSoup(html_content, 'html.parser')
        plain_text = soup.get_text()

        # Print with simple formatting
        print("\n" + "="*60)
        print(f"SMD PREVIEW: {file_path}")
        print("="*60)
        print(plain_text)
        print("="*60 + "\n")
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ SMD error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smd_preview.py <file.md>")
        sys.exit(1)
    shell_md(sys.argv[1])
