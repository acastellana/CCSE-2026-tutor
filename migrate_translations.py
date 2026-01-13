#!/usr/bin/env python3
"""Merge existing Q&A translations with new option translations"""

import json
from pathlib import Path

from ccse_questions import translations as old_translations

INPUT_FILE = Path('options_translations.json')


def main() -> None:
    print('=' * 60)
    print('  Migración de Traducciones - CCSE 2026')
    print('=' * 60 + '\n')

    if not INPUT_FILE.exists():
        print(f'❌ Error: {INPUT_FILE} no encontrado')
        print('Ejecuta primero translate_options.py')
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        options_trans = json.load(f)

    print(f'📄 Cargadas {len(options_trans)} traducciones de opciones')
    print(f'📄 Traducciones existentes: {len(old_translations)} preguntas\n')

    new_translations = {}

    for q_num_int in old_translations.keys():
        # Get existing Q+A translations
        old_data = old_translations[q_num_int]

        if isinstance(old_data, (list, tuple)):
            ru_question, ru_answer = old_data
        else:
            ru_question = old_data.get('question', '')
            ru_answer = old_data.get('answer', '')

        # Get option translations if available
        options = []
        q_num_str = str(q_num_int)
        if q_num_str in options_trans:
            options = options_trans[q_num_str]['options']

        new_translations[q_num_int] = {
            'question': ru_question,
            'answer': ru_answer,
            'options': options,
        }

    # Save as JSON first
    json_output = Path('translations_complete.json')
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(new_translations, f, ensure_ascii=False, indent=2)

    print(f'✅ Guardado en JSON: {json_output}')

    # Now generate Python code using repr for safe escaping
    output_file = Path('translations_migrated.py')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('translations = {\n')
        for q_num in sorted(new_translations.keys()):
            data = new_translations[q_num]
            # Use repr() for automatic and safe escaping
            f.write(f'    {q_num}: {{\n')
            f.write(f'        "question": {repr(data["question"])},\n')
            f.write(f'        "answer": {repr(data["answer"])},\n')
            f.write(f'        "options": [\n')
            for opt in data['options']:
                f.write(f'            {{"label": {repr(opt["label"])}, "text": {repr(opt["text"])}}},\n')
            f.write(f'        ],\n')
            f.write(f'    }},\n')
        f.write('}\n')

    print(f'✅ Generado código Python: {output_file}')
    print(f'📊 Total: {len(new_translations)} preguntas con opciones traducidas')


if __name__ == '__main__':
    main()
