from os.path import join
from csv import reader
from json import dumps
import re

MIN_DIALOG_LENGTH = 6

CHARS = join('data', 'characters.tsv')
DIALOGS = join('data', 'dialogs.tsv')
LINES = join('data', 'lines.tsv')

charfields = ['id', 'name', 'm_id', 'm_title', 'gender', 'pos']
dialogfields = ['id_1', 'id_2', 'm_id', 'lines']
linefields = ['line_id', 'id', 'm_id', 'name', 'text']


def load(tsvfile, fields):
    data = []
    with open(tsvfile, 'r') as fd:
        for line in reader(fd, delimiter='\t', quotechar='"'):
            current = {}
            for field, value in zip(fields, line):
                current[field] = value
            data.append(current)
    return data


def get_female_ids():
    # instead of taking female characters directly, we put all female names into
    # list and then we treat all characters with that names as female
    all_chars = load(CHARS, charfields)
    female_names = []
    for char in all_chars:
        try:
            if char['gender'] in ['f', 'F']:
                female_names.append(char['name'])
        except KeyError:
            continue
    female_chars = []
    for char in all_chars:
        try:
            if char['name'] in female_names:
                female_chars.append(char['id'])
        except KeyError:
            continue
    return female_chars


def get_female_dialogs():
    female_ids = get_female_ids()
    all_dialogs_raw = load(DIALOGS, dialogfields)
    female_dialogs = []
    re_line = re.compile('(L\d*)')
    for dialog in all_dialogs_raw:
        lines = re_line.findall(dialog['lines'])
        if len(lines) < MIN_DIALOG_LENGTH:
            continue
        if dialog['id_1'] in female_ids:
            if dialog['id_2'] in female_ids:
                female_dialogs.append(lines)
    return female_dialogs


def get_female_dialog_lines():
    all_lines = load(LINES, linefields)
    female_dialogs = get_female_dialogs()
    female_dialog_text = []
    for dialog in female_dialogs:
        conversation = []
        correct = True
        for number, line in enumerate(dialog):
            current_line = [i['text'] for i in all_lines if i['line_id'] == line]
            if len(current_line) == 0:
                correct = False
                continue
            talker_number = (number % 2) + 1
            conversation.append({talker_number: current_line[0]})
        if correct is not True:
            continue
        female_dialog_text.append(conversation)
    return female_dialog_text


def main():
    female_dialog_lines = get_female_dialog_lines()
    json_dataset = dumps(female_dialog_lines)
    with open('dialogs.json', 'w') as fd:
        fd.write(json_dataset)


if __name__ == '__main__':
    main()
