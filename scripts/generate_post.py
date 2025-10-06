#!/usr/bin/env python3
"""
generate_post.py
 - Reads metadata.json (title, slug, date, link, difficulty)
 - Uses OpenAI (if OPENAI_API_KEY env var present) to generate:
    * Python solution (in a code block)
    * Explanation and complexity
 - Writes markdown to: content/YYYY-MM/DD-<slug>.md
Usage:
  python scripts/generate_post.py --meta-file metadata.json
"""

import os, json, argparse, datetime, textwrap
from pathlib import Path

def load_meta(path):
    return json.load(open(path, "r", encoding="utf-8"))

def build_prompt(meta):
    prompt = f"""
Write a clear, concise Python solution for the LeetCode problem below. Include:
- A short problem restatement (1-3 sentences),
- The final Python solution (executable, no external libs),
- Explanation of the approach in simple language,
- Complexity analysis (time & space),
- A few example test cases (input -> output),
Return the answer in MARKDOWN only. Put the Python code in a fenced block with language "python".

Problem:
Title: {meta.get('title')}
Link: {meta.get('link')}
Difficulty: {meta.get('difficulty')}
"""
    return prompt.strip()

def generate_with_openai(prompt):
    import openai
    apikey = os.environ.get("OPENAI_API_KEY")
    if not apikey:
        raise RuntimeError("OPENAI_API_KEY not set")
    openai.api_key = apikey
    # Use Chat Completions API (GPT-4/GPT-3.5) if available
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini" if False else "gpt-4o", # adjust model if needed; fallback below
        messages=[{"role":"user","content":prompt}],
        max_tokens=1200,
        temperature=0.0,
    )
    return resp["choices"][0]["message"]["content"]

def fallback_scaffold(meta):
    return f"""# {meta.get('title')}

> LeetCode: {meta.get('link')}
> Difficulty: {meta.get('difficulty')}

## Problem
*(Add the problem statement here — fetch from leetcode if you want.)*

## Solution (Python)

```python
# Add your Python solution here
