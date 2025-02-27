import re;
TABLE_START_CHAR = '|';
def extract_tables(txt):
    lns = txt.split('\n');
    started = False;
    header = None;
    body = None;
    tables = list();
    ntxt = '';
    for n in lns:
        if n.startswith(TABLE_START_CHAR):
            cols = n.split(TABLE_START_CHAR);
            cols = list(map(lambda x: x.strip(), filter(not_empty, cols)));
            if not started:
                started = True;
                header = cols;
                body = list();
            elif not_divider(cols):
                body.append(cols);
        elif not header is None:
            tables.append((header, body));
            started = False;
            header = None;
            body = None;
        if not started:
            ntxt += n + '\n';
    return ntxt, tables;
def not_divider(c):
    return all(map(lambda x: len(re.sub('[-\\s:]+', '', x)) > 0, c));
def not_empty(s):
    return len(s.strip()) > 0;
