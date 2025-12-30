#!/usr/bin/env python3
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

app = create_app('development')
with app.test_client() as c:
    r = c.get('/films')
    s = r.get_data(as_text=True)
    print(s[:2000])
    m = re.search(r'<img[^>]+src=\"([^\"]+)\"', s)
    if m:
        print('\\nFIRST IMG SRC:', m.group(1))
    else:
        print('\\nNO IMG TAG FOUND')


