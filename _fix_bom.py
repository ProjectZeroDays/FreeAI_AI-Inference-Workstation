import glob, os, ast, sys

# Fix BOM
fixed_bom = []
for f in glob.glob('**/*.py', recursive=True):
    if '__pycache__' in f or '.bak' in f:
        continue
    path = os.path.abspath(f)
    with open(path, 'rb') as fh:
        raw = fh.read()
    if raw[:3] == b'\xef\xbb\xbf':
        with open(path, 'wb') as fh:
            fh.write(raw[3:])
        fixed_bom.append(f)

# Check syntax
errors = []
for f in glob.glob('**/*.py', recursive=True):
    if '__pycache__' in f or '.bak' in f:
        continue
    try:
        with open(os.path.abspath(f), 'r', encoding='utf-8') as fh:
            ast.parse(fh.read())
    except SyntaxError as e:
        errors.append(f"{f}:{e.lineno}:{e.msg}")

with open('/tmp/fix_results.txt', 'w') as out:
    out.write(f"BOM fixed: {len(fixed_bom)} files\n")
    for f in fixed_bom:
        out.write(f"  {f}\n")
    out.write(f"Syntax errors: {len(errors)}\n")
    for e in errors:
        out.write(f"  {e}\n")
    out.write(f"Total py files: {len([f for f in glob.glob('**/*.py', recursive=True) if '__pycache__' not in f and '.bak' not in f])}\n")

print(f"BOM fixed: {len(fixed_bom)}")
print(f"Syntax errors: {len(errors)}")
for e in errors[:5]:
    print(f"  {e}")
