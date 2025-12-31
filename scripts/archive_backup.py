#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 instance 下最新的 app.db.bak.* 复制到 scripts/backups/
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(ROOT, "instance")
dst_dir = os.path.join(ROOT, "scripts", "backups")
os.makedirs(dst_dir, exist_ok=True)

files = [f for f in os.listdir(src_dir) if f.startswith("app.db.bak.")]
if not files:
    print("no backup files found in instance/")
    raise SystemExit(0)
files.sort()
latest = files[-1]
src = os.path.join(src_dir, latest)
dst = os.path.join(dst_dir, latest)
shutil.copy2(src, dst)
print("copied", src, "->", dst)
