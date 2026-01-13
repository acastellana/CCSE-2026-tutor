#!/usr/bin/env python3
"""Translate all Spanish options to Russian using OpenAI API"""

import json
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

INPUT_FILE = Path('official_options_raw.json')
OUTPUT_FILE = Path('options_translations.json')


def translate_option(client: OpenAI, text: str) -> str:
    """Translate single Spanish option to Russian"""
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {
                'role': 'system',
                'content': 'You are a translator. Translate Spanish to Russian accurately and concisely.',
            },
            {'role': 'user', 'content': f'Translate to Russian: {text}'},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def main() -> None:
    print('=' * 60)
    print('  Traducción de Opciones - CCSE 2026')
    print('=' * 60 + '\n')

    load_dotenv(Path.cwd().parent / 'exocortex' / '.env')
    client = OpenAI()

    if not INPUT_FILE.exists():
        print(f'❌ Error: {INPUT_FILE} no encontrado')
        print('Ejecuta primero extract_official_options.py')
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        official_data = json.load(f)

    print(f'📄 Cargadas {len(official_data)} preguntas de {INPUT_FILE}')
    print(f'📊 Total de opciones a traducir: {len(official_data) * 3}\n')

    translations = {}
    total = len(official_data)
    start_time = time.time()

    for idx, (q_num, data) in enumerate(
        sorted(official_data.items(), key=lambda x: int(x[0])), 1
    ):
        print(f'[{idx}/{total}] Pregunta {q_num}: Traduciendo opciones... ', end='', flush=True)

        translated_options = []
        for option in data['options']:
            try:
                ru_text = translate_option(client, option['text'])
                translated_options.append({'label': option['label'], 'text': ru_text})
            except Exception as e:
                print(f'\n⚠ Error traduciendo opción {option["label"]}: {e}')
                translated_options.append(
                    {'label': option['label'], 'text': '[ERROR: sin traducir]'}
                )

        translations[q_num] = {'options': translated_options}
        print('✓')

        # Save incrementally every 10 questions
        if idx % 10 == 0:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)

        # Small delay to avoid rate limits
        time.sleep(0.2)

    elapsed = time.time() - start_time

    print(f'\n💾 Guardando traducciones en {OUTPUT_FILE}... ', end='', flush=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    print('✓')

    print('\n' + '=' * 60)
    print(f'  ✅ {len(translations)} preguntas traducidas en {elapsed:.1f}s')
    print('=' * 60)


if __name__ == '__main__':
    main()
