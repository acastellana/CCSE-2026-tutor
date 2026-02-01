#!/usr/bin/env python3
"""
Fix specific issues in official_options.json and official_options_raw.json based on PDF source of truth.
"""

import json
from pathlib import Path

FILES_TO_FIX = [
    Path('official_options.json'),
    Path('official_options_raw.json'),
    Path('options_translations.json'),
]


def fix_data(data: dict, filename: str) -> list:
    """Apply fixes to the data dict. Returns list of fix descriptions."""
    fixes = []

    # Fix 1: Question 1059 - completely wrong question from GPT extraction
    # PDF says: "¿Qué lengua cooficial se habla en las Islas Baleares?"
    # Options: a. Gallego, b. Catalán, c. Euskera
    # Correct: b
    print(f'  Fixing question 1059 in {filename}...')

    if 'translations' in filename:
        # Russian translations file
        data['1059'] = {
            'options': [
                {'label': 'a', 'text': 'Галисийский.'},
                {'label': 'b', 'text': 'Каталанский.'},
                {'label': 'c', 'text': 'Баскский.'}
            ]
        }
    elif 'raw' in filename:
        # Raw file - no 'correct' key
        data['1059'] = {
            'question': '¿Qué lengua cooficial se habla en las Islas Baleares?',
            'options': [
                {'label': 'a', 'text': 'Gallego.'},
                {'label': 'b', 'text': 'Catalán.'},
                {'label': 'c', 'text': 'Euskera.'}
            ]
        }
    else:
        # Main file - includes 'correct' key
        data['1059'] = {
            'question': '¿Qué lengua cooficial se habla en las Islas Baleares?',
            'options': [
                {'label': 'a', 'text': 'Gallego.'},
                {'label': 'b', 'text': 'Catalán.'},
                {'label': 'c', 'text': 'Euskera.'}
            ],
            'correct': 'b'
        }
    fixes.append('1059: Replaced wrong question (was 1015 content) with correct Balearic language question')

    # Fix 2: Question 5038 - missing correct answer label (only in official_options.json)
    if 'raw' not in filename and 'translations' not in filename:
        print(f'  Fixing question 5038 in {filename}...')
        if data.get('5038', {}).get('correct') is None:
            data['5038']['correct'] = 'b'
            fixes.append('5038: Set correct answer to "b" (se compone de dos cursos académicos)')

    # Fix 3: Question 5041 - question text includes answer (skip translations file)
    # Should be: "Los colegios públicos…"
    if 'translations' not in filename:
        print(f'  Fixing question 5041 in {filename}...')
        if '5041' in data:
            data['5041']['question'] = 'Los colegios públicos…'
            fixes.append('5041: Fixed question text (removed answer from question)')

    return fixes


def main():
    print('=' * 60)
    print('  Fixing official_options JSON files')
    print('=' * 60 + '\n')

    all_fixes = []

    for filepath in FILES_TO_FIX:
        if not filepath.exists():
            print(f'Skipping {filepath} (not found)')
            continue

        print(f'Processing {filepath}...')
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        fixes = fix_data(data, str(filepath))

        print(f'  Saving to {filepath}...')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        all_fixes.extend(fixes)
        print()

    print('=' * 60)
    print('  All fixes applied:')
    print('=' * 60)
    for fix in all_fixes:
        print(f'  ✓ {fix}')

    print(f'\n✓ Done! {len(all_fixes)} fixes applied.')


if __name__ == '__main__':
    main()
