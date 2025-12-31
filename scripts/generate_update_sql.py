#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 scripts/poster_mapping.csv 生成批量更新 SQL（update_posters.sql）
每行格式：UPDATE film SET poster_url='FILENAME' WHERE id=ID;
"""
import os, csv, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT = os.path.join('scripts', 'poster_mapping.csv')
OUT = os.path.join('scripts', 'update_posters.sql')

if not os.path.exists(INPUT):
    print('找不到', INPUT)
    sys.exit(1)

with open(INPUT, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

with open(OUT, 'w', encoding='utf-8') as outf:
    outf.write('-- Backup your DB before running these updates\n')
    for r in rows:
        fid = r.get('id')
        suggested = r.get('suggested_local_filename') or r.get('suggested_english_filename') or ''
        if not suggested:
            continue
        # ensure ascii-friendly filename
        safe = suggested.replace("'", "''")
        outf.write("UPDATE film SET poster_url='%s' WHERE id=%s;\n" % (safe, fid))

print('SQL update script generated at', OUT)


