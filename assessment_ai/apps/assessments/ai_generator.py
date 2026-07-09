import json
import re
from django.conf import settings


def _build_prompt(text: str, num_questions: int, question_type: str, topic: str) -> str:
    topic_line = f"Focus specifically on the topic: **{topic}**\n" if topic else ""
    type_instruction = {
        "mcq": "All questions must be Multiple Choice (MCQ) with exactly 4 options. Mark the correct answer with is_correct: true.",
        "true_false": "All questions must be True/False with exactly 2 options: 'True' and 'False'. Mark the correct one.",
        "mixed": "Mix of MCQ (4 options) and True/False (2 options) questions.",
        "short_answer": "All questions must be Short Answer type — no options needed, just the question and empty options array.",
    }.get(question_type, "All questions must be MCQ with 4 options.")

    return f"""You are an expert educator and quiz creator.

Below is study material extracted from a document. Based on this content, generate exactly {num_questions} quiz questions.

{topic_line}
{type_instruction}

Return ONLY a valid JSON array — no explanation, no markdown, no extra text. Just the raw JSON array starting with [ and ending with ].

Format:
[
  {{
    "question_text": "What is ...?",
    "question_type": "mcq",
    "marks": 1,
    "order": 1,
    "explanation": "Brief explanation of the correct answer.",
    "options": [
      {{"option_text": "Option A", "is_correct": false, "order": 1}},
      {{"option_text": "Option B", "is_correct": true, "order": 2}},
      {{"option_text": "Option C", "is_correct": false, "order": 3}},
      {{"option_text": "Option D", "is_correct": false, "order": 4}}
    ]
  }}
]

For short_answer type, use: "options": []

Study Material:
---
{text[:10000]}
---

Generate exactly {num_questions} questions now as a JSON array:"""


def generate_questions_with_ai(
    text: str,
    num_questions: int,
    question_type: str = "mcq",
    topic: str = "",
) -> list[dict]:
    """
    Generate quiz questions using Groq (free) with Llama 3.
    Falls back to Anthropic Claude if GROQ_API_KEY is not set.
    """
    groq_key = getattr(settings, 'GROQ_API_KEY', '')
    anthropic_key = getattr(settings, 'ANTHROPIC_API_KEY', '')

    prompt = _build_prompt(text, num_questions, question_type, topic)

    if groq_key and groq_key != 'your-groq-api-key-here':
        raw = _call_groq(groq_key, prompt)
    elif anthropic_key and anthropic_key != 'your-anthropic-api-key-here':
        raw = _call_anthropic(anthropic_key, prompt)
    else:
        raise ValueError(
            "No AI API key configured. "
            "Add GROQ_API_KEY (free at console.groq.com) to your .env file."
        )

    # Strip markdown code fences if model wraps in ```json ... ```
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    # Extract JSON array if there's extra text before/after
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        raw = match.group(0)

    questions = json.loads(raw)

    if not isinstance(questions, list):
        raise ValueError("AI returned unexpected format — expected a JSON array.")

    return questions


def _call_groq(api_key: str, prompt: str) -> str:
    from groq import Groq
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=8000,
    )
    return response.choices[0].message.content


def _call_anthropic(api_key: str, prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
