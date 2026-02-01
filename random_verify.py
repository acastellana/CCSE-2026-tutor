#!/usr/bin/env python3
"""
Verify random questions from each section to ensure comprehensive coverage.
"""

import json
import random
from ccse_questions import questions

# Load official options
with open('official_options.json', 'r', encoding='utf-8') as f:
    official_options = json.load(f)

# PDF Solution Key
PDF_SOLUTIONS = {
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
    2001: 'b', 2002: 'b', 2003: 'a', 2004: 'a', 2005: 'b', 2006: 'b', 2007: 'a', 2008: 'a',
    2009: 'b', 2010: 'a', 2011: 'a', 2012: 'a', 2013: 'b', 2014: 'a', 2015: 'a', 2016: 'a',
    2017: 'a', 2018: 'b', 2019: 'a', 2020: 'a', 2021: 'b', 2022: 'a', 2023: 'b', 2024: 'a',
    2025: 'a', 2026: 'a', 2027: 'b', 2028: 'b', 2029: 'a', 2030: 'a', 2031: 'a', 2032: 'a',
    2033: 'a', 2034: 'b', 2035: 'a', 2036: 'a',
    3001: 'c', 3002: 'c', 3003: 'b', 3004: 'c', 3005: 'a', 3006: 'b', 3007: 'a', 3008: 'a',
    3009: 'c', 3010: 'b', 3011: 'a', 3012: 'b', 3013: 'b', 3014: 'a', 3015: 'b', 3016: 'c',
    3017: 'a', 3018: 'a', 3019: 'b', 3020: 'c', 3021: 'a', 3022: 'b', 3023: 'a', 3024: 'c',
    4001: 'b', 4002: 'c', 4003: 'a', 4004: 'a', 4005: 'a', 4006: 'b', 4007: 'b', 4008: 'c',
    4009: 'a', 4010: 'c', 4011: 'c', 4012: 'a', 4013: 'a', 4014: 'b', 4015: 'b', 4016: 'b',
    4017: 'c', 4018: 'a', 4019: 'b', 4020: 'c', 4021: 'c', 4022: 'a', 4023: 'a', 4024: 'b',
    4025: 'a', 4026: 'b', 4027: 'a', 4028: 'a', 4029: 'a', 4030: 'c', 4031: 'a', 4032: 'b',
    4033: 'a', 4034: 'b', 4035: 'a', 4036: 'c',
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

# Verify ALL 300 questions have correct answer matching PDF
print('=' * 70)
print('  FULL 300 QUESTION ANSWER VERIFICATION')
print('=' * 70)
print()

mismatches = []

for q_num in sorted(PDF_SOLUTIONS.keys()):
    q_str = str(q_num)
    pdf_answer = PDF_SOLUTIONS[q_num]

    if q_str in official_options:
        json_answer = official_options[q_str].get('correct')

        if json_answer != pdf_answer:
            mismatches.append({
                'q_num': q_num,
                'pdf': pdf_answer,
                'json': json_answer
            })

if mismatches:
    print(f'MISMATCHES FOUND: {len(mismatches)}')
    for m in mismatches:
        print(f"  Q{m['q_num']}: PDF={m['pdf']}, JSON={m['json']}")
else:
    print('✓ ALL 300 QUESTIONS HAVE CORRECT ANSWERS MATCHING PDF SOLUTION KEY')

# Also verify answer text matches the selected option
print()
print('=' * 70)
print('  ANSWER TEXT CONSISTENCY CHECK')
print('=' * 70)
print()

text_issues = []

for q_num in sorted(questions.keys()):
    q_str = str(q_num)
    _, answer_text = questions[q_num]

    if q_str in official_options:
        opts = official_options[q_str].get('options', [])
        correct_label = official_options[q_str].get('correct')

        # Find the correct option
        correct_opt = next((o for o in opts if o['label'] == correct_label), None)

        if correct_opt:
            # Check if answer text is contained in or matches the option
            answer_lower = answer_text.lower().rstrip('.')
            option_lower = correct_opt['text'].lower().rstrip('.')

            # They should be very similar or one contains the other
            match = (answer_lower in option_lower or
                    option_lower in answer_lower or
                    answer_lower == option_lower)

            if not match:
                text_issues.append({
                    'q_num': q_num,
                    'answer': answer_text,
                    'option': correct_opt['text'],
                    'label': correct_label
                })

if text_issues:
    print(f'POTENTIAL TEXT MISMATCHES: {len(text_issues)}')
    for issue in text_issues[:10]:
        print(f"  Q{issue['q_num']}: answer='{issue['answer']}' vs option {issue['label']}='{issue['option']}'")
else:
    print('✓ ALL ANSWER TEXTS MATCH THEIR CORRESPONDING OPTIONS')

print()
print('=' * 70)
print('  SUMMARY')
print('=' * 70)
print()
print(f'Total questions checked: 300')
print(f'Answer mismatches with PDF: {len(mismatches)}')
print(f'Text consistency issues: {len(text_issues)}')

if not mismatches and not text_issues:
    print()
    print('✓✓✓ ALL VERIFICATIONS PASSED ✓✓✓')
