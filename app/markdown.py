"""Markdown rendering utility for blog articles."""

import html
import re
from markupsafe import Markup


def render_markdown(text: str) -> Markup:
    """Render Markdown text (headings, lists, code blocks, blockquotes, inline formatting) to safe HTML."""
    if not text:
        return Markup("")

    lines = text.replace("\r\n", "\n").split("\n")
    output = []
    i = 0
    n = len(lines)

    def parse_inline(s: str) -> str:
        # 1. Escape HTML entities
        s = html.escape(s)
        # 2. Inline code: `code`
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        # 3. Bold: **bold** or __bold__
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", s)
        # 4. Italic: *italic* (with negative lookahead/behind to avoid bold collisions)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
        # 5. Links: [text](url)
        s = re.sub(
            r"\[([^\]]+)\]\((https?://[^\s\)]+|/[^\s\)]*)\)",
            r'<a href="\2" rel="noopener noreferrer">\1</a>',
            s,
        )
        return s

    while i < n:
        line = lines[i]

        # 1. Fenced code block (```lang ... ```)
        if line.startswith("```"):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < n and not lines[i].startswith("```"):
                code_lines.append(html.escape(lines[i]))
                i += 1
            if i < n and lines[i].startswith("```"):
                i += 1
            code_content = "\n".join(code_lines)
            class_attr = f' class="language-{html.escape(lang)}"' if lang else ""
            output.append(
                f'<div class="code-block"><pre><code{class_attr}>{code_content}</code></pre></div>'
            )
            continue

        # 2. Blank line
        if not line.strip():
            i += 1
            continue

        # 3. Headings (# to ######)
        heading_match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            h_text = parse_inline(heading_match.group(2).strip())
            output.append(f"<h{level}>{h_text}</h{level}>")
            i += 1
            continue

        # 4. Blockquote (> ...)
        if line.startswith(">"):
            quote_lines = []
            while i < n and lines[i].startswith(">"):
                quote_lines.append(lines[i].lstrip(">").strip())
                i += 1
            q_text = parse_inline(" ".join(quote_lines))
            output.append(f"<blockquote><p>{q_text}</p></blockquote>")
            continue

        # 5. Unordered List (- or *)
        if re.match(r"^[\*\-]\s+", line):
            items = []
            while i < n and re.match(r"^[\*\-]\s+", lines[i]):
                item_text = re.sub(r"^[\*\-]\s+", "", lines[i])
                if item_text.startswith("[ ] "):
                    item_html = (
                        '<span class="task-checkbox unchecked">☐</span> '
                        + parse_inline(item_text[4:])
                    )
                elif item_text.startswith("[x] "):
                    item_html = (
                        '<span class="task-checkbox checked">☑</span> '
                        + parse_inline(item_text[4:])
                    )
                else:
                    item_html = parse_inline(item_text)
                items.append(f"<li>{item_html}</li>")
                i += 1
            output.append("<ul>\n" + "\n".join(items) + "\n</ul>")
            continue

        # 6. Ordered List (1. 2. 3.)
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i]):
                item_text = re.sub(r"^\d+\.\s+", "", lines[i])
                items.append(f"<li>{parse_inline(item_text)}</li>")
                i += 1
            output.append("<ol>\n" + "\n".join(items) + "\n</ol>")
            continue

        # 7. Standard Paragraph
        para_lines = []
        while (
            i < n
            and lines[i].strip()
            and not lines[i].startswith(("```", "#", ">", "- ", "* "))
            and not re.match(r"^\d+\.\s+", lines[i])
        ):
            para_lines.append(lines[i])
            i += 1
        p_text = parse_inline(" ".join(para_lines))
        output.append(f"<p>{p_text}</p>")

    return Markup("\n\n".join(output))
