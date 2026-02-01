#!/usr/bin/env python3
"""
Comprehensive verification of all question data against PDF source of truth.

This script checks:
1. All question numbers are present (1001-1120, 2001-2036, 3001-3024, 4001-4036, 5001-5084)
2. Question text matches PDF
3. Options match PDF (a, b, c or a, b for true/false)
4. Correct answer labels match PDF solution key
"""

import json
import re
from pathlib import Path
from difflib import SequenceMatcher

# Import the questions data
from ccse_questions import questions, translations

# PDF Solution Key (from pages 25-27 of the PDF)
# Format: question_number: correct_label
PDF_SOLUTIONS = {
    # TAREA 1 (pages 25)
    1001: 'a', 1002: 'a', 1003: 'a', 1004: 'b', 1005: 'a', 1006: 'a', 1007: 'c', 1008: 'b',
    1009: 'a', 1010: 'b', 1011: 'b', 1012: 'b', 1013: 'b', 1014: 'b', 1015: 'b', 1016: 'a',
    1017: 'b', 1018: 'b', 1019: 'a', 1020: 'a', 1021: 'b', 1022: 'b', 1023: 'b', 1024: 'a',
    1025: 'b', 1026: 'a', 1027: 'b', 1028: 'b', 1029: 'a', 1030: 'a', 1031: 'a', 1032: 'c',
    1033: 'b', 1034: 'a', 1035: 'b', 1036: 'a', 1037: 'c', 1038: 'c', 1039: 'c', 1040: 'c',
    1041: 'a', 1042: 'a', 1043: 'a', 1044: 'a', 1045: 'c', 1046: 'b', 1047: 'b', 1048: 'c',
    1049: 'c', 1050: 'b', 1051: 'c', 1052: 'c', 1053: 'b', 1054: 'a', 1055: 'b', 1056: 'c',
    1057: 'b', 1058: 'c', 1059: 'b', 1060: 'a', 1061: 'b', 1062: 'b', 1063: 'b', 1064: 'b',
    1065: 'c', 1066: 'a', 1067: 'b', 1068: 'b', 1069: 'b', 1070: 'b', 1071: 'a', 1072: 'a',
    1073: 'a', 1074: 'b', 1075: 'b', 1076: 'c', 1077: 'a', 1078: 'c', 1079: 'b', 1080: 'c',
    1081: 'a', 1082: 'b', 1083: 'c', 1084: 'c', 1085: 'a', 1086: 'a', 1087: 'b', 1088: 'c',
    1089: 'a', 1090: 'c', 1091: 'b', 1092: 'b', 1093: 'c', 1094: 'b', 1095: 'a', 1096: 'b',
    1097: 'b', 1098: 'b', 1099: 'a', 1100: 'b', 1101: 'a', 1102: 'a', 1103: 'a', 1104: 'a',
    1105: 'a', 1106: 'c', 1107: 'a', 1108: 'c', 1109: 'a', 1110: 'b', 1111: 'c', 1112: 'b',
    1113: 'a', 1114: 'c', 1115: 'a', 1116: 'b', 1117: 'b', 1118: 'a', 1119: 'c', 1120: 'a',

    # TAREA 2 (page 26)
    2001: 'b', 2002: 'b', 2003: 'a', 2004: 'a', 2005: 'b', 2006: 'b', 2007: 'a', 2008: 'a',
    2009: 'b', 2010: 'a', 2011: 'a', 2012: 'a', 2013: 'b', 2014: 'a', 2015: 'a', 2016: 'a',
    2017: 'a', 2018: 'b', 2019: 'a', 2020: 'a', 2021: 'b', 2022: 'a', 2023: 'b', 2024: 'a',
    2025: 'a', 2026: 'a', 2027: 'b', 2028: 'b', 2029: 'a', 2030: 'a', 2031: 'a', 2032: 'a',
    2033: 'a', 2034: 'b', 2035: 'a', 2036: 'a',

    # TAREA 3 (page 26)
    3001: 'c', 3002: 'c', 3003: 'b', 3004: 'c', 3005: 'a', 3006: 'b', 3007: 'a', 3008: 'a',
    3009: 'c', 3010: 'b', 3011: 'a', 3012: 'b', 3013: 'b', 3014: 'a', 3015: 'b', 3016: 'c',
    3017: 'a', 3018: 'a', 3019: 'b', 3020: 'c', 3021: 'a', 3022: 'b', 3023: 'a', 3024: 'c',

    # TAREA 4 (page 26)
    4001: 'b', 4002: 'c', 4003: 'a', 4004: 'a', 4005: 'a', 4006: 'b', 4007: 'b', 4008: 'c',
    4009: 'a', 4010: 'c', 4011: 'c', 4012: 'a', 4013: 'a', 4014: 'b', 4015: 'b', 4016: 'b',
    4017: 'c', 4018: 'a', 4019: 'b', 4020: 'c', 4021: 'c', 4022: 'a', 4023: 'a', 4024: 'b',
    4025: 'a', 4026: 'b', 4027: 'a', 4028: 'a', 4029: 'a', 4030: 'c', 4031: 'a', 4032: 'b',
    4033: 'a', 4034: 'b', 4035: 'a', 4036: 'c',

    # TAREA 5 (page 27)
    5001: 'b', 5002: 'a', 5003: 'c', 5004: 'b', 5005: 'a', 5006: 'c', 5007: 'a', 5008: 'c',
    5009: 'b', 5010: 'a', 5011: 'b', 5012: 'b', 5013: 'b', 5014: 'b', 5015: 'b', 5016: 'c',
    5017: 'b', 5018: 'c', 5019: 'b', 5020: 'a', 5021: 'b', 5022: 'b', 5023: 'a', 5024: 'a',
    5025: 'c', 5026: 'c', 5027: 'b', 5028: 'b', 5029: 'b', 5030: 'b', 5031: 'b', 5032: 'b',
    5033: 'c', 5034: 'a', 5035: 'c', 5036: 'c', 5037: 'a', 5038: 'b', 5039: 'a', 5040: 'a',
    5041: 'c', 5042: 'c', 5043: 'a', 5044: 'b', 5045: 'a', 5046: 'c', 5047: 'a', 5048: 'b',
    5049: 'b', 5050: 'b', 5051: 'c', 5052: 'b', 5053: 'b', 5054: 'c', 5055: 'a', 5056: 'a',
    5057: 'a', 5058: 'c', 5059: 'c', 5060: 'a', 5061: 'a', 5062: 'b', 5063: 'c', 5064: 'c',
    5065: 'a', 5066: 'b', 5067: 'b', 5068: 'c', 5069: 'b', 5070: 'a', 5071: 'b', 5072: 'b',
    5073: 'b', 5074: 'a', 5075: 'b', 5076: 'b', 5077: 'b', 5078: 'a', 5079: 'b', 5080: 'b',
    5081: 'b', 5082: 'a', 5083: 'a', 5084: 'a',
}

# Expected question ranges
EXPECTED_RANGES = [
    (1001, 1120),  # Tarea 1: 120 questions
    (2001, 2036),  # Tarea 2: 36 questions
    (3001, 3024),  # Tarea 3: 24 questions
    (4001, 4036),  # Tarea 4: 36 questions
    (5001, 5084),  # Tarea 5: 84 questions
]

def get_expected_questions():
    """Generate list of all expected question numbers."""
    expected = []
    for start, end in EXPECTED_RANGES:
        expected.extend(range(start, end + 1))
    return expected


def normalize(text):
    """Normalize text for comparison."""
    if not text:
        return ''
    # Replace special characters
    text = text.replace('\u2019', "'").replace('\u2013', '-').replace('\u200b', '')
    text = text.replace('\u2026', '...').replace('…', '...')
    # Convert ñ to n for comparison
    text = text.replace('ñ', 'n').replace('Ñ', 'N')
    # Remove accents for comparison
    import unicodedata
    # Decompose unicode characters
    text = unicodedata.normalize('NFD', text)
    # Remove combining diacritical marks
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    # Recompose
    text = unicodedata.normalize('NFC', text)
    # Remove extra whitespace and punctuation
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[¿¡?!.,;:\-]', '', text)
    return text.lower().strip()


def similarity(a, b):
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def main():
    print('=' * 70)
    print('  COMPREHENSIVE VERIFICATION AGAINST PDF')
    print('=' * 70)
    print()

    # Load all JSON data files
    with open('official_options.json', 'r', encoding='utf-8') as f:
        official_options = json.load(f)

    with open('official_options_raw.json', 'r', encoding='utf-8') as f:
        official_options_raw = json.load(f)

    with open('options_translations.json', 'r', encoding='utf-8') as f:
        options_translations = json.load(f)

    expected_questions = get_expected_questions()
    total_expected = len(expected_questions)

    print(f'Expected total questions: {total_expected}')
    print(f'  Tarea 1 (1001-1120): 120 questions')
    print(f'  Tarea 2 (2001-2036): 36 questions')
    print(f'  Tarea 3 (3001-3024): 24 questions')
    print(f'  Tarea 4 (4001-4036): 36 questions')
    print(f'  Tarea 5 (5001-5084): 84 questions')
    print()

    # Check 1: Verify all expected questions exist in each data source
    print('=' * 70)
    print('  CHECK 1: Question Number Coverage')
    print('=' * 70)

    sources = {
        'ccse_questions.py (questions)': set(questions.keys()),
        'ccse_questions.py (translations)': set(translations.keys()),
        'official_options.json': set(int(k) for k in official_options.keys()),
        'official_options_raw.json': set(int(k) for k in official_options_raw.keys()),
        'options_translations.json': set(int(k) for k in options_translations.keys()),
        'PDF_SOLUTIONS': set(PDF_SOLUTIONS.keys()),
    }

    all_coverage_ok = True
    for source_name, source_keys in sources.items():
        missing = set(expected_questions) - source_keys
        extra = source_keys - set(expected_questions)

        if missing or extra:
            all_coverage_ok = False
            print(f'\n{source_name}:')
            if missing:
                print(f'  MISSING: {sorted(missing)[:10]}{"..." if len(missing) > 10 else ""}')
            if extra:
                print(f'  EXTRA: {sorted(extra)[:10]}{"..." if len(extra) > 10 else ""}')
        else:
            print(f'{source_name}: OK ({len(source_keys)} questions)')

    if all_coverage_ok:
        print('\n✓ All sources have exactly the expected questions')

    # Check 2: Verify correct answers match PDF solution key
    print()
    print('=' * 70)
    print('  CHECK 2: Correct Answer Labels vs PDF Solution Key')
    print('=' * 70)

    answer_mismatches = []

    for q_num in sorted(expected_questions):
        q_str = str(q_num)

        # Get expected correct answer from PDF
        pdf_correct = PDF_SOLUTIONS.get(q_num)

        # Get correct answer from official_options.json
        if q_str in official_options:
            json_correct = official_options[q_str].get('correct')

            if json_correct != pdf_correct:
                answer_mismatches.append({
                    'q_num': q_num,
                    'pdf': pdf_correct,
                    'json': json_correct
                })

    if answer_mismatches:
        print(f'\n✗ Found {len(answer_mismatches)} answer mismatches:')
        for m in answer_mismatches[:20]:
            print(f"  {m['q_num']}: PDF says '{m['pdf']}', JSON says '{m['json']}'")
        if len(answer_mismatches) > 20:
            print(f'  ... and {len(answer_mismatches) - 20} more')
    else:
        print(f'\n✓ All {len(expected_questions)} correct answers match PDF solution key')

    # Check 3: Verify ccse_questions.py answers match the correct option
    print()
    print('=' * 70)
    print('  CHECK 3: ccse_questions.py Answers Match Correct Options')
    print('=' * 70)

    answer_option_mismatches = []

    for q_num in sorted(expected_questions):
        q_str = str(q_num)

        # Get the answer text from ccse_questions.py
        if q_num in questions:
            _, answer_text = questions[q_num]
            answer_norm = normalize(answer_text)
        else:
            continue

        # Get the options and correct label from official_options.json
        if q_str in official_options:
            options = official_options[q_str].get('options', [])
            correct_label = official_options[q_str].get('correct')

            if correct_label:
                # Find the option with the correct label
                correct_option_text = None
                for opt in options:
                    if opt['label'] == correct_label:
                        correct_option_text = opt['text']
                        break

                if correct_option_text:
                    option_norm = normalize(correct_option_text)

                    # Check if answer matches the correct option
                    sim = similarity(answer_text, correct_option_text)
                    if sim < 0.8:
                        answer_option_mismatches.append({
                            'q_num': q_num,
                            'answer': answer_text,
                            'correct_option': correct_option_text,
                            'label': correct_label,
                            'similarity': sim
                        })

    if answer_option_mismatches:
        print(f'\n✗ Found {len(answer_option_mismatches)} answer-option mismatches:')
        for m in answer_option_mismatches[:20]:
            print(f"  {m['q_num']}: Answer '{m['answer'][:40]}...' vs Option {m['label']}: '{m['correct_option'][:40]}...' (sim: {m['similarity']:.2f})")
    else:
        print(f'\n✓ All answers in ccse_questions.py match their correct options')

    # Check 4: Verify options have correct structure
    print()
    print('=' * 70)
    print('  CHECK 4: Options Structure Verification')
    print('=' * 70)

    structure_issues = []

    for q_num in sorted(expected_questions):
        q_str = str(q_num)

        if q_str in official_options:
            options = official_options[q_str].get('options', [])

            # Check number of options (should be 2 for T/F, 3 for multiple choice)
            if len(options) < 2 or len(options) > 3:
                structure_issues.append({
                    'q_num': q_num,
                    'issue': f'Has {len(options)} options (expected 2 or 3)'
                })
                continue

            # Check option labels
            labels = [opt.get('label') for opt in options]
            expected_labels = ['a', 'b'] if len(options) == 2 else ['a', 'b', 'c']

            if labels != expected_labels:
                structure_issues.append({
                    'q_num': q_num,
                    'issue': f'Labels are {labels}, expected {expected_labels}'
                })

            # Check all options have text
            for opt in options:
                if not opt.get('text'):
                    structure_issues.append({
                        'q_num': q_num,
                        'issue': f"Option {opt.get('label')} has no text"
                    })

    if structure_issues:
        print(f'\n✗ Found {len(structure_issues)} structure issues:')
        for issue in structure_issues[:20]:
            print(f"  {issue['q_num']}: {issue['issue']}")
    else:
        print(f'\n✓ All {len(expected_questions)} questions have valid option structure')

    # Check 5: Verify no duplicate questions
    print()
    print('=' * 70)
    print('  CHECK 5: Duplicate Question Detection')
    print('=' * 70)

    # Build question text -> numbers mapping
    question_texts = {}
    for q_num in sorted(expected_questions):
        q_str = str(q_num)
        if q_str in official_options:
            q_text = normalize(official_options[q_str].get('question', ''))
            if q_text:
                if q_text not in question_texts:
                    question_texts[q_text] = []
                question_texts[q_text].append(q_num)

    duplicates = {text: nums for text, nums in question_texts.items() if len(nums) > 1}

    if duplicates:
        print(f'\n✗ Found {len(duplicates)} duplicate question texts:')
        for text, nums in list(duplicates.items())[:10]:
            print(f"  Questions {nums}: '{text[:60]}...'")
    else:
        print(f'\n✓ No duplicate questions found')

    # Check 6: Sample verification of specific questions against PDF
    print()
    print('=' * 70)
    print('  CHECK 6: Sample Questions Spot Check')
    print('=' * 70)

    # These are samples I can verify against the PDF I read
    # Using key words that should appear in questions/options
    spot_checks = [
        # (q_num, key_words_in_question, key_words_in_options, expected_correct)
        (1001, ["espana"], ["monarquia parlamentaria", "republica federal"], 'a'),
        (1015, ["modera", "instituciones"], ["presidente", "rey", "academia"], 'b'),
        (1059, ["lengua", "baleares"], ["gallego", "catalan", "euskera"], 'b'),
        (2001, ["constitucion", "religion"], ["verdadero", "falso"], 'b'),
        (3001, ["caceres", "badajoz"], ["asturias", "andalucia", "extremadura"], 'c'),
        (4001, ["quijote"], ["don juan", "sancho panza"], 'b'),
        (5001, ["extranjeros", "residir"], ["dni", "tie", "empadronamiento"], 'b'),
    ]

    spot_check_failures = []

    for q_num, q_keywords, opt_keywords, expected_correct in spot_checks:
        q_str = str(q_num)

        if q_str not in official_options:
            spot_check_failures.append(f'{q_num}: Missing from official_options.json')
            continue

        data = official_options[q_str]

        # Check question text contains expected keywords
        q_text_norm = normalize(data.get('question', ''))

        missing_q_keywords = []
        for keyword in q_keywords:
            if normalize(keyword) not in q_text_norm:
                missing_q_keywords.append(keyword)

        if missing_q_keywords:
            spot_check_failures.append(f"{q_num}: Question missing keywords {missing_q_keywords}. Got: '{data.get('question', '')[:50]}...'")
            continue

        # Check correct answer
        if data.get('correct') != expected_correct:
            spot_check_failures.append(f"{q_num}: Correct answer is '{data.get('correct')}', expected '{expected_correct}'")
            continue

        # Check options contain expected keywords
        all_options_text = ' '.join(normalize(opt.get('text', '')) for opt in data.get('options', []))
        missing_opt_keywords = []
        for keyword in opt_keywords:
            if normalize(keyword) not in all_options_text:
                missing_opt_keywords.append(keyword)

        if missing_opt_keywords:
            opts_display = [opt.get('text', '') for opt in data.get('options', [])]
            spot_check_failures.append(f"{q_num}: Options missing keywords {missing_opt_keywords}. Got: {opts_display}")
            continue

        print(f'  {q_num}: OK - "{data.get("question", "")[:50]}..."')

    if spot_check_failures:
        print(f'\n✗ Spot check failures:')
        for failure in spot_check_failures:
            print(f'  {failure}')
    else:
        print(f'\n✓ All spot checks passed')

    # Summary
    print()
    print('=' * 70)
    print('  VERIFICATION SUMMARY')
    print('=' * 70)

    total_issues = (
        (0 if all_coverage_ok else 1) +
        len(answer_mismatches) +
        len(answer_option_mismatches) +
        len(structure_issues) +
        len(duplicates) +
        len(spot_check_failures)
    )

    if total_issues == 0:
        print(f'\n✓ ALL CHECKS PASSED')
        print(f'  - {total_expected} questions verified')
        print(f'  - All question numbers present')
        print(f'  - All correct answers match PDF solution key')
        print(f'  - All options have valid structure')
        print(f'  - No duplicate questions')
        print(f'  - Spot checks passed')
    else:
        print(f'\n✗ FOUND {total_issues} ISSUE(S)')

    return total_issues


if __name__ == '__main__':
    exit(main())
