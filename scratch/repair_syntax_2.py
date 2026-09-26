import codecs

def fix_it():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_idx = -1
    end_idx = -1

    for i, line in enumerate(lines):
        if 'const hasEnemySummonPhrase = text.includes(' in line:
            if start_idx == -1:
                start_idx = i
        if 'return hasEnemySummonPhrase;' in line:
            end_idx = i + 1
            break

    if start_idx != -1 and end_idx != -1:
        print(f'Replacing lines {start_idx} to {end_idx}')
        
        correct_lines = [
            '  const hasEnemySummonPhrase = text.includes("\\u53ec\\u559a") || text.includes("\\u7279\\u6b8a\\u53ec\\u559a"); // "召喚" or "特殊召喚"\\r\\n',
            '  return hasEnemySummonPhrase;\\r\\n',
            '}\\r\\n'
        ]
        
        new_lines = lines[:start_idx] + correct_lines + lines[end_idx+1:]
        with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print('Fixed!')
    else:
        print('Could not find start or end.')

fix_it()
