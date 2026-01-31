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

        # Also prepare Spanish options to show in parenthesis for correct answer
        es_options_json_str = json.dumps([{
            'label': opt['label'],
            'text': opt['text']
        } for opt in es_options], ensure_ascii=False)
        es_options_js = js_and_html_escape(es_options_json_str)

        explanation_js = js_and_html_escape(explanation)

        # Build Russian options HTML for print
        ru_options_html = []
        for opt in ru_options:
            opt_class = 'correct' if opt['label'] == correct_label else ''
            ru_options_html.append(f'                    <div class="ru-option {opt_class}">{opt["label"]}) {opt["text"]}</div>')

        # Build Spanish options as plain text for print
        es_options_print_html = []
        for opt in es_options:
            opt_class = 'correct' if opt['label'] == correct_label else ''
            es_options_print_html.append(f'                    <div class="print-option {opt_class}">{opt["label"]}) {opt["text"]}</div>')

        html_questions.append(f'''
        <div class="question-card" id="q{q_num}" data-correct="{correct_label}">
            <div class="score-indicator not-attempted" id="indicator{q_num}" title="Sin responder">
                <span class="score-tooltip">Sin responder</span>
            </div>
            <div class="print-columns">
                <div class="print-spanish">
                    <div class="q-number">#{q_num}</div>
                    <div class="question">{es_q}</div>
                    <div class="print-options">
{''.join(es_options_print_html)}
                    </div>
                </div>
                <div class="print-russian">
                    <div class="q-number-ru">#{q_num}</div>
                    <div class="question-ru">{ru_q}</div>
                    <div class="ru-options">
{''.join(ru_options_html)}
                    </div>
                </div>
            </div>
            <div class="screen-only">
                <div class="q-number">#{q_num}</div>
                <div class="question">{es_q}</div>
                <div class="options-container">
                    {''.join(options_html)}
                    <div class="result" id="result{q_num}"></div>
                </div>
                <div class="buttons">
                    <button class="btn translate" onclick="toggleTranslate({q_num}, '{ru_q_js}', '{ru_options_js}', '{es_options_js}', '{correct_label}')">Перевод</button>
                    <button class="btn explain" onclick="toggleExplain({q_num}, '{explanation_js}')">Объяснение</button>
                </div>
                <div class="translation" id="trans{q_num}"></div>
                <div class="explanation" id="expl{q_num}"></div>
            </div>
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
    <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,500;0,8..60,600;1,8..60,400&display=optional" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700;900&family=Literata:opsz,wght@7..72,400;7..72,600;7..72,700&display=optional" rel="stylesheet">
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
            margin-bottom: 24px;
            text-align: center;
        }}

        .language-select {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            padding: 8px 12px;
            border-radius: 24px;
            cursor: pointer;
            font-size: 1rem;
            font-family: 'Source Serif 4', Georgia, serif;
            transition: all 0.2s ease;
        }}

        .language-select:hover {{
            background: var(--accent-soft);
            color: var(--accent);
            border-color: var(--accent);
        }}

        .language-select:focus {{
            outline: none;
            border-color: var(--accent);
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
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 4px;
            letter-spacing: -0.02em;
            color: var(--text);
        }}

        .subtitle {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            font-weight: 400;
            font-style: italic;
        }}

        .stats {{
            text-align: center;
            margin-bottom: 20px;
            padding: 10px 16px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            font-size: 0.95rem;
            color: var(--text-secondary);
        }}

        .search-box {{
            width: 100%;
            padding: 10px 16px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: var(--bg-card);
            color: var(--text);
            font-size: 1rem;
            font-family: 'Source Serif 4', Georgia, serif;
            margin-bottom: 24px;
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
            color: var(--text);
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
            display: flex;
            flex-direction: column;
        }}

        .sidebar-top {{
            padding: 20px;
            padding-top: 24px;
            border-bottom: 1px solid var(--border);
            flex-shrink: 0;
            overflow: visible;
        }}

        #indexContent {{
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }}

        .sidebar-bottom {{
            padding: 20px;
            border-top: 1px solid var(--border);
            flex-shrink: 0;
        }}

        .sidebar-icon-group {{
            display: flex;
            gap: 6px;
        }}

        .menu-overlay {{
            display: none;
        }}

        .index-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 16px;
            color: var(--text);
        }}


        .sidebar-btn {{
            width: 100%;
            padding: 12px 16px;
            border-radius: 10px;
            font-size: 0.95rem;
            text-align: left;
            border: 1px solid var(--border);
            background: var(--bg);
            color: var(--text);
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: 'Source Serif 4', Georgia, serif;
        }}

        .sidebar-btn:hover {{
            background: var(--accent-soft);
            color: var(--accent);
            border-color: var(--accent);
            transform: scale(1.05);
        }}

        .icon-btn {{
            text-align: center;
            font-size: 1.25rem;
            padding: 10px 12px;
            flex: 1;
            line-height: 1;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .sidebar-top .quiz-toggle {{
            background: var(--accent);
            border-color: var(--accent);
            font-weight: 600;
            margin-top: 16px;
            padding: 14px 20px;
            font-size: 1.05rem;
        }}

        .sidebar-top .quiz-toggle:hover {{
            background: #1d4ed8;
            border-color: #1d4ed8;
        }}

        .quiz-toggle-text {{
            color: white;
        }}

        .index-section {{
            margin-bottom: 16px;
        }}

        .index-section-title {{
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text);
            padding: 8px 12px;
            border-radius: 8px;
            background: var(--bg);
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s ease;
            user-select: none;
        }}

        .index-section-title:hover {{
            background: var(--accent-soft);
            color: var(--accent);
        }}

        .index-section-title::after {{
            content: '▼';
            font-size: 0.7rem;
            transition: transform 0.2s ease;
        }}

        .index-section-title.collapsed::after {{
            transform: rotate(-90deg);
        }}

        .index-section-content {{
            max-height: 1000px;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }}

        .index-section-content.collapsed {{
            max-height: 0;
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

        /* Hide print-columns on screen, show screen-only */
        .print-columns {{
            display: none;
        }}

        .screen-only {{
            display: block;
        }}

        /* Print mode styles - Two-column layout */
        @media print {{
            @page {{
                margin: 10mm 8mm;
                size: letter;
            }}

            body {{
                background: white;
                color: black;
                padding: 0;
                font-size: 6.5pt;
                line-height: 1.1;
            }}

            .header, .stats, .search-box, .bottom-nav, .header-controls, .theme-toggle, .menu-toggle, .index-menu, .menu-overlay {{
                display: none !important;
            }}

            body {{
                margin-left: 0;
            }}

            .container {{
                max-width: 100%;
                padding: 0 6mm;
            }}

            .section-header {{
                position: static;
                page-break-after: avoid;
                border-bottom: 1px solid #000;
                padding: 1px 0;
                margin: 6px 0 2px;
                background: white;
            }}

            .section-header h2 {{
                color: black;
                font-size: 9pt;
                margin: 0;
                font-weight: 600;
            }}

            .section-ru {{
                color: #666;
                font-size: 7pt;
                margin: 0;
            }}

            .question-card {{
                background: white;
                border: none;
                border-bottom: 0.5px solid #ddd;
                page-break-inside: avoid;
                break-inside: avoid;
                margin-bottom: 0;
                padding: 2px 0;
                box-shadow: none;
            }}

            .question-card.print-hide {{
                display: none;
            }}

            /* Hide screen-only content in print */
            .screen-only {{
                display: none !important;
            }}

            /* Show print columns */
            .print-columns {{
                display: flex;
                gap: 8mm;
                page-break-inside: avoid;
                break-inside: avoid;
            }}

            .print-spanish {{
                flex: 1;
                border-right: 0.5px solid #ccc;
                padding-right: 4mm;
            }}

            .print-russian {{
                flex: 1;
                padding-left: 4mm;
            }}

            .q-number, .q-number-ru {{
                color: #666;
                font-size: 6pt;
                margin-bottom: 0.5px;
                font-weight: 500;
                page-break-after: avoid;
            }}

            .question, .question-ru {{
                color: black;
                font-size: 7pt;
                margin-bottom: 1px;
                line-height: 1.15;
                font-weight: 600;
                page-break-after: avoid;
            }}

            .print-options, .ru-options {{
                margin-top: 1px;
            }}

            .print-option, .ru-option {{
                font-size: 6.5pt;
                line-height: 1.15;
                padding: 0.5px 0;
                margin-bottom: 0.5px;
                color: black;
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
                font-size: 1.75rem;
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
                margin-bottom: 20px;
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
                z-index: 250;
            }}

            .index-menu.open {{
                left: 0;
            }}

            .sidebar-top {{
                padding-top: 80px;
            }}

            .menu-toggle {{
                display: block;
            }}

            .icon-btn {{
                font-size: 1.4rem;
                padding: 12px;
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

        /* Quiz Mode Styles */
        .quiz-toggle {{
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

        .quiz-toggle:hover {{
            background: var(--accent-soft);
            color: var(--accent);
            border-color: var(--accent);
        }}

        /* Modal Overlay */
        .modal-overlay {{
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }}

        .modal-content {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px var(--shadow-hover);
        }}

        .modal-header {{
            padding: 24px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .modal-header h2 {{
            font-size: 1.75rem;
            font-weight: 600;
            color: var(--text);
            margin: 0;
        }}

        .modal-close {{
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-secondary);
            padding: 4px 8px;
            transition: all 0.2s ease;
            line-height: 1;
        }}

        .modal-close:hover {{
            color: var(--error);
            transform: scale(1.1);
        }}

        .modal-body {{
            padding: 24px;
        }}

        .config-section {{
            margin-bottom: 24px;
        }}

        .config-label {{
            display: block;
            font-weight: 600;
            margin-bottom: 12px;
            color: var(--text);
            font-size: 1.05rem;
        }}

        .radio-group {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .radio-option {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px;
            border: 2px solid var(--border);
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            background: var(--bg);
        }}

        .radio-option:hover {{
            border-color: var(--accent);
            background: var(--accent-soft);
        }}

        .radio-option input[type="radio"] {{
            width: 20px;
            height: 20px;
            cursor: pointer;
        }}

        .radio-option input[type="number"] {{
            width: 80px;
            padding: 6px 10px;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: var(--bg-card);
            color: var(--text);
            font-family: 'Source Serif 4', Georgia, serif;
            font-size: 1rem;
        }}

        .radio-option input[type="number"]:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .radio-option select {{
            padding: 6px 10px;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: var(--bg-card);
            color: var(--text);
            font-family: 'Source Serif 4', Georgia, serif;
            font-size: 1rem;
            cursor: pointer;
        }}

        .radio-option select:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .checkbox-option {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px;
            border: 2px solid var(--border);
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            background: var(--bg);
        }}

        .checkbox-option:hover {{
            border-color: var(--accent);
            background: var(--accent-soft);
        }}

        .checkbox-option input[type="checkbox"] {{
            width: 20px;
            height: 20px;
            cursor: pointer;
        }}

        .modal-footer {{
            padding: 24px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }}

        .btn-primary, .btn-secondary {{
            padding: 12px 24px;
            border-radius: 10px;
            font-size: 1rem;
            font-family: 'Source Serif 4', Georgia, serif;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            border: none;
        }}

        .btn-primary {{
            background: var(--accent);
            color: white;
        }}

        .btn-primary:hover {{
            background: #1d4ed8;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px var(--shadow-hover);
        }}

        .quiz-next-card-btn {{
            width: 100%;
            margin-top: 24px;
            padding: 16px 24px;
            font-size: 1.1rem;
        }}

        .btn-secondary {{
            background: var(--bg);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }}

        .btn-secondary:hover {{
            background: var(--bg-card);
            border-color: var(--text-secondary);
        }}

        .btn-secondary:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .btn-secondary:disabled:hover {{
            background: var(--bg);
            border-color: var(--border);
            transform: none;
        }}

        /* Quiz Mode Active State */
        body.quiz-mode .header,
        body.quiz-mode .stats,
        body.quiz-mode .search-box,
        body.quiz-mode .index-menu,
        body.quiz-mode .menu-toggle,
        body.quiz-mode .bottom-nav,
        body.quiz-mode .section-header {{
            display: none !important;
        }}

        body.quiz-mode {{
            margin-left: 0;
        }}

        /* Quiz Header */
        .quiz-header {{
            position: sticky;
            top: 0;
            background: var(--bg-card);
            border-bottom: 2px solid var(--accent);
            padding: 16px 24px;
            z-index: 500;
            display: none;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px var(--shadow);
        }}

        body.quiz-mode .quiz-header {{
            display: flex;
        }}

        .quiz-timer {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text);
            font-variant-numeric: tabular-nums;
        }}

        .quiz-timer.warning {{
            color: #ef4444;
            animation: pulse 1s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.6;
            }}
        }}

        .quiz-progress {{
            font-size: 1.125rem;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .progress-bar {{
            width: 150px;
            height: 8px;
            background: var(--border);
            border-radius: 4px;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            background: var(--accent);
            transition: width 0.3s ease;
        }}

        .quiz-actions {{
            display: flex;
            gap: 8px;
        }}

        /* Quiz Option States */
        .option.selected-quiz {{
            border-color: var(--accent);
            background: var(--accent-soft);
        }}

        .option.flagged {{
            border-color: #f59e0b;
            background: #fff7ed;
        }}

        [data-theme="dark"] .option.flagged {{
            background: #451a03;
        }}

        body.quiz-mode .option:hover {{
            border-color: var(--accent);
            background: var(--accent-soft);
        }}

        body.quiz-mode .buttons {{
            display: none;
        }}

        /* Flag Button */
        .flag-btn {{
            padding: 8px 12px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.25rem;
            transition: all 0.2s ease;
        }}

        .flag-btn:hover {{
            border-color: #f59e0b;
            background: #fff7ed;
        }}

        .flag-btn.active {{
            border-color: #f59e0b;
            background: #fff7ed;
        }}

        [data-theme="dark"] .flag-btn:hover,
        [data-theme="dark"] .flag-btn.active {{
            background: #451a03;
        }}

        /* Results Page - Editorial Magazine Aesthetic */

        .results-page {{
            display: none;
        }}

        body.quiz-results .results-page {{
            display: block;
        }}

        body.quiz-results .container,
        body.quiz-results .quiz-header,
        body.quiz-results .index-menu,
        body.quiz-results .menu-toggle,
        body.quiz-results .header,
        body.quiz-results .stats,
        body.quiz-results .search-box,
        body.quiz-results .bottom-nav,
        body.quiz-results .section-header,
        body.quiz-results .menu-overlay {{
            display: none !important;
        }}

        body.quiz-results {{
            margin-left: 0;
            padding: 40px 20px;
        }}

        .results-container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 0;
        }}

        .results-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 0;
            margin-top: 48px;
            margin-bottom: 32px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            position: relative;
            overflow: hidden;
        }}

        .results-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 8px;
            height: 100%;
            background: linear-gradient(180deg, #065f46 0%, #059669 50%, #10b981 100%);
        }}

        .results-card.failed::before {{
            background: linear-gradient(180deg, #b45309 0%, #d97706 50%, #f59e0b 100%);
        }}

        .results-hero {{
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            padding: 32px;
            gap: 28px;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .results-content {{
            animation: slideInLeft 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        @keyframes slideInLeft {{
            from {{
                opacity: 0;
                transform: translateX(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        .results-kicker {{
            font-family: 'Source Serif 4', Georgia, serif;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--text-tertiary);
            margin-bottom: 12px;
            font-weight: 600;
        }}

        .results-status {{
            font-family: 'Source Serif 4', Georgia, serif;
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1.1;
            letter-spacing: -0.02em;
            margin-bottom: 16px;
            color: #065f46;
        }}

        .results-status.failed {{
            color: #b45309;
        }}

        [data-theme="dark"] .results-status {{
            color: #10b981;
        }}

        [data-theme="dark"] .results-status.failed {{
            color: #f59e0b;
        }}

        .results-subtitle {{
            font-family: 'Source Serif 4', Georgia, serif;
            font-size: 1rem;
            line-height: 1.5;
            color: var(--text-secondary);
            margin-bottom: 20px;
            max-width: 420px;
        }}

        .results-meta {{
            display: flex;
            gap: 28px;
            font-family: 'Source Serif 4', Georgia, serif;
        }}

        .results-meta-item {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .results-meta-label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--text-tertiary);
            font-weight: 600;
        }}

        .results-meta-value {{
            font-size: 1.125rem;
            font-weight: 700;
            color: var(--text);
        }}

        .results-score-section {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            animation: scaleIn 1s cubic-bezier(0.16, 1, 0.3, 1) 0.3s both;
        }}

        @keyframes scaleIn {{
            from {{
                opacity: 0;
                transform: scale(0.8);
            }}
            to {{
                opacity: 1;
                transform: scale(1);
            }}
        }}

        .results-score-circle {{
            position: relative;
            width: 160px;
            height: 160px;
            margin-bottom: 12px;
        }}

        .results-score-circle svg {{
            transform: rotate(-90deg);
            filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.08));
        }}

        .results-circle-bg {{
            fill: none;
            stroke: rgba(0, 0, 0, 0.05);
            stroke-width: 3;
        }}

        [data-theme="dark"] .results-circle-bg {{
            stroke: rgba(255, 255, 255, 0.08);
        }}

        .results-circle-progress {{
            fill: none;
            stroke: url(#scoreGradient);
            stroke-width: 3;
            stroke-linecap: round;
            transition: stroke-dashoffset 2s cubic-bezier(0.16, 1, 0.3, 1) 0.5s;
        }}

        .results-score {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }}

        .results-score-number {{
            font-family: 'Source Serif 4', Georgia, serif;
            font-size: 3rem;
            font-weight: 700;
            line-height: 1;
            letter-spacing: -0.02em;
            color: #065f46;
            font-variant-numeric: tabular-nums;
        }}

        .results-score-number.failed {{
            color: #b45309;
        }}

        [data-theme="dark"] .results-score-number {{
            color: #10b981;
        }}

        [data-theme="dark"] .results-score-number.failed {{
            color: #f59e0b;
        }}

        .results-score-label {{
            font-family: 'Source Serif 4', Georgia, serif;
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--text-tertiary);
            font-weight: 600;
            margin-top: 4px;
        }}

        .section-performance {{
            padding: 32px;
            animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.6s both;
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .section-performance h3 {{
            font-family: 'Source Serif 4', Georgia, serif;
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.01em;
            margin-bottom: 24px;
            color: var(--text);
        }}

        .performance-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}

        .performance-bar {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 0;
            background: transparent;
            border-radius: 0;
            transition: none;
            animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
        }}

        .performance-bar:nth-child(1) {{ animation-delay: 0.7s; }}
        .performance-bar:nth-child(2) {{ animation-delay: 0.8s; }}
        .performance-bar:nth-child(3) {{ animation-delay: 0.9s; }}
        .performance-bar:nth-child(4) {{ animation-delay: 1s; }}
        .performance-bar:nth-child(5) {{ animation-delay: 1.1s; }}

        .performance-bar:hover {{
            transform: none;
        }}

        .performance-label {{
            font-family: 'Source Serif 4', Georgia, serif;
            flex: none;
            width: 100%;
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.85rem;
            line-height: 1.3;
        }}

        .performance-track {{
            flex: none;
            width: 100%;
            height: 6px;
            background: var(--border);
            border-radius: 3px;
            overflow: hidden;
            position: relative;
            box-shadow: none;
        }}

        .performance-fill {{
            height: 100%;
            background: #065f46;
            border-radius: 3px;
            transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1) 0.8s;
            position: relative;
            overflow: hidden;
        }}

        [data-theme="dark"] .performance-fill {{
            background: #10b981;
        }}

        .performance-fill::after {{
            display: none;
        }}

        .performance-percentage {{
            flex: none;
            width: 100%;
            text-align: center;
            font-family: 'Source Serif 4', Georgia, serif;
            font-weight: 700;
            font-size: 1.125rem;
            color: #065f46;
            font-variant-numeric: tabular-nums;
        }}

        [data-theme="dark"] .performance-percentage {{
            color: #10b981;
        }}

        .results-actions {{
            display: flex;
            gap: 16px;
            padding: 40px 40px 40px 56px;
            flex-wrap: wrap;
            animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 1.2s both;
        }}

        .results-actions .btn-primary,
        .results-actions .btn-secondary {{
            font-family: 'Literata', Georgia, serif;
            padding: 16px 32px;
            font-size: 0.95rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            border-radius: 0;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .results-actions .btn-primary {{
            background: #065f46;
            border: 2px solid #065f46;
        }}

        .results-actions .btn-primary:hover {{
            background: #064e3b;
            border-color: #064e3b;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(6, 95, 70, 0.3);
        }}

        [data-theme="dark"] .results-actions .btn-primary {{
            background: #10b981;
            border-color: #10b981;
            color: #1c1917;
        }}

        [data-theme="dark"] .results-actions .btn-primary:hover {{
            background: #059669;
            border-color: #059669;
            box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
        }}

        .results-actions .btn-secondary {{
            background: transparent;
            color: #1c1917;
            border: 2px solid rgba(0, 0, 0, 0.15);
        }}

        .results-actions .btn-secondary:hover {{
            border-color: #1c1917;
            background: rgba(0, 0, 0, 0.02);
            transform: translateY(-2px);
        }}

        [data-theme="dark"] .results-actions .btn-secondary {{
            color: #fafaf9;
            border-color: rgba(255, 255, 255, 0.15);
        }}

        [data-theme="dark"] .results-actions .btn-secondary:hover {{
            border-color: #fafaf9;
            background: rgba(255, 255, 255, 0.05);
        }}

        /* Question Review */
        .question-review {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
        }}

        .review-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }}

        .review-status {{
            font-size: 1.5rem;
            font-weight: 600;
        }}

        .review-status.correct-review {{
            color: var(--success);
        }}

        .review-status.incorrect-review {{
            color: var(--error);
        }}

        .review-question {{
            font-size: 1.125rem;
            margin-bottom: 16px;
            color: var(--text);
        }}

        .review-answers {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .review-answer {{
            padding: 12px 16px;
            border-radius: 10px;
            font-size: 1rem;
        }}

        .review-answer.user-correct {{
            background: var(--success-soft);
            border: 2px solid var(--success);
            color: var(--success);
            font-weight: 600;
        }}

        .review-answer.user-incorrect {{
            background: var(--error-soft);
            border: 2px solid var(--error);
            color: var(--error);
            text-decoration: line-through;
        }}

        .review-answer.correct-answer {{
            background: var(--success-soft);
            border: 2px solid var(--success);
            color: var(--success);
            font-weight: 600;
        }}

        /* Mobile quiz mode */
        @media (max-width: 768px) {{
            .quiz-header {{
                padding: 12px 16px;
                flex-wrap: wrap;
            }}

            .quiz-timer {{
                font-size: 1.25rem;
            }}

            .quiz-progress {{
                font-size: 1rem;
            }}

            .progress-bar {{
                width: 100px;
            }}

            .results-container {{
                padding: 0;
            }}

            .results-hero {{
                grid-template-columns: 1fr;
                padding: 32px 24px;
                gap: 28px;
            }}

            .results-status {{
                font-size: 3rem;
            }}

            .results-subtitle {{
                font-size: 1rem;
            }}

            .results-meta {{
                flex-direction: column;
                gap: 20px;
            }}

            .results-score-circle {{
                width: 160px;
                height: 160px;
            }}

            .results-score-number {{
                font-size: 3.5rem;
            }}

            .results-score-label {{
                font-size: 0.7rem;
            }}

            .section-performance {{
                padding: 32px 24px;
            }}

            .section-performance h3 {{
                font-size: 1.75rem;
                margin-bottom: 28px;
            }}

            .performance-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}

            .results-actions {{
                padding: 32px 24px;
                flex-direction: column;
            }}

            .results-card {{
                border-radius: 12px;
            }}

            .results-actions .btn-primary,
            .results-actions .btn-secondary {{
                width: 100%;
                padding: 18px 24px;
            }}

            .modal-content {{
                width: 95%;
                max-height: 85vh;
            }}

            .performance-label {{
                flex: 0 0 120px;
                font-size: 0.9rem;
            }}

            .performance-percentage {{
                flex: 0 0 50px;
                font-size: 0.9rem;
            }}
        }}

        /* Practice Mode Button */
        .practice-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
            position: relative;
            overflow: visible;
            animation: pulse-glow 2s infinite;
            margin-top: 12px;
        }}

        .practice-btn:hover {{
            background: linear-gradient(135deg, #5a6fd6 0%, #6a4190 100%);
            color: white;
            transform: translateY(-1px);
        }}

        .practice-btn .badge {{
            position: absolute;
            top: -8px;
            right: 8px;
            background: #ef4444;
            color: white;
            font-size: 0.7rem;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 10px;
            min-width: 18px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}

        .practice-btn .badge.empty {{
            display: none;
        }}

        @keyframes pulse-glow {{
            0%, 100% {{ box-shadow: 0 0 15px rgba(102, 126, 234, 0.4); }}
            50% {{ box-shadow: 0 0 25px rgba(102, 126, 234, 0.6); }}
        }}

        /* Stats Panel */
        .stats-panel {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            margin: 16px;
            margin-top: 0;
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .stats-panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            cursor: pointer;
            user-select: none;
            font-weight: 600;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}

        .stats-panel-header:hover {{
            background: var(--accent-soft);
        }}

        .stats-panel-toggle {{
            transition: transform 0.3s ease;
        }}

        .stats-panel.collapsed .stats-panel-toggle {{
            transform: rotate(-90deg);
        }}

        .stats-panel.collapsed .stats-panel-content {{
            display: none;
        }}

        .stats-panel-content {{
            padding: 0 16px 12px;
        }}

        .stats-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid var(--border);
            font-size: 0.85rem;
        }}

        .stats-row:last-child {{
            border-bottom: none;
        }}

        .stats-label {{
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .stats-value {{
            font-weight: 600;
            color: var(--text);
        }}

        .stats-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }}

        .stats-dot.needs-practice {{ background: #f97316; }}
        .stats-dot.mastered {{ background: #22c55e; }}
        .stats-dot.not-attempted {{ background: #9ca3af; }}

        .stats-reset-btn {{
            width: 100%;
            margin-top: 8px;
            padding: 8px;
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-tertiary);
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .stats-reset-btn:hover {{
            background: var(--error-soft);
            border-color: var(--error);
            color: var(--error);
        }}

        /* Score Indicators on Cards */
        .question-card {{
            position: relative;
        }}

        .score-indicator {{
            position: absolute;
            top: 12px;
            right: 12px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            cursor: help;
            transition: transform 0.2s ease;
            z-index: 5;
        }}

        .score-indicator:hover {{
            transform: scale(1.3);
        }}

        .score-indicator.struggling {{ background: #ef4444; }}
        .score-indicator.needs-work {{ background: #f97316; }}
        .score-indicator.learning {{ background: #eab308; }}
        .score-indicator.mastered {{ background: #22c55e; }}
        .score-indicator.not-attempted {{ background: #9ca3af; }}

        .score-tooltip {{
            position: absolute;
            top: 100%;
            right: 0;
            margin-top: 4px;
            padding: 4px 8px;
            background: var(--text);
            color: var(--bg);
            font-size: 0.75rem;
            border-radius: 4px;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s ease;
            z-index: 10;
        }}

        .score-indicator:hover .score-tooltip {{
            opacity: 1;
            visibility: visible;
        }}

        /* Practice Mode Styles */
        body.practice-mode .question-card {{
            display: none;
        }}

        body.practice-mode .question-card.practice-visible {{
            display: block;
        }}

        body.practice-mode .section-header {{
            display: none;
        }}

        body.practice-mode .search-box,
        body.practice-mode .stats {{
            display: none;
        }}

        .practice-header {{
            display: none;
            position: fixed;
            top: 0;
            left: 280px;
            right: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 24px;
            z-index: 100;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}

        body.practice-mode .practice-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        body.practice-mode .container {{
            padding-top: 80px;
        }}

        .practice-info {{
            display: flex;
            align-items: center;
            gap: 24px;
        }}

        .practice-title {{
            font-weight: 700;
            font-size: 1.1rem;
        }}

        .practice-progress {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}

        .practice-actions {{
            display: flex;
            gap: 12px;
        }}

        .practice-actions button {{
            padding: 8px 16px;
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            border-radius: 8px;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }}

        .practice-actions button:hover {{
            background: rgba(255,255,255,0.3);
        }}

        .practice-congrats {{
            text-align: center;
            padding: 60px 24px;
            color: var(--text-secondary);
        }}

        .practice-congrats h2 {{
            color: var(--success);
            margin-bottom: 16px;
            font-size: 1.5rem;
        }}

        .practice-congrats p {{
            margin-bottom: 24px;
        }}

        /* Mobile adjustments for practice mode */
        @media (max-width: 768px) {{
            .practice-header {{
                left: 0;
                padding: 12px 16px;
            }}

            .practice-info {{
                flex-direction: column;
                align-items: flex-start;
                gap: 4px;
            }}

            .practice-title {{
                font-size: 1rem;
            }}

            .practice-progress {{
                font-size: 0.8rem;
            }}
        }}

        @media print {{
            .score-indicator {{
                display: none;
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
        <div class="sidebar-top">
            <div class="index-title">Оглавление</div>
            <button class="quiz-toggle sidebar-btn" id="quizToggleBtn" onclick="toggleQuizMode()">
                <span class="quiz-toggle-text" id="quizToggleText">Режим Экзамена</span>
            </button>
            <button class="sidebar-btn practice-btn" id="practiceBtn" onclick="startFocusedPractice()">
                <span id="practiceBtnText">Практика ошибок</span>
                <span class="badge empty" id="practiceBadge">0</span>
            </button>
        </div>
        <div class="stats-panel" id="statsPanel">
            <div class="stats-panel-header" onclick="toggleStatsPanel()">
                <span id="statsPanelTitle">Статистика</span>
                <span class="stats-panel-toggle">▼</span>
            </div>
            <div class="stats-panel-content">
                <div class="stats-row">
                    <span class="stats-label"><span class="stats-dot needs-practice"></span><span id="statsNeedsPracticeLabel">Нужна практика</span></span>
                    <span class="stats-value" id="statsNeedsPractice">0</span>
                </div>
                <div class="stats-row">
                    <span class="stats-label"><span class="stats-dot mastered"></span><span id="statsMasteredLabel">Освоено</span></span>
                    <span class="stats-value" id="statsMastered">0</span>
                </div>
                <div class="stats-row">
                    <span class="stats-label"><span class="stats-dot not-attempted"></span><span id="statsNotAttemptedLabel">Без ответа</span></span>
                    <span class="stats-value" id="statsNotAttempted">0</span>
                </div>
                <button class="stats-reset-btn" onclick="resetAllScores()" id="statsResetBtn">Сбросить статистику</button>
            </div>
        </div>
        <div id="indexContent"></div>
        <div class="sidebar-bottom">
            <div class="sidebar-icon-group">
                <button class="language-btn sidebar-btn icon-btn" onclick="cycleLanguage()" title="Язык">🇷🇺</button>
                <button class="print-btn sidebar-btn icon-btn" onclick="window.print()" title="Печать всех">🖨️</button>
                <button class="theme-toggle sidebar-btn icon-btn" onclick="toggleTheme()" title="Темный режим">🌙</button>
            </div>
        </div>
    </div>

    <!-- Quiz Configuration Modal -->
    <div class="modal-overlay" id="quizModal" style="display: none;">
        <div class="modal-content quiz-config">
            <div class="modal-header">
                <h2 id="quizModalTitle">Configurar Examen</h2>
                <button class="modal-close" onclick="closeQuizConfig()">✕</button>
            </div>
            <div class="modal-body">
                <div class="config-section">
                    <label class="config-label" id="questionSelectionLabel">Selección de preguntas:</label>
                    <div class="radio-group">
                        <label class="radio-option">
                            <input type="radio" name="questionMode" value="all" checked>
                            <span id="fullExamLabel">Examen completo (300 preguntas)</span>
                        </label>
                        <label class="radio-option">
                            <input type="radio" name="questionMode" value="section">
                            <span id="bySectionLabel">Por sección:</span>
                            <select id="sectionSelect" disabled>
                                <option value="1">TAREA 1 (120 preguntas)</option>
                                <option value="2">TAREA 2 (36 preguntas)</option>
                                <option value="3">TAREA 3 (24 preguntas)</option>
                                <option value="4">TAREA 4 (36 preguntas)</option>
                                <option value="5">TAREA 5 (84 preguntas)</option>
                            </select>
                        </label>
                        <label class="radio-option">
                            <input type="radio" name="questionMode" value="custom">
                            <span id="quickPracticeLabel">Práctica rápida:</span>
                            <input type="number" id="customCount" min="1" max="300" value="25" disabled>
                            <span id="questionsLabel">preguntas</span>
                        </label>
                    </div>
                </div>

                <div class="config-section">
                    <label class="checkbox-option">
                        <input type="checkbox" id="randomOrder">
                        <span id="randomOrderLabel">Orden aleatorio</span>
                    </label>
                </div>

                <div class="config-section">
                    <label class="config-label" id="timerLabel">Temporizador:</label>
                    <div class="radio-group">
                        <label class="radio-option">
                            <input type="radio" name="timerMode" value="none" checked>
                            <span id="noTimerLabel">Sin temporizador</span>
                        </label>
                        <label class="radio-option">
                            <input type="radio" name="timerMode" value="full">
                            <span id="fullTimerLabel">45 minutos (examen completo)</span>
                        </label>
                        <label class="radio-option">
                            <input type="radio" name="timerMode" value="proportional">
                            <span id="proportionalTimerLabel">Proporcional al número de preguntas</span>
                        </label>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" id="quizCancelBtn" onclick="closeQuizConfig()">Cancelar</button>
                <button class="btn-primary" id="quizStartBtn" onclick="startQuizFromConfig()">Iniciar Examen</button>
            </div>
        </div>
    </div>

    <!-- Quiz Header (shown only in quiz mode) -->
    <div class="quiz-header" id="quizHeader">
        <div class="quiz-timer" id="quizTimer"></div>
        <div class="quiz-progress">
            <span id="quizProgressText">Pregunta 1/25 (0 respondidas)</span>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill" style="width: 0%"></div>
            </div>
        </div>
        <div class="quiz-actions">
            <button class="btn-secondary" onclick="navigateQuizQuestion(-1)" id="quizPrevBtn">← Anterior</button>
            <button class="btn-secondary" onclick="navigateQuizQuestion(1)" id="quizNextBtn">Siguiente →</button>
            <button class="btn-secondary" onclick="submitQuiz()" id="quizFinishBtn">Terminar Examen</button>
            <button class="btn-secondary" onclick="exitQuiz()" id="quizExitBtn">Salir</button>
        </div>
    </div>

    <!-- Practice Header (shown only in practice mode) -->
    <div class="practice-header" id="practiceHeader">
        <div class="practice-info">
            <span class="practice-title" id="practiceTitle">Практика ошибок</span>
            <span class="practice-progress" id="practiceProgressText">Осталось: 0 вопросов</span>
        </div>
        <div class="practice-actions">
            <button onclick="skipPracticeQuestion()" id="practiceSkipBtn">Пропустить</button>
            <button onclick="exitFocusedPractice()" id="practiceExitBtn">Выход</button>
        </div>
    </div>

    <!-- Results Page (shown only after quiz completion) -->
    <div class="results-page" id="resultsPage">
        <!-- Content will be dynamically generated -->
    </div>

    <div class="container">
        <div class="header">
            <h1>CCSE 2026</h1>
            <p class="subtitle">Вопросы для гражданства Испании</p>
        </div>

        <div class="stats">
            <span id="revealed">0</span> / {len(questions)} вопросов отвечено
        </div>

        <input type="text" class="search-box" placeholder="Поиск вопроса..." oninput="filterQuestions(this.value)">

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

        // All question numbers for quiz mode
        const allQuestionNumbers = {json.dumps(sorted(questions.keys()))};

        // Quiz toggle button update
        function updateQuizToggleButton() {{
            const toggleBtn = document.getElementById('quizToggleBtn');
            const toggleText = document.getElementById('quizToggleText');

            if (!toggleBtn || !toggleText) return;

            // Check if quizMode is defined and active
            const isQuizActive = typeof quizMode !== 'undefined' && (quizMode.active || document.body.classList.contains('quiz-mode'));

            if (isQuizActive) {{
                // In quiz mode - show "Study Mode" button
                toggleText.textContent = t('studyMode');
                toggleBtn.onclick = exitQuiz;
            }} else {{
                // In study mode - show "Quiz Mode" button
                toggleText.textContent = t('quizMode');
                toggleBtn.onclick = openQuizConfig;
            }}
        }}

        function toggleQuizMode() {{
            if (typeof quizMode !== 'undefined' && (quizMode.active || document.body.classList.contains('quiz-mode'))) {{
                exitQuiz();
            }} else {{
                openQuizConfig();
            }}
        }}

        // Language translations
        const translations = {{
            es: {{
                // Header
                title: 'CCSE 2026',
                subtitle: 'Preguntas de Ciudadanía Española',
                questionsAnswered: 'preguntas respondidas',
                searchPlaceholder: 'Buscar pregunta...',

                // Buttons
                quizMode: 'Modo Examen',
                printAll: 'Imprimir todo',
                printUnanswered: 'Imprimir sin responder',
                darkMode: 'Modo oscuro',
                lightMode: 'Modo claro',
                translate: 'Перевод',
                explain: 'Объяснение',

                // Quiz config modal
                configureExam: 'Configurar Examen',
                questionSelection: 'Selección de preguntas:',
                fullExam: 'Examen completo (300 preguntas)',
                bySection: 'Por sección:',
                quickPractice: 'Práctica rápida:',
                questions: 'preguntas',
                randomOrder: 'Orden aleatorio',
                timer: 'Temporizador:',
                noTimer: 'Sin temporizador',
                fullTimer: '45 minutos (examen completo)',
                proportionalTimer: 'Proporcional al número de preguntas',
                cancel: 'Cancelar',
                startExam: 'Iniciar Examen',

                // Quiz interface
                question: 'Pregunta',
                answered: 'respondidas',
                previous: 'Anterior',
                next: 'Siguiente',
                finishExam: 'Terminar Examen',
                exit: 'Salir',

                // Results
                passed: 'APROBADO',
                failed: 'NO APROBADO',
                correctAnswers: 'respuestas correctas',
                time: 'Tiempo:',
                sectionPerformance: 'Rendimiento por sección',
                reviewQuestions: 'Revisar Preguntas',
                newExam: 'Nuevo Examen',
                studyMode: 'Modo Estudio',
                detailedReview: 'Revisión Detallada',
                correct: 'Correcta',
                incorrect: 'Incorrecta',
                yourAnswer: 'Tu respuesta:',
                correctAnswer: 'Respuesta correcta:',
                notAnswered: 'No respondida',

                // Navigation
                index: 'Índice',
                home: 'Inicio',
                nextUnanswered: 'Próxima',

                // Alerts
                confirmFinish: '¿Estás seguro de que quieres terminar el examen?',
                unansweredQuestions: 'Tienes',
                questionsUnanswered: 'pregunta(s) sin responder.',
                confirmExit: '¿Seguro que quieres salir del examen? Se perderá tu progreso.',
                timeExpired: '¡Tiempo agotado! El examen se enviará automáticamente.',
                continueExam: '¿Quieres continuar el examen anterior?',
                continueButton: 'Continuar',
                startNewButton: 'Empezar nuevo',
                examTimeExpired: 'El tiempo del examen ha expirado.',
                confirmLeave: '¿Seguro que quieres salir? Se guardará tu progreso.',

                // Practice mode
                practiceMode: 'Práctica de errores',
                practiceTitle: 'Práctica de errores',
                practiceRemaining: 'Quedan',
                practiceQuestions: 'preguntas',
                practiceSkip: 'Saltar',
                practiceExit: 'Salir',
                practiceCongrats: '¡Felicidades!',
                practiceCongratsText: 'Has dominado todas las preguntas difíciles.',
                practiceNoQuestions: 'No hay preguntas para practicar.',
                practiceNoQuestionsText: 'Responde algunas preguntas primero para ver cuáles necesitas practicar.',
                practiceBackToStudy: 'Volver a estudiar',

                // Stats panel
                statsTitle: 'Estadísticas',
                needsPractice: 'Necesita práctica',
                mastered: 'Dominadas',
                notAttempted: 'Sin intentar',
                resetStats: 'Reiniciar estadísticas',
                confirmReset: '¿Estás seguro de que quieres reiniciar todas las estadísticas? Esta acción no se puede deshacer.',

                // Score indicators
                scoreStruggling: 'Difícil',
                scoreNeedsWork: 'Necesita práctica',
                scoreLearning: 'Aprendiendo',
                scoreMastered: 'Dominada',
                scoreNotAttempted: 'Sin responder'
            }},
            en: {{
                // Header
                title: 'CCSE 2026',
                subtitle: 'Spanish Citizenship Questions',
                questionsAnswered: 'questions answered',
                searchPlaceholder: 'Search question...',

                // Buttons
                quizMode: 'Exam Mode',
                printAll: 'Print all',
                printUnanswered: 'Print unanswered',
                darkMode: 'Dark mode',
                lightMode: 'Light mode',
                translate: 'Перевод',
                explain: 'Объяснение',

                // Quiz config modal
                configureExam: 'Configure Exam',
                questionSelection: 'Question selection:',
                fullExam: 'Full exam (300 questions)',
                bySection: 'By section:',
                quickPractice: 'Quick practice:',
                questions: 'questions',
                randomOrder: 'Random order',
                timer: 'Timer:',
                noTimer: 'No timer',
                fullTimer: '45 minutes (full exam)',
                proportionalTimer: 'Proportional to number of questions',
                cancel: 'Cancel',
                startExam: 'Start Exam',

                // Quiz interface
                question: 'Question',
                answered: 'answered',
                previous: 'Previous',
                next: 'Next',
                finishExam: 'Finish Exam',
                exit: 'Exit',

                // Results
                passed: 'PASSED',
                failed: 'FAILED',
                correctAnswers: 'correct answers',
                time: 'Time:',
                sectionPerformance: 'Performance by section',
                reviewQuestions: 'Review Questions',
                newExam: 'New Exam',
                studyMode: 'Study Mode',
                detailedReview: 'Detailed Review',
                correct: 'Correct',
                incorrect: 'Incorrect',
                yourAnswer: 'Your answer:',
                correctAnswer: 'Correct answer:',
                notAnswered: 'Not answered',

                // Navigation
                index: 'Index',
                home: 'Home',
                nextUnanswered: 'Next',

                // Alerts
                confirmFinish: 'Are you sure you want to finish the exam?',
                unansweredQuestions: 'You have',
                questionsUnanswered: 'unanswered question(s).',
                confirmExit: 'Are you sure you want to exit the exam? Your progress will be lost.',
                timeExpired: 'Time expired! The exam will be submitted automatically.',
                continueExam: 'Do you want to continue the previous exam?',
                continueButton: 'Continue',
                startNewButton: 'Start New',
                examTimeExpired: 'The exam time has expired.',
                confirmLeave: 'Are you sure you want to leave? Your progress will be saved.',

                // Practice mode
                practiceMode: 'Practice Mistakes',
                practiceTitle: 'Practice Mistakes',
                practiceRemaining: 'Remaining',
                practiceQuestions: 'questions',
                practiceSkip: 'Skip',
                practiceExit: 'Exit',
                practiceCongrats: 'Congratulations!',
                practiceCongratsText: 'You have mastered all the difficult questions.',
                practiceNoQuestions: 'No questions to practice.',
                practiceNoQuestionsText: 'Answer some questions first to see which ones you need to practice.',
                practiceBackToStudy: 'Back to study',

                // Stats panel
                statsTitle: 'Statistics',
                needsPractice: 'Needs practice',
                mastered: 'Mastered',
                notAttempted: 'Not attempted',
                resetStats: 'Reset statistics',
                confirmReset: 'Are you sure you want to reset all statistics? This action cannot be undone.',

                // Score indicators
                scoreStruggling: 'Struggling',
                scoreNeedsWork: 'Needs work',
                scoreLearning: 'Learning',
                scoreMastered: 'Mastered',
                scoreNotAttempted: 'Not answered'
            }},
            ru: {{
                // Header
                title: 'CCSE 2026',
                subtitle: 'Вопросы для гражданства Испании',
                questionsAnswered: 'вопросов отвечено',
                searchPlaceholder: 'Поиск вопроса...',

                // Buttons
                quizMode: 'Режим Экзамена',
                printAll: 'Печать всех',
                printUnanswered: 'Печать неотвеченных',
                darkMode: 'Темный режим',
                lightMode: 'Светлый режим',
                translate: 'Перевод',
                explain: 'Объяснение',

                // Quiz config modal
                configureExam: 'Настроить Экзамен',
                questionSelection: 'Выбор вопросов:',
                fullExam: 'Полный экзамен (300 вопросов)',
                bySection: 'По разделу:',
                quickPractice: 'Быстрая практика:',
                questions: 'вопросов',
                randomOrder: 'Случайный порядок',
                timer: 'Таймер:',
                noTimer: 'Без таймера',
                fullTimer: '45 минут (полный экзамен)',
                proportionalTimer: 'Пропорционально количеству вопросов',
                cancel: 'Отмена',
                startExam: 'Начать Экзамен',

                // Quiz interface
                question: 'Вопрос',
                answered: 'отвечено',
                previous: 'Назад',
                next: 'Далее',
                finishExam: 'Завершить Экзамен',
                exit: 'Выход',

                // Results
                passed: 'СДАЛ',
                failed: 'НЕ СДАЛ',
                correctAnswers: 'правильных ответов',
                time: 'Время:',
                sectionPerformance: 'Результаты по разделам',
                reviewQuestions: 'Просмотреть Вопросы',
                newExam: 'Новый Экзамен',
                studyMode: 'Режим Обучения',
                detailedReview: 'Подробный Обзор',
                correct: 'Правильно',
                incorrect: 'Неправильно',
                yourAnswer: 'Ваш ответ:',
                correctAnswer: 'Правильный ответ:',
                notAnswered: 'Не отвечено',

                // Navigation
                index: 'Оглавление',
                home: 'Главная',
                nextUnanswered: 'Следующий',

                // Alerts
                confirmFinish: 'Вы уверены, что хотите завершить экзамен?',
                unansweredQuestions: 'У вас',
                questionsUnanswered: 'неотвеченных вопроса(ов).',
                confirmExit: 'Вы уверены, что хотите выйти из экзамена? Ваш прогресс будет потерян.',
                timeExpired: 'Время истекло! Экзамен будет отправлен автоматически.',
                continueExam: 'Хотите продолжить предыдущий экзамен?',
                continueButton: 'Продолжить',
                startNewButton: 'Начать новый',
                examTimeExpired: 'Время экзамена истекло.',
                confirmLeave: 'Вы уверены, что хотите выйти? Ваш прогресс будет сохранен.',

                // Practice mode
                practiceMode: 'Практика ошибок',
                practiceTitle: 'Практика ошибок',
                practiceRemaining: 'Осталось',
                practiceQuestions: 'вопросов',
                practiceSkip: 'Пропустить',
                practiceExit: 'Выход',
                practiceCongrats: 'Поздравляем!',
                practiceCongratsText: 'Вы освоили все сложные вопросы.',
                practiceNoQuestions: 'Нет вопросов для практики.',
                practiceNoQuestionsText: 'Сначала ответьте на несколько вопросов, чтобы увидеть, какие нужно практиковать.',
                practiceBackToStudy: 'Вернуться к учебе',

                // Stats panel
                statsTitle: 'Статистика',
                needsPractice: 'Нужна практика',
                mastered: 'Освоено',
                notAttempted: 'Без ответа',
                resetStats: 'Сбросить статистику',
                confirmReset: 'Вы уверены, что хотите сбросить всю статистику? Это действие нельзя отменить.',

                // Score indicators
                scoreStruggling: 'Сложный',
                scoreNeedsWork: 'Нужна практика',
                scoreLearning: 'Изучается',
                scoreMastered: 'Освоен',
                scoreNotAttempted: 'Без ответа'
            }}
        }};

        let currentLanguage = localStorage.getItem('language') || 'ru';

        function t(key) {{
            return translations[currentLanguage][key] || key;
        }}

        // ==========================================
        // QUESTION SCORING SYSTEM
        // ==========================================

        // Get question scores from localStorage
        function getQuestionScores() {{
            try {{
                const stored = localStorage.getItem('questionScores');
                return stored ? JSON.parse(stored) : {{}};
            }} catch (e) {{
                console.error('Error parsing questionScores:', e);
                localStorage.removeItem('questionScores');
                return {{}};
            }}
        }}

        // Save question scores to localStorage
        function saveQuestionScores(scores) {{
            localStorage.setItem('questionScores', JSON.stringify(scores));
        }}

        // Update score for a specific question
        function updateQuestionScore(qNum, isCorrect) {{
            const scores = getQuestionScores();
            const qKey = String(qNum);

            if (!scores[qKey]) {{
                scores[qKey] = {{ score: 0, consecutiveWrong: 0 }};
            }}

            if (isCorrect) {{
                scores[qKey].score += 1;
                scores[qKey].consecutiveWrong = 0;
            }} else {{
                // Escalating penalty based on consecutive wrong answers
                const consecutive = scores[qKey].consecutiveWrong + 1;
                let penalty;
                if (consecutive === 1) penalty = -2;
                else if (consecutive === 2) penalty = -3;
                else penalty = -4;

                scores[qKey].score += penalty;
                scores[qKey].consecutiveWrong = consecutive;
            }}

            saveQuestionScores(scores);
            updateScoreIndicator(qNum);
            updateStatsPanel();
            updatePracticeBadge();
        }}

        // Get score indicator class based on score
        function getScoreIndicatorClass(score) {{
            if (score === null || score === undefined) return 'not-attempted';
            if (score < -4) return 'struggling';
            if (score >= -4 && score <= -1) return 'needs-work';
            if (score >= 0 && score <= 1) return 'learning';
            return 'mastered';
        }}

        // Get score indicator tooltip text
        function getScoreTooltip(score) {{
            if (score === null || score === undefined) return t('scoreNotAttempted');
            if (score < -4) return t('scoreStruggling') + ': ' + score;
            if (score >= -4 && score <= -1) return t('scoreNeedsWork') + ': ' + score;
            if (score >= 0 && score <= 1) return t('scoreLearning') + ': ' + score;
            return t('scoreMastered') + ': ' + score;
        }}

        // Update score indicator for a specific question
        function updateScoreIndicator(qNum) {{
            const scores = getQuestionScores();
            const scoreData = scores[String(qNum)];
            const score = scoreData ? scoreData.score : null;

            const indicator = document.getElementById('indicator' + qNum);
            if (indicator) {{
                // Remove all score classes
                indicator.classList.remove('struggling', 'needs-work', 'learning', 'mastered', 'not-attempted');
                // Add the appropriate class
                indicator.classList.add(getScoreIndicatorClass(score));
                // Update tooltip
                const tooltip = indicator.querySelector('.score-tooltip');
                if (tooltip) {{
                    tooltip.textContent = getScoreTooltip(score);
                }}
                indicator.title = getScoreTooltip(score);
            }}
        }}

        // Render all score indicators on page load
        function renderAllIndicators() {{
            allQuestionNumbers.forEach(qNum => {{
                updateScoreIndicator(qNum);
            }});
        }}

        // Update stats panel with current counts
        function updateStatsPanel() {{
            const scores = getQuestionScores();
            let needsPractice = 0;
            let mastered = 0;
            let notAttempted = 0;

            allQuestionNumbers.forEach(qNum => {{
                const scoreData = scores[String(qNum)];
                if (!scoreData) {{
                    notAttempted++;
                }} else if (scoreData.score >= 2) {{
                    mastered++;
                }} else {{
                    needsPractice++;
                }}
            }});

            const needsPracticeEl = document.getElementById('statsNeedsPractice');
            const masteredEl = document.getElementById('statsMastered');
            const notAttemptedEl = document.getElementById('statsNotAttempted');

            if (needsPracticeEl) needsPracticeEl.textContent = needsPractice;
            if (masteredEl) masteredEl.textContent = mastered;
            if (notAttemptedEl) notAttemptedEl.textContent = notAttempted;
        }}

        // Update practice button badge
        function updatePracticeBadge() {{
            const scores = getQuestionScores();
            let count = 0;

            allQuestionNumbers.forEach(qNum => {{
                const scoreData = scores[String(qNum)];
                if (scoreData && scoreData.score < 2) {{
                    count++;
                }}
            }});

            const badge = document.getElementById('practiceBadge');
            if (badge) {{
                badge.textContent = count;
                badge.classList.toggle('empty', count === 0);
            }}
        }}

        // Toggle stats panel collapse
        function toggleStatsPanel() {{
            const panel = document.getElementById('statsPanel');
            if (panel) {{
                panel.classList.toggle('collapsed');
            }}
        }}

        // Reset all scores with confirmation
        function resetAllScores() {{
            if (confirm(t('confirmReset'))) {{
                localStorage.removeItem('questionScores');
                renderAllIndicators();
                updateStatsPanel();
                updatePracticeBadge();
            }}
        }}

        // ==========================================
        // FOCUSED PRACTICE MODE
        // ==========================================

        let practiceMode = {{
            active: false,
            questions: [],
            currentIndex: 0,
            recentQuestions: [] // Buffer to avoid showing same question repeatedly
        }};

        const RECENT_BUFFER_SIZE = 5; // Number of recent questions to exclude from selection

        // Get questions that need practice (score < 2)
        function getQuestionsNeedingPractice() {{
            const scores = getQuestionScores();
            const questions = [];

            allQuestionNumbers.forEach(qNum => {{
                const scoreData = scores[String(qNum)];
                if (scoreData && scoreData.score < 2) {{
                    questions.push({{
                        qNum: qNum,
                        score: scoreData.score,
                        weight: Math.max(1, Math.abs(scoreData.score)) // Weight for random selection (min 1)
                    }});
                }}
            }});

            return questions;
        }}

        // Select a weighted random question (lower scores = higher chance)
        function selectWeightedQuestion(questions) {{
            if (questions.length === 0) return null;

            // Filter out recently shown questions to avoid repetition
            let candidates = questions.filter(q => !practiceMode.recentQuestions.includes(q.qNum));

            // If all questions are in recent buffer, use full list
            if (candidates.length === 0) {{
                candidates = questions;
            }}

            // Calculate total weight
            const totalWeight = candidates.reduce((sum, q) => sum + q.weight, 0);

            // Select random based on weight
            let random = Math.random() * totalWeight;
            for (const q of candidates) {{
                random -= q.weight;
                if (random <= 0) {{
                    // Add to recent buffer
                    practiceMode.recentQuestions.push(q.qNum);
                    if (practiceMode.recentQuestions.length > RECENT_BUFFER_SIZE) {{
                        practiceMode.recentQuestions.shift();
                    }}
                    return q.qNum;
                }}
            }}

            // Fallback to first candidate
            const fallback = candidates[0].qNum;
            practiceMode.recentQuestions.push(fallback);
            if (practiceMode.recentQuestions.length > RECENT_BUFFER_SIZE) {{
                practiceMode.recentQuestions.shift();
            }}
            return fallback;
        }}

        // Start focused practice mode
        function startFocusedPractice() {{
            // Prevent starting practice mode while quiz is active
            if (quizMode.active) {{
                console.warn('Cannot start practice mode while quiz is active');
                return;
            }}

            const questions = getQuestionsNeedingPractice();

            if (questions.length === 0) {{
                // Check if there are any attempted questions
                const scores = getQuestionScores();
                const hasAttempted = Object.keys(scores).length > 0;

                showPracticeMessage(
                    hasAttempted ? t('practiceCongrats') : t('practiceNoQuestions'),
                    hasAttempted ? t('practiceCongratsText') : t('practiceNoQuestionsText')
                );
                return;
            }}

            practiceMode.active = true;
            practiceMode.questions = questions;
            practiceMode.currentIndex = 0;
            practiceMode.recentQuestions = []; // Clear recent buffer

            document.body.classList.add('practice-mode');

            // Hide all cards first
            const allCards = document.querySelectorAll('.question-card');
            allCards.forEach(card => {{
                card.style.display = 'none';
                card.classList.remove('practice-visible');
                // Reset answer state for practice
                const options = card.querySelectorAll('.option');
                options.forEach(opt => {{
                    opt.classList.remove('correct', 'incorrect', 'disabled');
                }});
                const result = card.querySelector('.result');
                if (result) {{
                    result.innerHTML = '';
                    result.classList.remove('correct', 'incorrect');
                }}
            }});

            // Show first question (answeredQuestions is reset per-question in showNextPracticeQuestion)
            showNextPracticeQuestion();
            updatePracticeHeader();
        }}

        // Show the next practice question
        function showNextPracticeQuestion() {{
            // Hide current visible card
            const currentVisible = document.querySelector('.question-card.practice-visible');
            if (currentVisible) {{
                currentVisible.classList.remove('practice-visible');
                currentVisible.style.display = 'none';
            }}

            // Get remaining questions that still need practice
            const remainingQuestions = getQuestionsNeedingPractice();

            if (remainingQuestions.length === 0) {{
                // All questions mastered!
                exitFocusedPractice();
                showPracticeMessage(t('practiceCongrats'), t('practiceCongratsText'));
                return;
            }}

            // Select next question with weighted random
            const nextQNum = selectWeightedQuestion(remainingQuestions);

            // Show the selected card
            const card = document.getElementById('q' + nextQNum);
            if (card) {{
                card.style.display = 'block';
                card.classList.add('practice-visible');
                card.scrollIntoView({{ behavior: 'smooth', block: 'center' }});

                // Allow this question to be answered
                answeredQuestions.delete(nextQNum);

                // Reset answer state
                const options = card.querySelectorAll('.option');
                options.forEach(opt => {{
                    opt.classList.remove('correct', 'incorrect', 'disabled');
                }});
                const result = card.querySelector('.result');
                if (result) {{
                    result.innerHTML = '';
                    result.classList.remove('correct', 'incorrect');
                }}
            }}

            updatePracticeHeader();
        }}

        // Skip current practice question
        function skipPracticeQuestion() {{
            showNextPracticeQuestion();
        }}

        // Update practice header with remaining count
        function updatePracticeHeader() {{
            const remaining = getQuestionsNeedingPractice().length;
            const progressText = document.getElementById('practiceProgressText');
            if (progressText) {{
                progressText.textContent = t('practiceRemaining') + ': ' + remaining + ' ' + t('practiceQuestions');
            }}
        }}

        // Exit focused practice mode
        function exitFocusedPractice() {{
            practiceMode.active = false;
            practiceMode.questions = [];
            practiceMode.currentIndex = 0;
            practiceMode.recentQuestions = [];

            document.body.classList.remove('practice-mode');

            // Show all cards again
            const allCards = document.querySelectorAll('.question-card');
            allCards.forEach(card => {{
                card.style.display = 'block';
                card.classList.remove('practice-visible');
            }});

            // Show section headers again
            const headers = document.querySelectorAll('.section-header');
            headers.forEach(h => h.style.display = 'block');
        }}

        // Show a practice message (congrats or no questions)
        function showPracticeMessage(title, text) {{
            // Create overlay for message using DOM methods to prevent XSS
            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay';
            overlay.style.display = 'flex';

            const content = document.createElement('div');
            content.className = 'modal-content';
            content.style.cssText = 'text-align: center; padding: 40px;';

            const h2 = document.createElement('h2');
            h2.style.cssText = 'color: var(--success); margin-bottom: 16px;';
            h2.textContent = title;

            const p = document.createElement('p');
            p.style.cssText = 'margin-bottom: 24px; color: var(--text-secondary);';
            p.textContent = text;

            const btn = document.createElement('button');
            btn.className = 'btn-primary';
            btn.textContent = t('practiceBackToStudy');
            btn.onclick = () => overlay.remove();

            content.appendChild(h2);
            content.appendChild(p);
            content.appendChild(btn);
            overlay.appendChild(content);

            // Close on overlay click (outside modal)
            overlay.onclick = (e) => {{
                if (e.target === overlay) overlay.remove();
            }};

            document.body.appendChild(overlay);
        }}

        // Update practice mode UI translations
        function updatePracticeUI() {{
            const practiceBtn = document.getElementById('practiceBtnText');
            if (practiceBtn) practiceBtn.textContent = t('practiceMode');

            const practiceTitle = document.getElementById('practiceTitle');
            if (practiceTitle) practiceTitle.textContent = t('practiceTitle');

            const practiceSkipBtn = document.getElementById('practiceSkipBtn');
            if (practiceSkipBtn) practiceSkipBtn.textContent = t('practiceSkip');

            const practiceExitBtn = document.getElementById('practiceExitBtn');
            if (practiceExitBtn) practiceExitBtn.textContent = t('practiceExit');

            // Stats panel translations
            const statsPanelTitle = document.getElementById('statsPanelTitle');
            if (statsPanelTitle) statsPanelTitle.textContent = t('statsTitle');

            const statsNeedsPracticeLabel = document.getElementById('statsNeedsPracticeLabel');
            if (statsNeedsPracticeLabel) statsNeedsPracticeLabel.textContent = t('needsPractice');

            const statsMasteredLabel = document.getElementById('statsMasteredLabel');
            if (statsMasteredLabel) statsMasteredLabel.textContent = t('mastered');

            const statsNotAttemptedLabel = document.getElementById('statsNotAttemptedLabel');
            if (statsNotAttemptedLabel) statsNotAttemptedLabel.textContent = t('notAttempted');

            const statsResetBtn = document.getElementById('statsResetBtn');
            if (statsResetBtn) statsResetBtn.textContent = t('resetStats');

            updatePracticeHeader();

            // Update all score indicator tooltips for language change
            allQuestionNumbers.forEach(qNum => {{
                updateScoreIndicator(qNum);
            }});
        }}

        function updateInterfaceLanguage() {{
            // Header
            const subtitle = document.querySelector('.subtitle');
            if (subtitle) subtitle.textContent = t('subtitle');

            const searchBox = document.querySelector('.search-box');
            if (searchBox) searchBox.placeholder = t('searchPlaceholder');

            // Sidebar buttons - update quiz toggle based on mode
            try {{
                updateQuizToggleButton();
            }} catch (error) {{
                console.error('Error updating quiz toggle button:', error);
            }}

            const printBtn = document.querySelector('.print-btn');
            if (printBtn) printBtn.title = t('printAll');

            const themeBtn = document.querySelector('.theme-toggle');
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            if (themeBtn) themeBtn.title = isDark ? t('lightMode') : t('darkMode');

            // Stats
            const statsText = document.querySelector('.stats');
            if (statsText) {{
                const count = document.getElementById('revealed').textContent;
                statsText.innerHTML = `<span id="revealed">${{count}}</span> / ${{totalQuestions}} ${{t('questionsAnswered')}}`;
            }}

            // Quiz modal - use specific IDs
            const quizModalTitle = document.getElementById('quizModalTitle');
            if (quizModalTitle) quizModalTitle.textContent = t('configureExam');

            const questionSelectionLabel = document.getElementById('questionSelectionLabel');
            if (questionSelectionLabel) questionSelectionLabel.textContent = t('questionSelection');

            const fullExamLabel = document.getElementById('fullExamLabel');
            if (fullExamLabel) fullExamLabel.textContent = t('fullExam');

            const bySectionLabel = document.getElementById('bySectionLabel');
            if (bySectionLabel) bySectionLabel.textContent = t('bySection');

            const quickPracticeLabel = document.getElementById('quickPracticeLabel');
            if (quickPracticeLabel) quickPracticeLabel.textContent = t('quickPractice');

            const questionsLabel = document.getElementById('questionsLabel');
            if (questionsLabel) questionsLabel.textContent = t('questions');

            const randomOrderLabel = document.getElementById('randomOrderLabel');
            if (randomOrderLabel) randomOrderLabel.textContent = t('randomOrder');

            const timerLabel = document.getElementById('timerLabel');
            if (timerLabel) timerLabel.textContent = t('timer');

            const noTimerLabel = document.getElementById('noTimerLabel');
            if (noTimerLabel) noTimerLabel.textContent = t('noTimer');

            const fullTimerLabel = document.getElementById('fullTimerLabel');
            if (fullTimerLabel) fullTimerLabel.textContent = t('fullTimer');

            const proportionalTimerLabel = document.getElementById('proportionalTimerLabel');
            if (proportionalTimerLabel) proportionalTimerLabel.textContent = t('proportionalTimer');

            const quizCancelBtn = document.getElementById('quizCancelBtn');
            if (quizCancelBtn) quizCancelBtn.textContent = t('cancel');

            const quizStartBtn = document.getElementById('quizStartBtn');
            if (quizStartBtn) quizStartBtn.textContent = t('startExam');

            // Quiz header - use specific IDs
            const quizPrevBtn = document.getElementById('quizPrevBtn');
            if (quizPrevBtn) quizPrevBtn.textContent = '← ' + t('previous');

            const quizNextBtn = document.getElementById('quizNextBtn');
            if (quizNextBtn) quizNextBtn.textContent = t('next') + ' →';

            const quizFinishBtn = document.getElementById('quizFinishBtn');
            if (quizFinishBtn) quizFinishBtn.textContent = t('finishExam');

            const quizExitBtn = document.getElementById('quizExitBtn');
            if (quizExitBtn) quizExitBtn.textContent = t('exit');

            // Index
            const indexTitle = document.querySelector('.index-title');
            if (indexTitle) indexTitle.textContent = t('index');

            // Bottom nav
            const navBtns = document.querySelectorAll('.nav-btn span');
            if (navBtns.length >= 4) {{
                navBtns[0].textContent = t('home');
                navBtns[1].textContent = t('previous');
                navBtns[2].textContent = t('nextUnanswered');
                navBtns[3].textContent = t('next');
            }}

            // Practice mode UI
            updatePracticeUI();
        }}

        // Theme management with system preference detection
        const themeToggleBtn = document.querySelector('.theme-toggle');

        (function() {{
            const storedTheme = localStorage.getItem('theme');
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

            if (storedTheme === 'dark' || (!storedTheme && systemPrefersDark)) {{
                document.documentElement.setAttribute('data-theme', 'dark');
                themeToggleBtn.textContent = '☀️';
                themeToggleBtn.title = t('lightMode');
            }} else {{
                themeToggleBtn.textContent = '🌙';
                themeToggleBtn.title = t('darkMode');
            }}

            // Set language button to current language
            const flags = {{'ru': '🇷🇺', 'es': '🇪🇸', 'en': '🇬🇧'}};
            const titles = {{'ru': 'Язык', 'es': 'Idioma', 'en': 'Language'}};
            const langBtn = document.querySelector('.language-btn');
            if (langBtn) {{
                langBtn.textContent = flags[currentLanguage];
                langBtn.title = titles[currentLanguage];
            }}

            // Update interface with current language
            try {{
                updateInterfaceLanguage();
            }} catch (error) {{
                console.error('Error in updateInterfaceLanguage:', error);
            }}
        }})();

        function changeLanguage(lang) {{
            currentLanguage = lang;
            localStorage.setItem('language', lang);
            updateInterfaceLanguage();
        }}

        function cycleLanguage() {{
            const languages = ['ru', 'es', 'en'];
            const flags = {{'ru': '🇷🇺', 'es': '🇪🇸', 'en': '🇬🇧'}};
            const titles = {{'ru': 'Язык', 'es': 'Idioma', 'en': 'Language'}};

            const currentIndex = languages.indexOf(currentLanguage);
            const nextIndex = (currentIndex + 1) % languages.length;
            const nextLang = languages[nextIndex];

            currentLanguage = nextLang;
            localStorage.setItem('language', nextLang);

            const langBtn = document.querySelector('.language-btn');
            if (langBtn) {{
                langBtn.textContent = flags[nextLang];
                langBtn.title = titles[nextLang];
            }}

            updateInterfaceLanguage();
        }}

        function toggleTheme() {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            if (newTheme === 'dark') {{
                themeToggleBtn.textContent = '☀️';
                themeToggleBtn.title = t('lightMode');
            }} else {{
                themeToggleBtn.textContent = '🌙';
                themeToggleBtn.title = t('darkMode');
            }}
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
            // Check if in quiz mode
            if (quizMode.active) {{
                selectQuizAnswer(qNum, selectedLabel);
                return;
            }}

            // Prevent multiple answers in study mode
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
            const isCorrect = selectedLabel === correctLabel;

            if (isCorrect) {{
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

            // Update question score
            updateQuestionScore(qNum, isCorrect);

            // In practice mode, automatically show next question after a delay
            if (practiceMode.active) {{
                setTimeout(() => {{
                    showNextPracticeQuestion();
                }}, 1500);
            }}
        }}

        function toggleTranslate(qNum, ruQ, ruOptionsJson, esOptionsJson, correctLabel) {{
            // Disable in quiz mode until results
            if (quizMode.active && !quizMode.results) return;

            const el = document.getElementById('trans' + qNum);
            if (el.classList.contains('show')) {{
                el.classList.remove('show');
                el.innerHTML = '';
            }} else {{
                let ruOptions = [];
                let esOptions = [];
                try {{
                    // Parse the JSON directly - it's already properly escaped by Python
                    ruOptions = JSON.parse(ruOptionsJson);
                    esOptions = JSON.parse(esOptionsJson);
                }} catch (e) {{
                    console.error('Error parsing options:', e);
                    console.error('RU JSON string:', ruOptionsJson);
                    console.error('ES JSON string:', esOptionsJson);
                    ruOptions = [];
                    esOptions = [];
                }}

                // Create a map of Spanish options by label
                const esMap = {{}};
                esOptions.forEach(opt => {{
                    esMap[opt.label] = opt.text;
                }});

                let html = '<strong>Вопрос:</strong> ' + ruQ + '<br><br>';

                if (ruOptions.length > 0) {{
                    html += '<strong>Варианты:</strong><br>';
                    ruOptions.forEach(opt => {{
                        const isCorrect = opt.label === correctLabel;
                        const checkmark = isCorrect ? ' ✓' : '';
                        const spanishText = isCorrect && esMap[opt.label] ? ' <span style="color: var(--text-secondary); font-weight: 400; font-size: 0.95em;">(' + esMap[opt.label] + ')</span>' : '';
                        const style = isCorrect ? ' style="color: var(--success); font-weight: 600;"' : '';
                        html += opt.label + ') ' + '<span' + style + '>' + opt.text + checkmark + '</span>' + spanishText + '<br>';
                    }});
                }} else {{
                    html += '<em style="color: var(--text-tertiary);">Перевод вариантов пока недоступен</em>';
                }}

                el.innerHTML = html;
                el.classList.add('show');
            }}
        }}

        function toggleExplain(qNum, explanation) {{
            // Disable in quiz mode until results
            if (quizMode.active && !quizMode.results) return;

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
            console.log('buildIndex() called');
            const sections = document.querySelectorAll('.section-header');
            const indexContent = document.getElementById('indexContent');
            console.log('Found sections:', sections.length);
            console.log('indexContent element:', indexContent);

            if (!indexContent) {{
                console.error('indexContent element not found!');
                return;
            }}

            sections.forEach((section, idx) => {{
                const sectionTitle = section.querySelector('h2').textContent;
                const sectionDiv = document.createElement('div');
                sectionDiv.className = 'index-section';

                const titleDiv = document.createElement('div');
                titleDiv.className = 'index-section-title collapsed';
                titleDiv.textContent = sectionTitle;

                const contentDiv = document.createElement('div');
                contentDiv.className = 'index-section-content collapsed';

                // Toggle collapse on click
                titleDiv.onclick = () => {{
                    titleDiv.classList.toggle('collapsed');
                    contentDiv.classList.toggle('collapsed');
                }};

                sectionDiv.appendChild(titleDiv);

                // Find all question cards in this section
                let nextEl = section.nextElementSibling;
                while (nextEl && !nextEl.classList.contains('section-header')) {{
                    if (nextEl.classList.contains('question-card')) {{
                        const qNum = nextEl.querySelector('.q-number').textContent;
                        const question = nextEl.querySelector('.question').textContent;
                        const answer = nextEl.querySelector('.answer');
                        const cardId = nextEl.id; // Capture the card ID

                        const link = document.createElement('a');
                        link.href = '#';
                        link.className = 'index-link';
                        if (answer && answer.classList.contains('revealed')) {{
                            link.classList.add('answered');
                        }}
                        link.textContent = qNum + ' ' + (question.length > 40 ? question.substring(0, 40) + '...' : question);
                        link.onclick = (e) => {{
                            e.preventDefault();
                            const targetCard = document.getElementById(cardId);
                            if (targetCard) {{
                                targetCard.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                            }}
                            // Close menu only on mobile
                            if (window.innerWidth <= 768) {{
                                toggleMenu();
                            }}
                        }};
                        contentDiv.appendChild(link);
                    }}
                    nextEl = nextEl.nextElementSibling;
                }}

                sectionDiv.appendChild(contentDiv);
                indexContent.appendChild(sectionDiv);
            }});
        }}

        // Quiz Mode Implementation
        let quizMode = {{
            active: false,
            currentQuestionIndex: 0,
            config: {{
                questionCount: 25,
                sections: [],
                randomOrder: false,
                timerEnabled: false,
                timerMinutes: 45
            }},
            session: {{
                questions: [],
                answers: {{}},
                flagged: new Set(),
                startTime: null,
                endTime: null,
                timerInterval: null
            }},
            results: null
        }};

        // Enable/disable inputs based on radio selection
        document.querySelectorAll('input[name="questionMode"]').forEach(radio => {{
            radio.addEventListener('change', (e) => {{
                const mode = e.target.value;
                document.getElementById('sectionSelect').disabled = (mode !== 'section');
                document.getElementById('customCount').disabled = (mode !== 'custom');
            }});
        }});

        function openQuizConfig() {{
            document.getElementById('quizModal').style.display = 'flex';
        }}

        function closeQuizConfig() {{
            document.getElementById('quizModal').style.display = 'none';
        }}

        function startQuizFromConfig() {{
            const questionMode = document.querySelector('input[name="questionMode"]:checked').value;
            const timerMode = document.querySelector('input[name="timerMode"]:checked').value;
            const randomOrder = document.getElementById('randomOrder').checked;

            const config = {{
                randomOrder: randomOrder,
                timerEnabled: timerMode !== 'none',
                timerMinutes: 45
            }};

            // Determine question selection
            if (questionMode === 'all') {{
                config.questionCount = {len(questions)};
                config.sections = [];
            }} else if (questionMode === 'section') {{
                const section = parseInt(document.getElementById('sectionSelect').value);
                config.sections = [section];
                const ranges = {{1:[1001,1120], 2:[2001,2036], 3:[3001,3024], 4:[4001,4036], 5:[5001,5084]}};
                config.questionCount = ranges[section][1] - ranges[section][0] + 1;
            }} else {{
                config.questionCount = parseInt(document.getElementById('customCount').value) || 25;
                config.sections = [];
            }}

            // Adjust timer for proportional mode
            if (timerMode === 'proportional') {{
                config.timerMinutes = Math.ceil(config.questionCount * 45 / 300);
            }} else if (timerMode === 'full') {{
                config.timerMinutes = 45;
            }}

            closeQuizConfig();
            startQuiz(config);
        }}

        function getQuizQuestions(config) {{
            let pool = [];

            if (config.sections.length === 0) {{
                // All questions
                pool = [...allQuestionNumbers];
            }} else {{
                // Specific sections
                const ranges = {{1:[1001,1120], 2:[2001,2036], 3:[3001,3024], 4:[4001,4036], 5:[5001,5084]}};
                config.sections.forEach(s => {{
                    const [start, end] = ranges[s];
                    for (let i = start; i <= end; i++) {{
                        pool.push(i);
                    }}
                }});
            }}

            if (config.randomOrder) {{
                pool = pool.sort(() => Math.random() - 0.5);
            }}

            return pool.slice(0, config.questionCount);
        }}

        function startQuiz(config) {{
            // Exit practice mode if active
            if (practiceMode.active) {{
                exitFocusedPractice();
            }}

            quizMode.config = config;
            quizMode.active = true;
            quizMode.currentQuestionIndex = 0;
            quizMode.session.questions = getQuizQuestions(config);
            quizMode.session.answers = {{}};
            quizMode.session.flagged = new Set();
            quizMode.session.startTime = Date.now();
            quizMode.results = null;

            // Add quiz mode class to body
            document.body.classList.add('quiz-mode');

            // Reset all study mode selections
            allCards.forEach(card => {{
                // Remove all selection states from options
                const options = card.querySelectorAll('.option');
                options.forEach(option => {{
                    option.classList.remove('selected', 'correct', 'incorrect', 'selected-quiz', 'disabled');
                    option.style.borderColor = '';
                    option.style.background = '';
                }});

                // Clear result text (✓ Correcto / ✗ Incorrecto)
                const resultDiv = card.querySelector('.result');
                if (resultDiv) {{
                    resultDiv.innerHTML = '';
                    resultDiv.classList.remove('correct', 'incorrect');
                }}

                // Hide answer section
                const answer = card.querySelector('.answer');
                if (answer) {{
                    answer.classList.remove('revealed');
                    answer.style.display = 'none';
                }}

                // Remove any quiz next buttons from previous sessions
                const quizNextBtn = card.querySelector('.quiz-next-card-btn');
                if (quizNextBtn) quizNextBtn.remove();

                // Hide card initially
                card.style.display = 'none';
            }});

            // Show only the current question
            showQuizQuestion(0);

            // Update progress and navigation buttons
            updateQuizProgress();
            updateQuizNavButtons();

            // Start timer if enabled
            if (config.timerEnabled) {{
                startTimer(config.timerMinutes);
            }} else {{
                document.getElementById('quizTimer').textContent = '';
            }}

            // Save session to localStorage
            saveQuizSession();

            // Update toggle button
            updateQuizToggleButton();
        }}

        function showQuizQuestion(index) {{
            // Hide all cards
            allCards.forEach(card => {{
                card.style.display = 'none';
            }});

            // Show only the current quiz question
            if (index >= 0 && index < quizMode.session.questions.length) {{
                const qNum = quizMode.session.questions[index];
                const card = document.getElementById('q' + qNum);
                if (card) {{
                    card.style.display = 'block';
                    card.scrollIntoView({{ behavior: 'smooth', block: 'center' }});

                    // Show next/end button if question is already answered
                    if (quizMode.session.answers[qNum]) {{
                        let quizNextCardBtn = card.querySelector('.quiz-next-card-btn');
                        if (!quizNextCardBtn) {{
                            quizNextCardBtn = document.createElement('button');
                            quizNextCardBtn.className = 'quiz-next-card-btn btn-primary';

                            // If last question, show "End Exam" button
                            if (index >= quizMode.session.questions.length - 1) {{
                                quizNextCardBtn.textContent = t('finishExam');
                                quizNextCardBtn.onclick = () => submitQuiz();
                            }} else {{
                                quizNextCardBtn.textContent = t('next');
                                quizNextCardBtn.onclick = () => navigateQuizQuestion(1);
                            }}

                            card.appendChild(quizNextCardBtn);
                        }}
                    }}
                }}
            }}
        }}

        function navigateQuizQuestion(direction) {{
            const newIndex = quizMode.currentQuestionIndex + direction;
            if (newIndex >= 0 && newIndex < quizMode.session.questions.length) {{
                quizMode.currentQuestionIndex = newIndex;
                showQuizQuestion(newIndex);
                updateQuizProgress();
                updateQuizNavButtons();
                saveQuizSession();
            }}
        }}

        function updateQuizNavButtons() {{
            const prevBtn = document.getElementById('quizPrevBtn');
            const nextBtn = document.getElementById('quizNextBtn');

            if (prevBtn) {{
                prevBtn.disabled = quizMode.currentQuestionIndex === 0;
            }}

            if (nextBtn) {{
                nextBtn.disabled = quizMode.currentQuestionIndex >= quizMode.session.questions.length - 1;
            }}
        }}

        function selectQuizAnswer(qNum, label) {{
            quizMode.session.answers[qNum] = label;

            // Update visual state
            const card = document.getElementById('q' + qNum);
            const options = card.querySelectorAll('.option');
            options.forEach(opt => {{
                opt.classList.remove('selected-quiz');
                if (opt.dataset.label === label) {{
                    opt.classList.add('selected-quiz');
                }}
            }});

            // Show next button or end exam button
            let quizNextCardBtn = card.querySelector('.quiz-next-card-btn');
            if (!quizNextCardBtn) {{
                quizNextCardBtn = document.createElement('button');
                quizNextCardBtn.className = 'quiz-next-card-btn btn-primary';

                // If last question, show "End Exam" button
                if (quizMode.currentQuestionIndex >= quizMode.session.questions.length - 1) {{
                    quizNextCardBtn.textContent = t('finishExam');
                    quizNextCardBtn.onclick = () => submitQuiz();
                }} else {{
                    quizNextCardBtn.textContent = t('next');
                    quizNextCardBtn.onclick = () => navigateQuizQuestion(1);
                }}

                card.appendChild(quizNextCardBtn);
            }}

            // Update progress
            updateQuizProgress();

            // Save session
            saveQuizSession();
        }}

        function updateQuizProgress() {{
            const answered = Object.keys(quizMode.session.answers).length;
            const total = quizMode.session.questions.length;
            const percentage = total > 0 ? (answered / total * 100) : 0;
            const current = quizMode.currentQuestionIndex + 1;

            document.getElementById('quizProgressText').textContent = `${{t('question')}} ${{current}}/${{total}} (${{answered}} ${{t('answered')}})`;
            document.getElementById('progressFill').style.width = percentage + '%';
        }}

        function startTimer(minutes) {{
            const endTime = Date.now() + minutes * 60 * 1000;

            function updateTimer() {{
                const remaining = Math.max(0, endTime - Date.now());
                const mins = Math.floor(remaining / 60000);
                const secs = Math.floor((remaining % 60000) / 1000);

                const display = `${{String(mins).padStart(2, '0')}}:${{String(secs).padStart(2, '0')}}`;
                const timerEl = document.getElementById('quizTimer');
                timerEl.textContent = display;

                // Warning at 5 minutes
                if (mins < 5) {{
                    timerEl.classList.add('warning');
                }} else {{
                    timerEl.classList.remove('warning');
                }}

                // Auto-submit at 0
                if (remaining === 0) {{
                    stopTimer();
                    alert(t('timeExpired'));
                    calculateResults();
                }}
            }}

            updateTimer();
            quizMode.session.timerInterval = setInterval(updateTimer, 1000);
        }}

        function stopTimer() {{
            if (quizMode.session.timerInterval) {{
                clearInterval(quizMode.session.timerInterval);
                quizMode.session.timerInterval = null;
            }}
        }}

        function submitQuiz() {{
            console.log('submitQuiz called');
            const answered = Object.keys(quizMode.session.answers).length;
            const total = quizMode.session.questions.length;
            const unanswered = total - answered;

            let message = t('confirmFinish');
            if (unanswered > 0) {{
                message += `\\n\\n${{t('unansweredQuestions')}} ${{unanswered}} ${{t('questionsUnanswered')}}`;
            }}

            if (confirm(message)) {{
                console.log('User confirmed, calculating results...');
                stopTimer();
                calculateResults();
            }}
        }}

        function calculateResults() {{
            console.log('calculateResults called');
            quizMode.session.endTime = Date.now();

            const results = {{
                correct: 0,
                total: quizMode.session.questions.length,
                bySection: {{}},
                details: []
            }};

            quizMode.session.questions.forEach(qNum => {{
                const userAnswer = quizMode.session.answers[qNum];
                const card = document.getElementById('q' + qNum);
                const correctLabel = card.dataset.correct;
                console.log(`Question ${{qNum}}: user=${{userAnswer}}, correct=${{correctLabel}}`);

                const isCorrect = userAnswer === correctLabel;

                if (isCorrect) results.correct++;

                const section = Math.floor(qNum / 1000);
                if (!results.bySection[section]) {{
                    results.bySection[section] = {{correct: 0, total: 0}};
                }}
                results.bySection[section].total++;
                if (isCorrect) results.bySection[section].correct++;

                results.details.push({{qNum, userAnswer, correctLabel, isCorrect}});

                // Update question score for spaced repetition
                if (userAnswer !== undefined) {{
                    updateQuestionScore(qNum, isCorrect);
                }}
            }});

            results.percentage = (results.correct / results.total * 100).toFixed(1);
            results.passed = results.percentage >= 60;

            // Calculate time taken
            const timeMs = quizMode.session.endTime - quizMode.session.startTime;
            const mins = Math.floor(timeMs / 60000);
            const secs = Math.floor((timeMs % 60000) / 1000);
            results.timeTaken = `${{mins}}m ${{secs}}s`;

            quizMode.results = results;

            // Clear quiz session from localStorage
            localStorage.removeItem('quizSession');

            // Show results
            showQuizResults();
        }}

        function showQuizResults() {{
            console.log('showQuizResults called', quizMode.results);
            document.body.classList.remove('quiz-mode');
            document.body.classList.add('quiz-results');

            const results = quizMode.results;
            console.log('Body classes:', document.body.className);
            const sectionTitles = {{
                1: 'TAREA 1: Gobierno y legislación',
                2: 'TAREA 2: Derechos y deberes',
                3: 'TAREA 3: Geografía',
                4: 'TAREA 4: Cultura e historia',
                5: 'TAREA 5: Sociedad'
            }};

            // Build section performance HTML
            let sectionHTML = '';
            Object.keys(results.bySection).sort().forEach(section => {{
                const data = results.bySection[section];
                const pct = (data.correct / data.total * 100).toFixed(0);
                sectionHTML += `
                    <div class="performance-bar">
                        <div class="performance-label">${{sectionTitles[section] || 'Sección ' + section}}</div>
                        <div class="performance-track">
                            <div class="performance-fill" style="width: ${{pct}}%"></div>
                        </div>
                        <div class="performance-percentage">${{pct}}%</div>
                    </div>
                `;
            }});

            // Calculate circle progress
            const radius = 75;
            const circumference = 2 * Math.PI * radius;
            const progressOffset = circumference - (results.percentage / 100 * circumference);

            const passMessage = {{
                'es': 'Has aprobado el examen con éxito.',
                'en': 'You have successfully passed the examination.',
                'ru': 'Вы успешно сдали экзамен.'
            }};

            const failMessage = {{
                'es': 'No has alcanzado la puntuación mínima. ¡Sigue practicando!',
                'en': 'You have not reached the minimum score. Keep practicing!',
                'ru': 'Вы не набрали минимальный балл. Продолжайте практиковаться!'
            }};

            const html = `
                <div class="results-container">
                    <div class="results-card ${{results.passed ? 'passed' : 'failed'}}">
                        <div class="results-hero">
                            <div class="results-content">
                                <div class="results-kicker">CCSE 2026 — ${{t('examTimeExpired').split('.')[0] || 'RESULTADO DEL EXAMEN'}}</div>
                                <h1 class="results-status ${{results.passed ? 'passed' : 'failed'}}">
                                    ${{results.passed ? t('passed') : t('failed')}}
                                </h1>
                                <p class="results-subtitle">
                                    ${{results.passed ? passMessage[currentLanguage] : failMessage[currentLanguage]}}
                                </p>
                                <div class="results-meta">
                                    <div class="results-meta-item">
                                        <div class="results-meta-label">${{t('correctAnswers')}}</div>
                                        <div class="results-meta-value">${{results.correct}} / ${{results.total}}</div>
                                    </div>
                                    <div class="results-meta-item">
                                        <div class="results-meta-label">${{t('time')}}</div>
                                        <div class="results-meta-value">${{results.timeTaken}}</div>
                                    </div>
                                </div>
                            </div>
                            <div class="results-score-section">
                                <div class="results-score-circle">
                                    <svg width="160" height="160" viewBox="0 0 160 160">
                                        <defs>
                                            <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                                <stop offset="0%" style="stop-color:${{results.passed ? '#065f46' : '#b45309'}};stop-opacity:1" />
                                                <stop offset="100%" style="stop-color:${{results.passed ? '#10b981' : '#f59e0b'}};stop-opacity:1" />
                                            </linearGradient>
                                        </defs>
                                        <circle class="results-circle-bg" cx="80" cy="80" r="${{radius}}" />
                                        <circle
                                            class="results-circle-progress"
                                            cx="80"
                                            cy="80"
                                            r="${{radius}}"
                                            stroke-dasharray="${{circumference}}"
                                            stroke-dashoffset="${{progressOffset}}"
                                        />
                                    </svg>
                                    <div class="results-score">
                                        <div class="results-score-number ${{results.passed ? 'passed' : 'failed'}}">${{results.percentage}}%</div>
                                        <div class="results-score-label">${{t('questionsAnswered').toUpperCase()}}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="section-performance">
                            <h3>${{t('sectionPerformance')}}</h3>
                            <div class="performance-grid">
                                ${{sectionHTML}}
                            </div>
                        </div>
                        <div class="results-actions">
                            <button class="btn-primary" onclick="retryQuiz()">${{t('newExam')}}</button>
                            <button class="btn-secondary" onclick="reviewQuizQuestions()">${{t('reviewQuestions')}}</button>
                            <button class="btn-secondary" onclick="exitToStudyMode()">${{t('studyMode')}}</button>
                        </div>
                    </div>
                    <div id="questionReviewContainer"></div>
                </div>
            `;

            const resultsPageEl = document.getElementById('resultsPage');
            console.log('resultsPage element:', resultsPageEl);
            resultsPageEl.innerHTML = html;
            console.log('Results HTML inserted, resultsPage display:', window.getComputedStyle(resultsPageEl).display);
        }}

        function reviewQuizQuestions() {{
            const container = document.getElementById('questionReviewContainer');

            // If already showing review, scroll to it
            if (container.innerHTML) {{
                container.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                return;
            }}

            let html = `<h3 style="margin: 32px 0 24px; font-size: 1.5rem; font-family: 'Crimson Pro', Georgia, serif; font-weight: 700;">${{t('detailedReview')}}</h3>`;

            quizMode.results.details.forEach(detail => {{
                const qNum = detail.qNum;
                const card = document.getElementById('q' + qNum);
                const question = card.querySelector('.question').textContent;
                const options = Array.from(card.querySelectorAll('.option'));

                const userOption = options.find(opt => opt.dataset.label === detail.userAnswer);
                const correctOption = options.find(opt => opt.dataset.label === detail.correctLabel);

                html += `
                    <div class="question-review">
                        <div class="review-header">
                            <div class="q-number">#${{qNum}}</div>
                            <div class="review-status ${{detail.isCorrect ? 'correct-review' : 'incorrect-review'}}">
                                ${{detail.isCorrect ? '✓ ' + t('correct') : '✗ ' + t('incorrect')}}
                            </div>
                        </div>
                        <div class="review-question">${{question}}</div>
                        <div class="review-answers">
                            ${{detail.userAnswer ? `
                                <div class="review-answer ${{detail.isCorrect ? 'user-correct' : 'user-incorrect'}}">
                                    ${{t('yourAnswer')}} ${{userOption ? userOption.textContent : t('notAnswered')}}
                                </div>
                            ` : `<div class="review-answer user-incorrect">${{t('notAnswered')}}</div>`}}
                            ${{!detail.isCorrect ? `
                                <div class="review-answer correct-answer">
                                    ${{t('correctAnswer')}} ${{correctOption ? correctOption.textContent : 'N/A'}}
                                </div>
                            ` : ''}}
                        </div>
                    </div>
                `;
            }});

            container.innerHTML = html;

            // Scroll to review section
            setTimeout(() => {{
                container.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}, 100);
        }}

        function retryQuiz() {{
            // Exit results mode first
            document.body.classList.remove('quiz-results');
            quizMode.active = false;
            quizMode.results = null;

            // Reset quiz session
            quizMode.session = {{
                questions: [],
                answers: {{}},
                flagged: new Set(),
                startTime: null,
                endTime: null,
                timerInterval: null
            }};

            // Show all cards and clean up quiz state
            allCards.forEach(card => {{
                card.style.display = 'block';
                // Remove quiz next button if it exists
                const quizNextBtn = card.querySelector('.quiz-next-card-btn');
                if (quizNextBtn) quizNextBtn.remove();
                // Remove quiz selection state
                card.querySelectorAll('.option').forEach(opt => {{
                    opt.classList.remove('selected-quiz');
                }});
            }});

            // Open quiz config
            openQuizConfig();
        }}

        function exitToStudyMode() {{
            document.body.classList.remove('quiz-results');
            quizMode.active = false;
            quizMode.results = null;

            // Reset quiz session
            quizMode.session = {{
                questions: [],
                answers: {{}},
                flagged: new Set(),
                startTime: null,
                endTime: null,
                timerInterval: null
            }};

            // Show all cards and clean up quiz state
            allCards.forEach(card => {{
                card.style.display = 'block';
                // Remove quiz next button if it exists
                const quizNextBtn = card.querySelector('.quiz-next-card-btn');
                if (quizNextBtn) quizNextBtn.remove();
                // Remove quiz selection state
                card.querySelectorAll('.option').forEach(opt => {{
                    opt.classList.remove('selected-quiz');
                }});
            }});

            // Scroll to top
            window.scrollTo({{ top: 0, behavior: 'smooth' }});

            // Update toggle button
            updateQuizToggleButton();
        }}

        function exitQuiz() {{
            if (confirm(t('confirmExit'))) {{
                stopTimer();
                document.body.classList.remove('quiz-mode');
                quizMode.active = false;

                // Clear session
                localStorage.removeItem('quizSession');

                // Remove quiz option states
                allCards.forEach(card => {{
                    const options = card.querySelectorAll('.option');
                    options.forEach(opt => opt.classList.remove('selected-quiz'));
                    card.style.display = 'block';
                }});

                // Scroll to top
                window.scrollTo({{ top: 0, behavior: 'smooth' }});

                // Update toggle button
                updateQuizToggleButton();
            }}
        }}

        // Custom confirmation dialog
        function showConfirmDialog(message, confirmText, cancelText, onConfirm, onCancel) {{
            // Create modal overlay
            const overlay = document.createElement('div');
            overlay.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); z-index: 10000; display: flex; align-items: center; justify-content: center; padding: 20px;';

            // Create dialog box
            const dialog = document.createElement('div');
            dialog.style.cssText = 'background: var(--bg-card); border-radius: 16px; padding: 32px; max-width: 500px; width: 100%; box-shadow: 0 20px 60px rgba(0,0,0,0.3); border: 1px solid var(--border);';

            // Message
            const msg = document.createElement('p');
            msg.textContent = message;
            msg.style.cssText = 'color: var(--text); font-size: 1.125rem; margin-bottom: 24px; line-height: 1.6;';
            dialog.appendChild(msg);

            // Button container
            const buttons = document.createElement('div');
            buttons.style.cssText = 'display: flex; gap: 12px; justify-content: flex-end; flex-wrap: wrap;';

            // Cancel button
            const cancelBtn = document.createElement('button');
            cancelBtn.textContent = cancelText;
            cancelBtn.style.cssText = 'padding: 14px 28px; border-radius: 10px; border: 1px solid var(--border); background: var(--bg); color: var(--text-secondary); cursor: pointer; font-size: 1rem; font-family: inherit; transition: all 0.2s; min-width: 120px; touch-action: manipulation;';
            cancelBtn.onmouseover = () => cancelBtn.style.background = 'var(--accent-soft)';
            cancelBtn.onmouseout = () => cancelBtn.style.background = 'var(--bg)';
            cancelBtn.onclick = () => {{
                document.body.removeChild(overlay);
                if (onCancel) onCancel();
            }};

            // Confirm button
            const confirmBtn = document.createElement('button');
            confirmBtn.textContent = confirmText;
            confirmBtn.style.cssText = 'padding: 14px 28px; border-radius: 10px; border: none; background: var(--success); color: white; cursor: pointer; font-size: 1rem; font-weight: 600; font-family: inherit; transition: all 0.2s; min-width: 120px; touch-action: manipulation;';
            confirmBtn.onmouseover = () => confirmBtn.style.background = '#047857';
            confirmBtn.onmouseout = () => confirmBtn.style.background = 'var(--success)';
            confirmBtn.onclick = () => {{
                document.body.removeChild(overlay);
                if (onConfirm) onConfirm();
            }};

            buttons.appendChild(cancelBtn);
            buttons.appendChild(confirmBtn);
            dialog.appendChild(buttons);
            overlay.appendChild(dialog);
            document.body.appendChild(overlay);
        }}

        function saveQuizSession() {{
            if (quizMode.active && !quizMode.results) {{
                const session = {{
                    config: quizMode.config,
                    currentQuestionIndex: quizMode.currentQuestionIndex,
                    questions: quizMode.session.questions,
                    answers: quizMode.session.answers,
                    flagged: Array.from(quizMode.session.flagged),
                    startTime: quizMode.session.startTime
                }};
                localStorage.setItem('quizSession', JSON.stringify(session));
            }}
        }}

        function restoreQuizSession() {{
            const saved = localStorage.getItem('quizSession');
            if (saved) {{
                try {{
                    const session = JSON.parse(saved);

                    // Show custom confirmation dialog
                    showConfirmDialog(
                        t('continueExam'),
                        t('continueButton'),
                        t('startNewButton'),
                        // On Continue
                        () => {{
                            quizMode.config = session.config;
                            quizMode.active = true;
                            quizMode.currentQuestionIndex = session.currentQuestionIndex || 0;
                            quizMode.session.questions = session.questions;
                            quizMode.session.answers = session.answers;
                            quizMode.session.flagged = new Set(session.flagged);
                            quizMode.session.startTime = session.startTime;

                            document.body.classList.add('quiz-mode');

                            // Reset all study mode selections
                            allCards.forEach(card => {{
                                // Remove all selection states from options
                                const options = card.querySelectorAll('.option');
                                options.forEach(option => {{
                                    option.classList.remove('selected', 'correct', 'incorrect', 'selected-quiz', 'disabled');
                                    option.style.borderColor = '';
                                    option.style.background = '';
                                }});

                                // Clear result text (✓ Correcto / ✗ Incorrecto)
                                const resultDiv = card.querySelector('.result');
                                if (resultDiv) {{
                                    resultDiv.innerHTML = '';
                                    resultDiv.classList.remove('correct', 'incorrect');
                                }}

                                // Hide answer section
                                const answer = card.querySelector('.answer');
                                if (answer) {{
                                    answer.classList.remove('revealed');
                                    answer.style.display = 'none';
                                }}

                                // Remove any quiz next buttons
                                const quizNextBtn = card.querySelector('.quiz-next-card-btn');
                                if (quizNextBtn) quizNextBtn.remove();

                                // Hide card initially
                                card.style.display = 'none';
                            }});

                            // Restore answer state for all quiz questions
                            session.questions.forEach(qNum => {{
                                const card = document.getElementById('q' + qNum);
                                if (card && session.answers[qNum]) {{
                                    const options = card.querySelectorAll('.option');
                                    options.forEach(opt => {{
                                        if (opt.dataset.label === session.answers[qNum]) {{
                                            opt.classList.add('selected-quiz');
                                        }}
                                    }});
                                }}
                            }});

                            // Show only the current question
                            showQuizQuestion(quizMode.currentQuestionIndex);

                            updateQuizProgress();
                            updateQuizNavButtons();
                            updateQuizToggleButton();

                            // Resume timer if enabled
                            if (session.config.timerEnabled) {{
                                const elapsed = Date.now() - session.startTime;
                                const remaining = session.config.timerMinutes * 60 * 1000 - elapsed;
                                if (remaining > 0) {{
                                    startTimer(Math.ceil(remaining / 60000));
                                }} else {{
                                    alert(t('examTimeExpired'));
                                    calculateResults();
                                }}
                            }} else {{
                                document.getElementById('quizTimer').textContent = '';
                            }}
                        }},
                        // On Start New
                        () => {{
                            localStorage.removeItem('quizSession');
                        }}
                    );
                }} catch (e) {{
                    console.error('Error restoring quiz session:', e);
                    localStorage.removeItem('quizSession');
                }}
            }}
        }}

        // Warn before leaving during quiz or practice mode
        window.addEventListener('beforeunload', (e) => {{
            if ((quizMode.active && !quizMode.results) || practiceMode.active) {{
                e.preventDefault();
                e.returnValue = t('confirmLeave');
            }}
        }});

        // Try to restore quiz session on page load
        setTimeout(restoreQuizSession, 500);

        // Build index on load
        console.log('About to call buildIndex()');
        try {{
            buildIndex();
            console.log('buildIndex() completed');
        }} catch (error) {{
            console.error('Error in buildIndex():', error);
        }}

        // Initialize scoring system on page load
        try {{
            renderAllIndicators();
            updateStatsPanel();
            updatePracticeBadge();
            console.log('Scoring system initialized');
        }} catch (error) {{
            console.error('Error initializing scoring system:', error);
        }}
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
