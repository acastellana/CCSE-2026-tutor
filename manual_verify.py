#!/usr/bin/env python3
"""
Manual verification - print specific questions in detail for human review against PDF.
"""

import json
from ccse_questions import questions, translations

# Load official options
with open('official_options.json', 'r', encoding='utf-8') as f:
    official_options = json.load(f)

# Questions to verify manually (sample from each Tarea)
VERIFY_QUESTIONS = [
    # Tarea 1: First, middle, problem question, last
    1001, 1015, 1059, 1060, 1120,
    # Tarea 2: First, middle, last
    2001, 2018, 2036,
    # Tarea 3: First, middle, last
    3001, 3012, 3024,
    # Tarea 4: First, middle, last
    4001, 4018, 4036,
    # Tarea 5: First, middle, last
    5001, 5041, 5084,
]

print('=' * 80)
print('  MANUAL VERIFICATION - Compare these against the PDF')
print('=' * 80)

for q_num in VERIFY_QUESTIONS:
    q_str = str(q_num)

    # Get data from ccse_questions.py
    es_q, es_a = questions[q_num]

    # Get data from official_options.json
    opts_data = official_options.get(q_str, {})
    options = opts_data.get('options', [])
    correct_label = opts_data.get('correct')

    print(f'\n{"=" * 80}')
    print(f'QUESTION {q_num}')
    print(f'{"=" * 80}')
    print(f'Question: {es_q}')
    print(f'Expected answer (ccse_questions.py): {es_a}')
    print(f'Correct label: {correct_label}')
    print('Options:')
    for opt in options:
        marker = ' ✓' if opt['label'] == correct_label else ''
        print(f"  {opt['label']}) {opt['text']}{marker}")

    # Verify the correct option matches the expected answer
    correct_opt = next((opt for opt in options if opt['label'] == correct_label), None)
    if correct_opt:
        # Simple check - answer should be similar to correct option
        answer_in_option = es_a.lower().rstrip('.') in correct_opt['text'].lower()
        if not answer_in_option:
            print(f'\n  ⚠ WARNING: Answer "{es_a}" may not match option {correct_label}: "{correct_opt["text"]}"')

print('\n' + '=' * 80)
print('  Please verify the above against the PDF manually')
print('=' * 80)
