import re

sections = [
    ("beranda", 340, 760),
    ("profil", 760, 873),
    ("struktur", 873, 914),
    ("arsip", 914, 1044),
    ("anggota", 1044, 1193),
    ("proker", 1193, 1263),
    ("anggaran", 1263, 1423),
    ("formulir", 1423, 1493),
    ("aspirasi", 1493, 1652),
    ("berita", 1652, 1717),
    ("galeri", 1717, 1752),
    ("kontak", 1752, 1874),
]

with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for name, start, end in sections:
    sec = "".join(lines[start-1:end-1])
    vars_found = set(re.findall(r'\{\{\s*([a-zA-Z0-9_\.]+)', sec))
    tags_found = set(re.findall(r'\{%\s*([a-zA-Z0-9_]+)', sec))
    print(f"=== Section {name} ===")
    print("Variables:", sorted(list(vars_found)))
    print("Tags:", sorted(list(tags_found)))
