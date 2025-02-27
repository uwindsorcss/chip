from itertools import islice;
import os;
import pathlib;
import re;
from time import time;
import markdown;
import tables;
LEN_LIM = 700;
REPO_URL = 'https://github.com/uwindsorcss/wiki.git';
TARGET_DIR = '.';
def recursive_directory_iterator(pth):
    for i in pth.iterdir():
        if i.is_dir():
            yield from recursive_directory_iterator(i);
        else:
            yield i;
def traverse(ts):
    if pathlib.Path('.git').exists():
        os.system('git pull');
        try:
            it = recursive_directory_iterator(pathlib.Path(TARGET_DIR));
            dat = '';
            for p in it:
                if p.suffix == '.md':
                    lmt = p.stat().st_mtime;
                    if lmt > ts:
                        dat += generate(p);
            with open("updated.csv", 'w') as fh:
                fh.write(dat);
        except OSError as e:
            print(e);
    else:
        os.system('git clone ' + REPO_URL);
        print('Run the script again, inside the wiki repository this time.');
def generate(pth):
    print(pth);
    rows = '';
    rowcurr = '';
    rcnt = 1;
    parsed = markdown.markdown(pth.read_text());
    plain = str(parsed);
    plain = re.sub(r'<[^>]+>', '', plain);
    plain, tbls = tables.extract_tables(plain);
    parags = plain.split('\n\n');
    for p in parags:
        p = p.replace('\n', ' ');
        p = p.strip() + ' ';
        if len(rowcurr) + len(p) > LEN_LIM:
            rowcurr = rowcurr.strip();
            rows += str(pth) + ' part ' + str(rcnt) + ',' + '"' + rowcurr + '"' + '\n';
            rowcurr = p;
            rcnt += 1;
        else:
            rowcurr += p;
    if len(rowcurr) > 0:
        rows += str(pth) + ' part ' + str(rcnt) + ',' + '"' + rowcurr + '"' + '\n';
    rcnt = 1;
    for h, b in tbls:
        key = h[0];
        rowcurr = '';
        for r in b:
            val = r[0];
            rowcurr += '- ' + key + ' ' + val + ':\\n';
            for name, x in islice(zip(h, r), 1, None):
                rowcurr += '    - ' + name + ': ' + x + '\\n';
        rows += str(pth) + ' table ' + str(rcnt) + ',' + '"' + rowcurr + '"';
        rows += '\n';
        rcnt += 1;
    return rows;
timestamp = 0;
try:
    with open('timestamp.txt') as fh:
        cont = fh.readline().strip();
        timestamp = int(cont);
except:
    pass;
traverse(timestamp);
with open('timestamp.txt' , 'w') as fh:
    ts = int(time());
    print(ts, file = fh);
