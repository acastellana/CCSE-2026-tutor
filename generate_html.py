#!/usr/bin/env python3
"""
Generate interactive HTML study tool for CCSE exam questions
with Russian explanations generated via OpenAI API
"""

import os
import json
import asyncio
import aiohttp
import html as html_module
from pathlib import Path
from dotenv import load_dotenv

# Load environment from exocortex
load_dotenv(Path(__file__).parent.parent / "exocortex" / ".env")

# Import questions data
from ccse_questions import questions, translations, sections, get_section

EXPLANATIONS_FILE = "explanations.json"
OPTIONS_FILE = "options.json"

async def generate_wrong_options(session, q_num, es_q, es_a, ru_q, ru_a):
    """Generate 2 plausible but wrong answer options in Spanish and Russian"""

    prompt = f"""Para esta pregunta del examen CCSE (ciudadanía española), genera 2 respuestas INCORRECTAS pero plausibles.

Pregunta: {es_q}
Respuesta correcta: {es_a}

Genera exactamente 2 opciones incorrectas en español que sean plausibles pero claramente diferentes de la respuesta correcta.
Responde SOLO en este formato JSON (sin explicaciones):
{{"wrong1_es": "...", "wrong1_ru": "...", "wrong2_es": "...", "wrong2_ru": "..."}}

Las respuestas en ruso deben ser traducciones de las españolas."""

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 200
    }

    try:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                content = data['choices'][0]['message']['content'].strip()
                # Parse JSON from response
                import re
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return None
            else:
                error = await response.text()
                print(f"Error for {q_num}: {response.status} - {error[:100]}")
                return None
    except Exception as e:
        print(f"Exception for {q_num}: {e}")
        return None

async def generate_all_options():
    """Generate wrong options for all questions"""

    options = {}
    if os.path.exists(OPTIONS_FILE):
        with open(OPTIONS_FILE, 'r', encoding='utf-8') as f:
            options = json.load(f)
        print(f"Loaded {len(options)} existing options")

    to_generate = []
    for q_num in questions.keys():
        if str(q_num) not in options:
            to_generate.append(q_num)

    if not to_generate:
        print("All options already generated!")
        return options

    print(f"Generating options for {len(to_generate)} questions...")

    async with aiohttp.ClientSession() as session:
        batch_size = 10
        for i in range(0, len(to_generate), batch_size):
            batch = to_generate[i:i+batch_size]
            tasks = []

            for q_num in batch:
                es_q, es_a, _ = get_question_data(q_num)
                ru_q, ru_a = get_translation_data(q_num)
                tasks.append(generate_wrong_options(session, q_num, es_q, es_a, ru_q, ru_a))

            results = await asyncio.gather(*tasks)

            for q_num, opts in zip(batch, results):
                if opts:
                    options[str(q_num)] = opts

            with open(OPTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(options, f, ensure_ascii=False, indent=2)

            print(f"Options progress: {min(i+batch_size, len(to_generate))}/{len(to_generate)}")
            await asyncio.sleep(0.5)

    return options

async def generate_explanation(session, q_num, es_q, es_a, ru_q, ru_a):
    """Generate a brief Russian explanation for why this is the correct answer"""

    prompt = f"""Вопрос для экзамена CCSE (испанское гражданство):

Вопрос (ES): {es_q}
Правильный ответ (ES): {es_a}
Вопрос (RU): {ru_q}
Правильный ответ (RU): {ru_a}

Напиши КРАТКОЕ объяснение на русском языке (1-2 предложения), почему этот ответ правильный. Только факты, без вступлений."""

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 150
    }

    try:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data['choices'][0]['message']['content'].strip()
            else:
                error = await response.text()
                print(f"Error for {q_num}: {response.status} - {error[:100]}")
                return ""
    except Exception as e:
        print(f"Exception for {q_num}: {e}")
        return ""

def get_question_data(q_num):
    """Extract question and answer, handling variable tuple lengths"""
    data = questions[q_num]
    if len(data) == 2:
        return data[0], data[1], None
    elif len(data) >= 3:
        return data[0], data[1], data[2]
    return data[0], "", None

def get_translation_data(q_num):
    """Extract translation, handling both old tuple format and new dict format"""
    data = translations[q_num]

    # Handle new dict format
    if isinstance(data, dict):
        return data.get('question', ''), data.get('answer', ''), data.get('options', [])

    # Handle old tuple format
    if len(data) >= 2:
        return data[0], data[1], []
    return data[0], "", []


def normalize(text: str) -> str:
    """Normalize text for comparison"""
    import re
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    text = text.rstrip(' .')
    return text

async def generate_all_explanations():
    """Generate explanations for all questions"""

    # Load existing explanations if any
    explanations = {}
    if os.path.exists(EXPLANATIONS_FILE):
        with open(EXPLANATIONS_FILE, 'r', encoding='utf-8') as f:
            explanations = json.load(f)
        print(f"Loaded {len(explanations)} existing explanations")

    # Check for embedded explanations in questions data
    for q_num in questions.keys():
        if str(q_num) not in explanations:
            es_q, es_a, embedded_expl = get_question_data(q_num)
            if embedded_expl:
                explanations[str(q_num)] = embedded_expl

    # Find questions that need explanations
    to_generate = []
    for q_num in questions.keys():
        if str(q_num) not in explanations or not explanations[str(q_num)]:
            to_generate.append(q_num)

    if not to_generate:
        print("All explanations already generated!")
        return explanations

    print(f"Generating {len(to_generate)} explanations...")

    async with aiohttp.ClientSession() as session:
        # Process in batches of 10 to avoid rate limits
        batch_size = 10
        for i in range(0, len(to_generate), batch_size):
            batch = to_generate[i:i+batch_size]
            tasks = []

            for q_num in batch:
                es_q, es_a, _ = get_question_data(q_num)
                ru_q, ru_a = get_translation_data(q_num)
                tasks.append(generate_explanation(session, q_num, es_q, es_a, ru_q, ru_a))

            results = await asyncio.gather(*tasks)

            for q_num, explanation in zip(batch, results):
                explanations[str(q_num)] = explanation

            # Save progress after each batch
            with open(EXPLANATIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(explanations, f, ensure_ascii=False, indent=2)

            print(f"Progress: {min(i+batch_size, len(to_generate))}/{len(to_generate)}")

            # Small delay to avoid rate limits
            await asyncio.sleep(0.5)

    return explanations

def generate_html(explanations):
    """Generate the interactive HTML file"""

    # Load official options from JSON file
    options_file = Path('official_options_raw.json')
    if options_file.exists():
        with open(options_file, 'r', encoding='utf-8') as f:
            official_options = json.load(f)
        print(f"Loaded {len(official_options)} questions with official options")
    else:
        official_options = {}
        print("Warning: official_options_raw.json not found, using fallback options")

    html_questions = []
    current_section = 0

    for q_num in sorted(questions.keys()):
        section = get_section(q_num)
        es_q, es_a, _ = get_question_data(q_num)
        ru_q, ru_a, ru_options = get_translation_data(q_num)
        explanation = explanations.get(str(q_num), "")

        # Add section header if new section
        if section != current_section:
            current_section = section
            es_title, ru_title = sections[section]
            html_questions.append(f'''
        <div class="section-header">
            <h2>{es_title}</h2>
            <p class="section-ru">{ru_title}</p>
        </div>''')

        # Get Spanish options from official_options_raw.json
        q_num_str = str(q_num)
        if q_num_str in official_options:
            es_options = official_options[q_num_str]['options']
            correct_label = None

            # Find correct option label by matching answer
            for opt in es_options:
                if normalize(opt['text']) == normalize(es_a):
                    correct_label = opt['label']
                    break

            if not correct_label:
                correct_label = 'a'
        else:
            # Fallback if options not available
            es_options = [
                {'label': 'a', 'text': es_a},
                {'label': 'b', 'text': '...'},
                {'label': 'c', 'text': '...'}
            ]
            correct_label = 'a'

        # Build options HTML
        options_html = []
        for opt in es_options:
            opt_text = opt['text']
            label = opt['label']
            options_html.append(f'''
                <button class="option" data-label="{label}" onclick="selectOption(this, {q_num}, '{label}', '{correct_label}')">
                    {label}) {opt_text}
                </button>''')

        # Prepare data for JavaScript - escape for JS strings inside HTML onclick attributes
        # Must escape for both JavaScript AND HTML attribute context
        def js_and_html_escape(text):
            # First escape for JavaScript string (single quotes)
            text = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ').replace('\r', '')
            # Then escape double quotes for HTML attribute parsing
            text = text.replace('"', '&quot;')
            return text

        ru_q_js = js_and_html_escape(ru_q)

        # Prepare Russian options for translation button - JSON string needs JS+HTML escaping
        ru_options_json_str = json.dumps([{
            'label': opt['label'],
            'text': opt['text']
        } for opt in ru_options], ensure_ascii=False)
        ru_options_js = js_and_html_escape(ru_options_json_str)

        explanation_js = js_and_html_escape(explanation)

        html_questions.append(f'''
        <div class="question-card" id="q{q_num}">
            <div class="q-number">#{q_num}</div>
            <div class="question">{es_q}</div>
            <div class="options-container">
                {''.join(options_html)}
                <div class="result" id="result{q_num}"></div>
            </div>
            <div class="buttons">
                <button class="btn translate" onclick="toggleTranslate({q_num}, '{ru_q_js}', '{ru_options_js}', '{correct_label}')">Перевод</button>
                <button class="btn explain" onclick="toggleExplain({q_num}, '{explanation_js}')">Объяснение</button>
            </div>
            <div class="translation" id="trans{q_num}"></div>
            <div class="explanation" id="expl{q_num}"></div>
        </div>''')

    questions_html = '\n'.join(html_questions)

    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CCSE 2026 - Preguntas de Estudio</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,500;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #fafafa;
            --bg-card: #ffffff;
            --text: #1a1a1a;
            --text-secondary: #666666;
            --text-tertiary: #999999;
            --border: #e5e5e5;
            --accent: #2563eb;
            --accent-soft: #eff6ff;
            --success: #059669;
            --success-soft: #ecfdf5;
            --error: #b91c1c;
            --error-soft: #fee2e2;
            --translate: #7c3aed;
            --translate-soft: #f5f3ff;
            --shadow: rgba(0, 0, 0, 0.04);
            --shadow-hover: rgba(0, 0, 0, 0.08);
        }}

        [data-theme="dark"] {{
            --bg: #0a0a0a;
            --bg-card: #141414;
            --text: #f5f5f5;
            --text-secondary: #a3a3a3;
            --text-tertiary: #737373;
            --border: #262626;
            --accent: #3b82f6;
            --accent-soft: #1e3a5f;
            --success: #10b981;
            --success-soft: #064e3b;
            --error: #dc2626;
            --error-soft: #450a0a;
            --translate: #a78bfa;
            --translate-soft: #2e1065;
            --shadow: rgba(0, 0, 0, 0.3);
            --shadow-hover: rgba(0, 0, 0, 0.5);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Source Serif 4', Georgia, serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 0;
            line-height: 1.7;
            margin-left: 280px;
            font-size: 18px;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 24px;
        }}

        .header {{
            margin-bottom: 48px;
            text-align: center;
            position: relative;
        }}

        .header-controls {{
            position: absolute;
            top: 0;
            right: 0;
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .theme-toggle {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            padding: 8px 16px;
            border-radius: 24px;
            cursor: pointer;
            font-size: 1rem;
            font-family: 'Source Serif 4', Georgia, serif;
            transition: all 0.2s ease;
        }}

        .theme-toggle:hover {{
            background: var(--accent-soft);
            color: var(--accent);
            border-color: var(--accent);
        }}

        h1 {{
            font-size: 2.75rem;
            font-weight: 600;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
            color: var(--text);
        }}

        .subtitle {{
            color: var(--text-secondary);
            font-size: 1.125rem;
            font-weight: 400;
            font-style: italic;
        }}

        .stats {{
            text-align: center;
            margin-bottom: 32px;
            padding: 16px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            font-size: 1.05rem;
            color: var(--text-secondary);
        }}

        .search-box {{
            width: 100%;
            padding: 14px 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: var(--bg-card);
            color: var(--text);
            font-size: 1.125rem;
            font-family: 'Source Serif 4', Georgia, serif;
            margin-bottom: 32px;
            transition: all 0.2s ease;
        }}

        .search-box:focus {{
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-soft);
        }}

        .search-box::placeholder {{
            color: var(--text-tertiary);
        }}

        .section-header {{
            margin: 56px 0 32px;
            padding: 16px 0;
            border-bottom: 2px solid var(--border);
            background: var(--bg);
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .section-header h2 {{
            font-size: 1.75rem;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 4px;
            letter-spacing: -0.01em;
        }}

        .section-ru {{
            color: var(--text-secondary);
            font-size: 1rem;
            font-style: italic;
        }}

        .question-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 20px;
            transition: all 0.2s ease;
        }}

        .question-card:hover {{
            box-shadow: 0 4px 16px var(--shadow-hover);
            border-color: var(--text-tertiary);
        }}

        .q-number {{
            color: var(--text-tertiary);
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 12px;
            letter-spacing: 0.05em;
        }}

        .question {{
            font-size: 1.25rem;
            margin-bottom: 20px;
            line-height: 1.7;
            color: var(--text);
            font-weight: 600;
        }}

        .options-container {{
            margin-bottom: 20px;
        }}

        .option {{
            display: block;
            width: 100%;
            background: var(--bg-card);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
            cursor: pointer;
            font-size: 1.175rem;
            font-family: inherit;
            text-align: left;
            transition: all 0.25s ease;
            color: var(--text);
            touch-action: manipulation;
            -webkit-tap-highlight-color: rgba(0, 0, 0, 0.1);
        }}

        .option:hover {{
            border-color: var(--text-secondary);
            background: var(--accent-soft);
            transform: translateY(-2px);
        }}

        .option:active {{
            transform: scale(0.98);
        }}

        .option.correct {{
            border-color: var(--success);
            background: var(--success-soft);
            color: var(--success);
            font-weight: 600;
        }}

        .option.incorrect {{
            border-color: var(--error);
            background: var(--error-soft);
            color: var(--error);
            opacity: 0.7;
        }}

        .option.disabled {{
            cursor: default;
            pointer-events: none;
        }}

        .result {{
            margin-top: 10px;
            font-weight: 600;
            font-size: 0.9rem;
        }}

        .result.correct {{
            color: var(--success);
        }}

        .buttons {{
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }}

        .btn {{
            padding: 10px 18px;
            border: 1px solid var(--border);
            background: var(--bg-card);
            color: var(--text-secondary);
            border-radius: 10px;
            cursor: pointer;
            font-size: 1rem;
            font-family: 'Source Serif 4', Georgia, serif;
            transition: all 0.2s ease;
            font-weight: 500;
        }}

        .btn:hover {{
            background: var(--accent-soft);
            color: var(--accent);
            border-color: var(--accent);
        }}

        .btn.translate:hover {{
            background: var(--translate-soft);
            color: var(--translate);
            border-color: var(--translate);
        }}

        .translation, .explanation {{
            display: none;
            margin-top: 16px;
            padding: 16px 20px;
            border-radius: 12px;
            font-size: 1.05rem;
            line-height: 1.7;
            border-left: 3px solid var(--accent);
            background: var(--accent-soft);
            color: var(--text);
        }}

        .translation {{
            border-left-color: var(--translate);
            background: var(--translate-soft);
        }}

        .translation.show, .explanation.show {{
            display: block;
            animation: slideIn 0.3s ease;
        }}

        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(-8px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        /* Bottom navigation bar for mobile */
        .bottom-nav {{
            display: none;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--bg-card);
            border-top: 1px solid var(--border);
            padding: 12px 20px;
            justify-content: space-around;
            align-items: center;
            z-index: 200;
            box-shadow: 0 -4px 12px var(--shadow);
        }}

        .nav-btn {{
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 1.5rem;
            cursor: pointer;
            padding: 8px 16px;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
        }}

        .nav-btn span {{
            font-size: 0.7rem;
            font-family: 'Source Serif 4', Georgia, serif;
        }}

        .nav-btn:active {{
            transform: scale(0.95);
            color: var(--accent);
        }}

        .nav-btn:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
        }}

        /* Print controls - Icon only */
        .print-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            padding: 8px 12px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1.1rem;
            transition: all 0.2s ease;
            line-height: 1;
        }}

        .print-btn:hover {{
            background: var(--accent-soft);
            color: var(--accent);
            border-color: var(--accent);
        }}

        /* Hamburger menu */
        .menu-toggle {{
            display: none;
            position: fixed;
            top: 20px;
            left: 20px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 12px;
            cursor: pointer;
            z-index: 300;
            font-size: 1.5rem;
            box-shadow: 0 2px 8px var(--shadow);
        }}

        .menu-toggle:hover {{
            background: var(--accent-soft);
            color: var(--accent);
        }}

        .index-menu {{
            position: fixed;
            top: 0;
            left: 0;
            width: 280px;
            height: 100vh;
            background: var(--bg-card);
            border-right: 1px solid var(--border);
            z-index: 100;
            overflow-y: auto;
            padding: 32px 20px 100px 20px;
        }}

        .menu-overlay {{
            display: none;
        }}

        .index-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--text);
        }}

        .index-section {{
            margin-bottom: 24px;
        }}

        .index-section-title {{
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 8px;
            padding-bottom: 4px;
            border-bottom: 1px solid var(--border);
        }}

        .index-link {{
            display: block;
            padding: 8px 12px;
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.85rem;
            border-radius: 6px;
            margin-bottom: 4px;
            transition: all 0.2s ease;
        }}

        .index-link:hover {{
            background: var(--accent-soft);
            color: var(--accent);
        }}

        .index-link.answered {{
            color: var(--success);
        }}

        /* Print mode styles - Dense layout */
        @media print {{
            body {{
                background: white;
                color: black;
                padding: 0;
                font-size: 10pt;
                line-height: 1.3;
            }}

            .header, .stats, .search-box, .bottom-nav, .header-controls, .theme-toggle, .menu-toggle, .index-menu, .menu-overlay {{
                display: none !important;
            }}

            body {{
                margin-left: 0;
            }}

            .container {{
                max-width: 100%;
                padding: 0;
            }}

            .section-header {{
                position: static;
                page-break-after: avoid;
                border-bottom: 2px solid #000;
                padding: 4px 0;
                margin: 12px 0 6px;
            }}

            .section-header h2 {{
                color: black;
                font-size: 13pt;
                margin-bottom: 2px;
            }}

            .section-ru {{
                color: #666;
                font-size: 8pt;
            }}

            .question-card {{
                background: white;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                page-break-inside: avoid;
                margin-bottom: 0;
                padding: 6px 0;
            }}

            .question-card.print-hide {{
                display: none;
            }}

            .q-number {{
                color: #666;
                font-size: 8pt;
                margin-bottom: 3px;
            }}

            .question {{
                color: black;
                font-size: 10pt;
                margin-bottom: 4px;
                line-height: 1.3;
            }}

            .answer-container {{
                margin-bottom: 2px;
            }}

            /* Don't show blurred answers in print */
            .answer.hidden {{
                display: none;
            }}

            /* Only show revealed answers clearly */
            .answer.revealed {{
                background: none;
                border: none;
                color: #059669;
                font-size: 9pt;
                padding: 2px 0;
                font-weight: 600;
            }}

            .answer {{
                background: #f5f5f5;
                color: black;
                border: 1px solid #ddd;
                page-break-inside: avoid;
                padding: 4px 8px;
                margin-bottom: 4px;
                font-size: 9pt;
            }}

            .buttons {{
                display: none;
            }}

            .translation, .explanation {{
                display: none !important;
            }}

            .result {{
                display: none;
            }}
        }}

        /* Emoji explosion animation */
        .emoji-particle {{
            position: fixed;
            font-size: 30px;
            pointer-events: none;
            z-index: 9999;
            animation: emojiFloat 2s ease-out forwards;
        }}

        @keyframes emojiFloat {{
            0% {{
                opacity: 1;
                transform: translate(0, 0) rotate(0deg) scale(0);
            }}
            10% {{
                transform: translate(var(--tx), var(--ty)) rotate(var(--rot)) scale(1);
            }}
            100% {{
                opacity: 0;
                transform: translate(calc(var(--tx) * 2), calc(var(--ty) * 2)) rotate(calc(var(--rot) * 2)) scale(0.5);
            }}
        }}

        /* Responsive design for mobile */
        @media (max-width: 768px) {{
            body {{
                margin-left: 0;
                padding: 16px 16px 80px 16px; /* Extra bottom padding for nav bar */
            }}

            .container {{
                padding: 16px;
            }}

            h1 {{
                font-size: 2rem;
            }}

            .header-controls {{
                position: static;
                justify-content: center;
                margin-bottom: 16px;
            }}

            .theme-toggle {{
                padding: 8px 14px;
                font-size: 0.8rem;
            }}

            .header {{
                margin-bottom: 32px;
            }}

            .question-card {{
                padding: 20px;
                scroll-margin-top: 80px; /* Account for sticky header */
            }}

            .question {{
                font-size: 1.05rem;
            }}

            .buttons {{
                display: flex;
                align-items: center;
            }}

            .btn {{
                padding: 10px 16px;
                min-height: 44px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
            }}

            .bottom-nav {{
                display: flex;
            }}

            .section-header {{
                backdrop-filter: blur(10px);
                box-shadow: 0 2px 8px var(--shadow);
            }}

            /* Mobile: hide sidebar, show hamburger */
            .index-menu {{
                left: -100%;
                transition: left 0.3s ease;
                padding: 80px 20px 100px 20px;
                z-index: 250;
            }}

            .index-menu.open {{
                left: 0;
            }}

            .menu-toggle {{
                display: block;
            }}

            .menu-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 200;
            }}

            .menu-overlay.open {{
                display: block;
            }}
        }}
    </style>
</head>
<body>
    <!-- Hamburger menu toggle -->
    <button class="menu-toggle" onclick="toggleMenu()">☰</button>

    <!-- Menu overlay -->
    <div class="menu-overlay" onclick="toggleMenu()"></div>

    <!-- Index/Table of Contents Menu -->
    <div class="index-menu" id="indexMenu">
        <div class="index-title">Índice</div>
        <div id="indexContent"></div>
    </div>

    <div class="container">
        <div class="header">
            <div class="header-controls">
                <button class="print-btn" onclick="window.print()" title="Imprimir todo">🖨️</button>
                <button class="print-btn" onclick="printUnanswered()" title="Imprimir sin responder">📄</button>
                <button class="theme-toggle" onclick="toggleTheme()">Modo oscuro</button>
            </div>
            <h1>CCSE 2026</h1>
            <p class="subtitle">Preguntas de Ciudadanía Española</p>
        </div>

        <div class="stats">
            <span id="revealed">0</span> / {len(questions)} preguntas respondidas
        </div>

        <input type="text" class="search-box" placeholder="Buscar pregunta..." oninput="filterQuestions(this.value)">

        {questions_html}
    </div>

    <div class="bottom-nav">
        <button class="nav-btn" onclick="scrollToTop()">
            ⬆️
            <span>Inicio</span>
        </button>
        <button class="nav-btn" id="prevBtn" onclick="navigateQuestion(-1)">
            ←
            <span>Anterior</span>
        </button>
        <button class="nav-btn" onclick="scrollToNextUnanswered()">
            ❓
            <span>Próxima</span>
        </button>
        <button class="nav-btn" id="nextBtn" onclick="navigateQuestion(1)">
            →
            <span>Siguiente</span>
        </button>
    </div>

    <script>
        let revealedCount = 0;
        const totalQuestions = {len(questions)};

        // Theme management with system preference detection
        const themeToggleBtn = document.querySelector('.theme-toggle');

        (function() {{
            const storedTheme = localStorage.getItem('theme');
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

            if (storedTheme === 'dark' || (!storedTheme && systemPrefersDark)) {{
                document.documentElement.setAttribute('data-theme', 'dark');
                themeToggleBtn.textContent = 'Modo claro';
            }}
        }})();

        function toggleTheme() {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            themeToggleBtn.textContent = newTheme === 'dark' ? 'Modo claro' : 'Modo oscuro';
        }}

        function createEmojiExplosion(x, y) {{
            // Fun emoji mix - happy faces, hearts, party stuff
            const emojis = ['😄', '😊', '🥳', '🎉', '❤️', '💚', '💙', '🌟', '✨', '🎊', '💯', '🔥', '😎', '🤩', '💕', '🎈', '🏆', '👏', '🙌', '💪'];
            const emojiCount = 15; // Number of emojis to spawn

            for (let i = 0; i < emojiCount; i++) {{
                const emoji = document.createElement('div');
                emoji.className = 'emoji-particle';
                emoji.textContent = emojis[Math.floor(Math.random() * emojis.length)];

                // Random direction and distance
                const angle = (Math.random() * Math.PI * 2);
                const distance = 50 + Math.random() * 100;
                const tx = Math.cos(angle) * distance;
                const ty = Math.sin(angle) * distance;
                const rotation = Math.random() * 720 - 360; // Random rotation

                emoji.style.left = x + 'px';
                emoji.style.top = y + 'px';
                emoji.style.setProperty('--tx', tx + 'px');
                emoji.style.setProperty('--ty', ty + 'px');
                emoji.style.setProperty('--rot', rotation + 'deg');

                document.body.appendChild(emoji);

                // Remove emoji after animation
                setTimeout(() => emoji.remove(), 2000);
            }}
        }}

        let answeredQuestions = new Set();

        function selectOption(button, qNum, selectedLabel, correctLabel) {{
            // Prevent multiple answers
            if (answeredQuestions.has(qNum)) {{
                return;
            }}
            answeredQuestions.add(qNum);

            // Get all option buttons for this question
            const card = document.getElementById('q' + qNum);
            const options = card.querySelectorAll('.option');
            const resultDiv = document.getElementById('result' + qNum);

            // Disable all options
            options.forEach(opt => opt.classList.add('disabled'));

            // Mark selected option
            if (selectedLabel === correctLabel) {{
                button.classList.add('correct');
                resultDiv.innerHTML = '✓ Correcto';
                resultDiv.classList.add('correct');
                revealedCount++;
                document.getElementById('revealed').textContent = revealedCount;

                // Create emoji explosion at click position
                const rect = button.getBoundingClientRect();
                const x = rect.left + rect.width / 2;
                const y = rect.top + rect.height / 2;
                createEmojiExplosion(x, y);
            }} else {{
                button.classList.add('incorrect');
                // Also highlight the correct option
                options.forEach(opt => {{
                    if (opt.dataset.label === correctLabel) {{
                        opt.classList.add('correct');
                    }}
                }});
                resultDiv.innerHTML = '✗ Incorrecto';
            }}
        }}

        function toggleTranslate(qNum, ruQ, ruOptionsJson, correctLabel) {{
            const el = document.getElementById('trans' + qNum);
            if (el.classList.contains('show')) {{
                el.classList.remove('show');
                el.innerHTML = '';
            }} else {{
                let ruOptions = [];
                try {{
                    // Parse the JSON directly - it's already properly escaped by Python
                    ruOptions = JSON.parse(ruOptionsJson);
                }} catch (e) {{
                    console.error('Error parsing Russian options:', e);
                    console.error('JSON string:', ruOptionsJson);
                    ruOptions = [];
                }}

                let html = '<strong>Вопрос:</strong> ' + ruQ + '<br><br>';

                if (ruOptions.length > 0) {{
                    html += '<strong>Варианты:</strong><br>';
                    ruOptions.forEach(opt => {{
                        const isCorrect = opt.label === correctLabel;
                        const checkmark = isCorrect ? ' ✓' : '';
                        const style = isCorrect ? ' style="color: var(--success); font-weight: 600;"' : '';
                        html += opt.label + ') ' + '<span' + style + '>' + opt.text + checkmark + '</span><br>';
                    }});
                }} else {{
                    html += '<em style="color: var(--text-tertiary);">Перевод вариантов пока недоступен</em>';
                }}

                el.innerHTML = html;
                el.classList.add('show');
            }}
        }}

        function toggleExplain(qNum, explanation) {{
            const el = document.getElementById('expl' + qNum);
            if (el.classList.contains('show')) {{
                el.classList.remove('show');
                el.innerHTML = '';
            }} else {{
                el.innerHTML = explanation || 'Объяснение недоступно';
                el.classList.add('show');
            }}
        }}

        function filterQuestions(query) {{
            const cards = document.querySelectorAll('.question-card');
            const q = query.toLowerCase();
            cards.forEach(card => {{
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(q) ? 'block' : 'none';
            }});
        }}

        // Print unanswered questions only
        function printUnanswered() {{
            const cards = document.querySelectorAll('.question-card');
            cards.forEach(card => {{
                const answer = card.querySelector('.answer');
                if (answer && answer.classList.contains('revealed')) {{
                    card.classList.add('print-hide');
                }} else {{
                    card.classList.remove('print-hide');
                }}
            }});
            window.print();
            // Remove print-hide class after printing
            setTimeout(() => {{
                cards.forEach(card => card.classList.remove('print-hide'));
            }}, 1000);
        }}

        // Navigation functions
        let currentQuestionIndex = 0;
        const allCards = Array.from(document.querySelectorAll('.question-card'));

        function navigateQuestion(direction) {{
            const visibleCards = allCards.filter(card => card.style.display !== 'none');
            if (visibleCards.length === 0) return;

            currentQuestionIndex += direction;
            if (currentQuestionIndex < 0) currentQuestionIndex = 0;
            if (currentQuestionIndex >= visibleCards.length) currentQuestionIndex = visibleCards.length - 1;

            visibleCards[currentQuestionIndex].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            updateNavButtons();
        }}

        function updateNavButtons() {{
            const visibleCards = allCards.filter(card => card.style.display !== 'none');
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');

            if (prevBtn) prevBtn.disabled = currentQuestionIndex === 0;
            if (nextBtn) nextBtn.disabled = currentQuestionIndex >= visibleCards.length - 1;
        }}

        function scrollToTop() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        function scrollToNextUnanswered() {{
            const unanswered = allCards.find((card, index) => {{
                const answer = card.querySelector('.answer');
                return index > currentQuestionIndex &&
                       answer &&
                       !answer.classList.contains('revealed') &&
                       card.style.display !== 'none';
            }});

            if (unanswered) {{
                currentQuestionIndex = allCards.indexOf(unanswered);
                unanswered.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                updateNavButtons();
            }} else {{
                // Wrap around to first unanswered
                const firstUnanswered = allCards.find(card => {{
                    const answer = card.querySelector('.answer');
                    return answer &&
                           !answer.classList.contains('revealed') &&
                           card.style.display !== 'none';
                }});
                if (firstUnanswered) {{
                    currentQuestionIndex = allCards.indexOf(firstUnanswered);
                    firstUnanswered.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    updateNavButtons();
                }}
            }}
        }}

        // Swipe gesture support for mobile
        let touchStartX = 0;
        let touchStartY = 0;
        let touchEndX = 0;
        let touchEndY = 0;

        document.addEventListener('touchstart', e => {{
            touchStartX = e.changedTouches[0].screenX;
            touchStartY = e.changedTouches[0].screenY;
        }}, {{ passive: true }});

        document.addEventListener('touchend', e => {{
            touchEndX = e.changedTouches[0].screenX;
            touchEndY = e.changedTouches[0].screenY;
            handleSwipe();
        }}, {{ passive: true }});

        function handleSwipe() {{
            const swipeThreshold = 50;
            const deltaX = touchEndX - touchStartX;
            const deltaY = touchEndY - touchStartY;

            // Only trigger swipe if horizontal movement is greater than vertical
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > swipeThreshold) {{
                if (deltaX > 0) {{
                    // Swipe right - previous question
                    navigateQuestion(-1);
                }} else {{
                    // Swipe left - next question
                    navigateQuestion(1);
                }}
            }}
        }}

        // Update current question index on scroll
        let scrollTimeout;
        window.addEventListener('scroll', () => {{
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {{
                const visibleCards = allCards.filter(card => card.style.display !== 'none');
                const viewportCenter = window.innerHeight / 2;

                let closestCard = null;
                let closestDistance = Infinity;

                visibleCards.forEach((card, index) => {{
                    const rect = card.getBoundingClientRect();
                    const cardCenter = rect.top + rect.height / 2;
                    const distance = Math.abs(cardCenter - viewportCenter);

                    if (distance < closestDistance) {{
                        closestDistance = distance;
                        closestCard = card;
                        currentQuestionIndex = allCards.indexOf(card);
                    }}
                }});

                updateNavButtons();
            }}, 100);
        }}, {{ passive: true }});

        // Initialize nav buttons
        updateNavButtons();

        // Hamburger menu functions (mobile only)
        function toggleMenu() {{
            // Only toggle on mobile
            if (window.innerWidth <= 768) {{
                const menu = document.getElementById('indexMenu');
                const overlay = document.querySelector('.menu-overlay');
                menu.classList.toggle('open');
                overlay.classList.toggle('open');
            }}
        }}

        // Build index/table of contents
        function buildIndex() {{
            const sections = document.querySelectorAll('.section-header');
            const indexContent = document.getElementById('indexContent');

            sections.forEach(section => {{
                const sectionTitle = section.querySelector('h2').textContent;
                const sectionDiv = document.createElement('div');
                sectionDiv.className = 'index-section';

                const titleDiv = document.createElement('div');
                titleDiv.className = 'index-section-title';
                titleDiv.textContent = sectionTitle;
                sectionDiv.appendChild(titleDiv);

                // Find all question cards in this section
                let nextEl = section.nextElementSibling;
                while (nextEl && !nextEl.classList.contains('section-header')) {{
                    if (nextEl.classList.contains('question-card')) {{
                        const qNum = nextEl.querySelector('.q-number').textContent;
                        const question = nextEl.querySelector('.question').textContent;
                        const answer = nextEl.querySelector('.answer');

                        const link = document.createElement('a');
                        link.href = '#';
                        link.className = 'index-link';
                        if (answer && answer.classList.contains('revealed')) {{
                            link.classList.add('answered');
                        }}
                        link.textContent = qNum + ' ' + (question.length > 40 ? question.substring(0, 40) + '...' : question);
                        link.onclick = (e) => {{
                            e.preventDefault();
                            nextEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                            // Close menu only on mobile
                            if (window.innerWidth <= 768) {{
                                toggleMenu();
                            }}
                        }};
                        sectionDiv.appendChild(link);
                    }}
                    nextEl = nextEl.nextElementSibling;
                }}

                indexContent.appendChild(sectionDiv);
            }});
        }}

        // Build index on load
        buildIndex();
    </script>
</body>
</html>'''

    return html

async def main():
    print("Starting CCSE HTML generator...")

    # Generate explanations
    explanations = await generate_all_explanations()
    print(f"Total explanations: {len(explanations)}")

    # Generate HTML
    html = generate_html(explanations)

    output_file = "ccse_study.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
