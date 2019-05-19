# -*- coding: utf-8 -*-
import re

#FILE_NAME="1810292ho.txt"
#FILE_NAME="1901073ho.txt"
#FILE_NAME='testdata/1901241ho.txt'
#FILE_NAME='1903061ho.txt'
#FILE_NAME='1905063ho.txt'
FILE_NAME='1905171ho.txt'
FILE_CSV="out_{}-{}.csv"
EMPTY=re.compile('^\\s*$')
SWEEP=re.compile('^Sweep')
DOT_TO_COMMA=True


postfixes={
        'f': 1e-15,
        'p': 1e-12,
        'n': 1e-9,
        'u': 1e-6,
        'µ': 1e-6,
        'm': 1e-3,
        '':  1,
        'k': 1e3,
        'M': 1e6,
        'G': 1e9,
        'T': 1e12,
        }

def get_postfix(token):
    last_char=token[-1]
    if last_char in postfixes:
        return token[:-1], postfixes[last_char]
    else:
        return token, 1


class Series():
    def __init__(self, header_lines):
        self.entries=[]
        self.header_lines = header_lines
        self.measures=self.parse_measures(header_lines)

    def parse_measures(self, headers):
        def get_for_field(c,f):
            if   'Sweep'    in f: return ''
            elif 'time'     in f: return ''
            elif '[A]'      in f: return 'p'
            elif 'Constant' in f: return 'm'
            elif 'a5/b4'    in f: return 'M'
            else: return ''

        last_headers_line = headers[len(headers)-1]
        fields = last_headers_line.replace(',','\t').split('\t')
        result = [ get_for_field(c,f) for c,f in enumerate(fields)  ]
        return result

    def add_entry(self, entry):
        self.entries.append(entry)

    def format_file_name(self, counter):
        series_name = self.header_lines[0].split()[0][:-1] # First line's first word without the trailing comma
        return FILE_CSV.format(counter, series_name)

    def to_csv(self):
        headers = list(map(lambda l: l.replace(',', '\t'), self.header_lines ))
        entries = list(map(lambda x: x.to_csv_line(self.measures), self.entries))
        return "\r\n".join(headers + entries)


class Entry():
    def __init__(self, v):
        self.v = v

    def to_csv_line(self, measures):
        string_fields = []
        string_fields.append('{}'.format(int(self.v[0]))) # First is sweep. That is an iint
        for c, field in enumerate(self.v[1:]):
            measure = measures[c+1];
            divider=postfixes[measure]
            string_fields.append( '{:.15f}'.format(field / divider)  )

        result = '\t'.join(string_fields)
        return result.replace(".", ",")

def read_lines():
    with open(FILE_NAME, errors='ignore') as f:
        return f.readlines()


def write_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)


def skip_line(content):
    if not content:
        return None, []
    else:
        return (content[0].strip(), content[1:])


def skip_until_prefix(content, prefix):
    while content:
        line, content = skip_line(content)
        if line.startswith(prefix):
            return (line, content)
    return None, None


def token_value(token):
    word, multiplier = get_postfix(token)
    return float(word)*multiplier


def parse_line(line):
    if not line or EMPTY.match(line): return None
    tokens = line.replace(',','').split()
    values = list(map(token_value, tokens))
    return Entry(values)

def read_next_series(content):
    all_content = "\n".join(content)
    if all_content.find('SERIES_') >= 0:
        return read_next_series_regular(content)
    else:
        return read_next_series_no_header(content)

def read_next_series_regular(content):
    line_header_1, content = skip_until_prefix(content, 'SERIES_')
    if not line_header_1: return None, None
    line_header_2, content = skip_line(content)
    line_header_3, content = skip_line(content)
    line_header_4, content = skip_line(content)

    series = Series([line_header_1, line_header_2, line_header_3, line_header_4])
    entry_line, content = skip_line(content)
    while entry_line is not None and not EMPTY.match(entry_line):
        entry = parse_line(entry_line)
        series.add_entry(entry)
        entry_line, content = skip_line(content)
    return series, content

def read_next_series_no_header(content):
    line_header_1, content = skip_until_prefix(content, 'Sweep')
    if not line_header_1: return None, None

    series = Series([line_header_1])
    prev_content=content
    entry_line, content = skip_line(content)
    while entry_line is not None and not EMPTY.match(entry_line) and not SWEEP.match(entry_line):
        entry = parse_line(entry_line)
        series.add_entry(entry)
        prev_content = content
        entry_line, content = skip_line(content)
    return series, prev_content


def process_content(content):
    result = []
    counter = 1
    while True:
        s, content = read_next_series(content)
        if s is None: break
        filename=s.format_file_name(counter)
        csv=s.to_csv()
        result.append( (filename, csv) )
        counter+=1
    return result


if __name__ == '__main__':
    content = read_lines()
    l = process_content(content)
    for name, csv in l:
        write_file(name, csv)
