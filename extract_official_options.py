#!/usr/bin/env python3
"""Extract official CCSE question options from the PDF via gpt-5-nano."""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from ccse_questions import questions

PDF_PATH = Path.home() / 'Downloads' / 'Preguntas ccse 2026.pdf'
RAW_OUTPUT = Path('official_options_raw.json')
FINAL_OUTPUT = Path('official_options.json')
CHUNK_SIZE = 5
RETRIES = 3
SLEEP_SECONDS = 2

PROMPT_TEMPLATE = """
Utiliza exclusivamente el archivo PDF adjunto "Preguntas ccse 2026.pdf".
Para cada pregunta con los siguientes números: {numbers}, copia literalmente el enunciado y todas las opciones de respuesta
(letras a, b y c; o solo a y b cuando sea Verdadero/Falso) tal como aparecen.
Devuelve ÚNICAMENTE un objeto JSON cuya clave sea el número de pregunta (como texto) y cuyo valor sea:
{{"question": "<enunciado exacto en una sola línea>", "options": [{{"label": "a", "text": "..."}}, ...]}}.
Preserva los signos de puntuación originales y respeta la letra asignada a cada opción.
No añadas comentarios ni bloques de código.
"""


def chunked(seq: List[int], size: int) -> List[List[int]]:
    return [seq[i:i + size] for i in range(0, len(seq), size)]


def clean_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith('```'):
        parts = text.split('```')
        if len(parts) >= 3:
            core = parts[1]
            if core.startswith('json'):
                core = core[4:]
            text = core
    return text.strip()


def extract_options() -> Dict[str, Dict[str, object]]:
    load_dotenv(Path.cwd().parent / 'exocortex' / '.env')

    if not PDF_PATH.exists():
        sys.exit(f'No se encuentra el PDF en {PDF_PATH}')

    print(f'📄 Cargando PDF: {PDF_PATH.name}')
    client = OpenAI()
    uploaded = client.files.create(file=open(PDF_PATH, 'rb'), purpose='assistants')
    file_id = uploaded.id
    print(f'✓ PDF cargado (ID: {file_id[:12]}...)\n')

    aggregated: Dict[str, Dict[str, object]] = {}
    question_ids = sorted(questions.keys())
    chunks = chunked(question_ids, CHUNK_SIZE)
    total_chunks = len(chunks)
    total_questions = len(question_ids)

    print(f'📊 Total: {total_questions} preguntas en {total_chunks} grupos de {CHUNK_SIZE}\n')
    start_time = time.time()

    for chunk_idx, group in enumerate(chunks, 1):
        numbers = ', '.join(str(n) for n in group)
        print(f'[{chunk_idx}/{total_chunks}] Procesando preguntas {numbers}... ', end='', flush=True)
        prompt = PROMPT_TEMPLATE.format(numbers=numbers)

        for attempt in range(1, RETRIES + 1):
            try:
                response = client.responses.create(
                    model='gpt-5-nano',
                    input=[{
                        'role': 'user',
                        'content': [
                            {'type': 'input_text', 'text': prompt},
                            {'type': 'input_file', 'file_id': file_id},
                        ],
                    }],
                    timeout=120,
                )
                text_parts = []
                for item in response.output:
                    content = getattr(item, 'content', None)
                    if not content:
                        continue
                    for block in content:
                        block_text = getattr(block, 'text', None)
                        if block_text:
                            text_parts.append(block_text)
                combined = clean_json_text(''.join(text_parts))
                chunk_data = json.loads(combined)
                aggregated.update(chunk_data)
                print(f'✓ ({len(chunk_data)} preguntas)')

                # Save incrementally after each chunk
                with open(RAW_OUTPUT, 'w', encoding='utf-8') as fh:
                    json.dump(aggregated, fh, ensure_ascii=False, indent=2)

                break
            except Exception as err:  # noqa: BLE001
                if attempt == RETRIES:
                    print(f'✗ ERROR después de {RETRIES} intentos: {err}')
                    raise
                print(f'⚠ Intento {attempt} falló, reintentando... ', end='', flush=True)
                time.sleep(SLEEP_SECONDS * attempt)
        time.sleep(1)

    elapsed = time.time() - start_time
    print(f'\n✓ Completado en {elapsed:.1f}s - {len(aggregated)} preguntas extraídas')
    return aggregated


def normalize(text: str) -> str:
    text = text or ''
    text = text.replace('’', "'").replace('–', '-').replace('\u200b', '')
    text = re.sub(r'\s+', ' ', text.strip())
    text = text.rstrip(' .')
    return text.lower()


def build_final_payload(raw_data: Dict[str, Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    print('\n🔍 Validando y emparejando respuestas...')
    final: Dict[str, Dict[str, object]] = {}
    missing = []
    total = len(raw_data)

    for idx, q_num in enumerate(sorted(raw_data.keys(), key=int), 1):
        if idx % 50 == 0 or idx == total:
            print(f'  Validadas {idx}/{total} preguntas...', end='\r', flush=True)

        info = raw_data[q_num]
        options = info['options']
        answer = questions[int(q_num)][1]
        norm_answer = normalize(answer)
        correct_label = None
        for option in options:
            if normalize(option['text']) == norm_answer:
                correct_label = option['label']
                break
        if not correct_label:
            missing.append(q_num)
        final[q_num] = {
            'question': ' '.join(info['question'].split()),
            'options': options,
            'correct': correct_label,
        }

    print(f'  Validadas {total}/{total} preguntas... ✓')

    if missing:
        print(f'\n⚠ Advertencia: {len(missing)} pregunta(s) sin coincidencia: {missing}')
    else:
        print('✓ Todas las respuestas coinciden correctamente')

    return final


def main() -> None:
    print('═' * 60)
    print('  Extracción de Opciones Oficiales - CCSE 2026')
    print('═' * 60 + '\n')

    raw = extract_options()

    print(f'\n💾 Guardando datos sin procesar en {RAW_OUTPUT}... ', end='', flush=True)
    with open(RAW_OUTPUT, 'w', encoding='utf-8') as fh:
        json.dump(raw, fh, ensure_ascii=False, indent=2)
    print('✓')

    final = build_final_payload(raw)

    print(f'💾 Guardando datos finales en {FINAL_OUTPUT}... ', end='', flush=True)
    with open(FINAL_OUTPUT, 'w', encoding='utf-8') as fh:
        json.dump(final, fh, ensure_ascii=False, indent=2)
    print('✓')

    print('\n' + '═' * 60)
    print(f'  ✅ Proceso completado - {len(final)} preguntas guardadas')
    print('═' * 60)


if __name__ == '__main__':
    main()
