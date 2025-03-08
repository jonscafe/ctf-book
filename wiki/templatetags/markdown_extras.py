from django import template
import markdown2
import re

register = template.Library()

@register.filter
def markdown_format(text):
    extras = {
        # Mengaktifkan fenced code block dengan opsi untuk menebak bahasa (jika tidak didefinisikan)
        "fenced-code-blocks": {"cssclass": "codehilite", "guess_lang": True},
        # Mengaktifkan pewarnaan kode menggunakan Pygments
        "code-color": None,
        "code-friendly": None,
        "tables": None,
        "break-on-newline": None,
        "cuddled-lists": None,
        "metadata": None,
        "footnotes": None,
        "strike": None,
        "task_list": None,
        "wiki-tables": None,
        "link-patterns": [
            (re.compile(r'http[s]?://[^\s<>"]+|www\.[^\s<>"]+'),
             lambda match: f'<a href="{match.group(0)}">{match.group(0)}</a>'),
            (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
             lambda match: f'<a href="mailto:{match.group(0)}">{match.group(0)}</a>')
        ]
    }
    return markdown2.markdown(text, extras=extras)
