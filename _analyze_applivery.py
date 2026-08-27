import os, re

desktop = r'C:\Users\Project Zero\Desktop'
mhtml_files = [f for f in os.listdir(desktop) if f.lower().endswith('.mhtml')]
print('MHTML files found:', mhtml_files)

if mhtml_files:
    path = os.path.join(desktop, mhtml_files[0])
    print('Reading:', path)
    with open(path, encoding='utf-8', errors='replace') as f:
        content = f.read()
    print('Total length:', len(content))

    # Extract HTML body from mhtml
    # MHTML files have multipart format with Content-Type headers
    html_match = re.search(r'Content-Type:\s*text/html\s*\r?\n\r?\n(.*?)(?:\r?\n--|$)', content, re.DOTALL | re.IGNORECASE)
    if html_match:
        html = html_match.group(1)
    else:
        # Try different mhtml format
        html = content

    print('HTML length:', len(html))

    # Extract styles
    styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    print('Style blocks:', len(styles))
    for i, s in enumerate(styles[:2]):
        print(f'\n--- Style {i+1} (len={len(s)}) ---')
        print(s[:2000])

    # Colors
    colors = re.findall(r'#[0-9a-fA-F]{3,8}', html)
    unique_colors = list(set(colors))
    print(f'\nUnique colors ({len(unique_colors)}):', unique_colors[:30])

    # Fonts
    fonts = re.findall(r'font-family:\s*([^;"}\']+)', html, re.IGNORECASE)
    print('Fonts:', list(set(fonts))[:15])

    # Sections/headings
    headings = re.findall(r'<h([1-6])([^>]*)>(.*?)</h\1>', html, re.DOTALL | re.IGNORECASE)
    print('\nHeadings:')
    for level, attrs, text in headings[:15]:
        clean = re.sub(r'<[^>]+>', '', text).strip()
        if clean:
            print(f'  H{level}: {clean[:80]}')

    # Save extracted HTML
    out_path = r'C:\Users\Project Zero\ai-workstation\_applivery_design.html'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html[:80000])
    print(f'\nSaved {len(html[:80000])} chars to _applivery_design.html')
else:
    print('No mhtml files found on desktop')
