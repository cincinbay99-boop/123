#!/usr/bin/env python3
"""Build overlock-seams-that-stop-fraying.html from the Markdown article and the
site template. Run it from anywhere; the defaults point at the files next to
this script:

    python3 build_html.py
    python3 build_html.py --src article.md --template template.html --out page.html
"""
import argparse, os, re, html, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
_ap.add_argument('--src', default=os.path.join(HERE, 'overlock-seams-that-stop-fraying.md'), help='Markdown article')
_ap.add_argument('--template', default=os.path.join(HERE, 'template-what-is-private-label-apparel.html'), help='site template HTML')
_ap.add_argument('--out', default=os.path.join(HERE, 'overlock-seams-that-stop-fraying.html'), help='HTML to write')
_args = _ap.parse_args()
SRC, TPL, OUT = _args.src, _args.template, _args.out

OLD_ID = 'fm-private-label'
NEW_ID = 'fm-overlock-seams'
META_DESC = ("Why an overlocked seam still frays, and what stops it: the settings that hold on fabric that sheds, "
             "how to secure the thread chain at both ends, and when the fabric itself is slipping beside intact stitches.")

# figure definitions: (class suffix, src, width, height, alt, eager)
FIG = {
 'hero': ('', 'https://images.pexels.com/photos/7998331/pexels-photo-7998331.jpeg?auto=compress&cs=tinysrgb&w=1600', 5616, 3744,
          'Hands feeding fabric through an overlocker', True),
 'machine': ('', 'https://images.pexels.com/photos/38561617/pexels-photo-38561617.jpeg?auto=compress&cs=tinysrgb&w=1600', None, None,
          'Close-up of an overlocker threaded with black thread', False),
 'frayed': ('', 'https://www.fashionme.com/wp-content/uploads/2026/09/fm-frayed-raw-edge-on-satin-fabric-b6a473141e.jpg', None, None,
          'Frayed raw edge on a woven fabric', False),
 'dials': ('', 'https://images.pexels.com/photos/9850425/pexels-photo-9850425.jpeg?auto=compress&cs=tinysrgb&w=1600', None, None,
          'Overlocker tension dials and thread spools seen from above', False),
 'cones': ('--portrait', 'https://images.pexels.com/photos/7256903/pexels-photo-7256903.jpeg?auto=compress&cs=tinysrgb&w=1200', 4016, 6016,
          'Cones of black thread on an overlocker', False),
 'presser': ('', 'https://www.fashionme.com/wp-content/uploads/2026/09/fm-fine-silk-fabric-under-a-sewing-machine-presser-foot-53d0f6451c.webp', None, None,
          'Fabric under a sewing machine presser foot', False),
 'slippage': ('', 'https://www.fashionme.com/wp-content/uploads/2026/09/fm-seam-being-pulled-to-show-slippage-beside-the-stitch-line-41ca44b6cc.jpg', None, None,
          'A seam pulled open to show slippage beside the stitch line', False),
 'wash': ('', 'https://www.fashionme.com/wp-content/uploads/2026/10/Garment-Wash-Test-Reference.jpg', None, None,
          'Washing machine drum used for a wash test', False),
 'ripper': ('', 'https://images.pexels.com/photos/32641558/pexels-photo-32641558.jpeg?auto=compress&cs=tinysrgb&w=1600', 6000, 4000,
          'Unpicking a seam with a seam ripper', False),
 'sewing': ('', 'https://www.fashionme.com/wp-content/uploads/2026/10/Sewing-Seam-Close-Up.jpg', None, None,
          'Sewing machine stitching a seam', False),
}

# where figures go: section slug -> {paragraph index (1-based, counting <p> emitted in that section): figure key}
PLACE = {
 'what-the-stitch-is-doing-to-the-cut-edge': {1: 'machine'},
 'how-an-overlocked-seam-frays': {1: 'frayed'},
 'settings-that-hold-on-fabric-that-sheds': {2: 'dials', 'after-h3:Thread': 'cones', 'after-h3:Three threads or four': 'presser'},
 'seam-slippage': {1: 'slippage'},
 'washing-a-sample': {1: 'wash'},
 'repairs': {1: 'ripper'},
 'without-an-overlocker': {1: 'sewing'},
}

def fig_html(key):
    cls, src, w, h, alt, eager = FIG[key]
    attrs = [f'src="{src}"']
    if w: attrs.append(f'width="{w}"'); attrs.append(f'height="{h}"')
    attrs.append(f'alt="{html.escape(alt)}"')
    if eager:
        attrs += ['loading="eager"', 'fetchpriority="high"', 'decoding="async"']
    else:
        attrs += ['loading="lazy"', 'decoding="async"']
    c = 'fm-article-image' + (f' fm-article-image{cls}' if cls else '')
    return f'<figure class="{c}">\n<img\n  ' + '\n  '.join(attrs) + '>\n</figure>\n'

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', t)
    return t

def slug(s):
    s = re.sub(r"[^a-z0-9 ]", "", s.lower())
    return re.sub(r"\s+", "-", s.strip())

lines = open(SRC, encoding='utf-8').read().split('\n')
title = lines[0][2:].strip()
blocks = []  # (kind, payload)
i = 1
while i < len(lines):
    ln = lines[i]
    if not ln.strip():
        i += 1; continue
    if ln.startswith('## '):
        blocks.append(('h2', ln[3:].strip())); i += 1; continue
    if ln.startswith('### '):
        blocks.append(('h3', ln[4:].strip())); i += 1; continue
    if ln.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(set(c) <= set('-') for c in cells):
                rows.append(cells)
            i += 1
        blocks.append(('table', rows)); continue
    m = re.match(r'^(\d+)\. (.*)$', ln)
    if m or ln.startswith('- '):
        items = []
        while i < len(lines) and (re.match(r'^(\d+)\. ', lines[i]) or lines[i].startswith('- ')):
            items.append(re.sub(r'^(\d+\. |- )', '', lines[i])); i += 1
        blocks.append(('list', items)); continue
    blocks.append(('p', ln.strip())); i += 1

# build sections
intro, sections = [], []
cur = None
for kind, payload in blocks:
    if kind == 'h2':
        cur = {'title': payload, 'id': slug(payload), 'blocks': []}
        sections.append(cur)
    elif cur is None:
        intro.append((kind, payload))
    else:
        cur['blocks'].append((kind, payload))

def bold_lead(item):
    m = re.match(r'^([^.]+\.)\s+(.*)$', item)
    if m and m.group(2):
        return f'<strong>{inline(m.group(1))}</strong> {inline(m.group(2))}'
    return inline(item)

def render_section(sec):
    out = []
    out.append(f'<section class="fm-section" id="{sec["id"]}">\n\n<h2>{html.escape(sec["title"])}</h2>\n')
    pcount = 0
    place = PLACE.get(sec['id'], {})
    prev_p = ''
    for kind, payload in sec['blocks']:
        if kind == 'p':
            pcount += 1
            out.append(f'<p>{inline(payload)}</p>\n')
            if pcount in place:
                out.append(fig_html(place[pcount]))
            prev_p = payload
        elif kind == 'h3':
            out.append(f'<h3>{html.escape(payload)}</h3>\n')
            pcount = 0
            key = PLACE.get(sec['id'], {}).get('after-h3:' + payload)
            place = {1: key} if key else {}
        elif kind == 'table':
            head, body = payload[0], payload[1:]
            t = ['<div class="fm-table-wrap">\n<table>\n<thead>\n<tr>']
            t += [f'<th scope="col">{inline(c)}</th>' for c in head]
            t.append('</tr>\n</thead>\n\n<tbody>')
            for r in body:
                t.append('<tr>\n' + '\n'.join(f'<td>{inline(c)}</td>' for c in r) + '\n</tr>\n')
            t.append('</tbody>\n</table>\n</div>\n')
            out.append('\n'.join(t))
        elif kind == 'list':
            lead = prev_p.rstrip()
            if sec['id'] == 'sources':
                for it in payload:
                    out.append(f'<p>{inline(it)}</p>\n')
            elif lead.endswith('at the start:'):
                for it in payload:
                    out.append(f'<p>{inline(it)}</p>\n')
            else:
                for it in payload:
                    out.append(f'<p>{bold_lead(it)}</p>\n')
    out.append('\n</section>\n')
    return '\n'.join(out)

# the template may be saved with CRLF line endings; the CSS rules below are matched with LF
tpl = open(TPL, encoding='utf-8', newline='').read().replace('\r\n', '\n').replace('\r', '\n')
head_end = tpl.index('</head>')
head = tpl[:head_end]
head = head.replace(OLD_ID, NEW_ID)
head = re.sub(r'<title>.*?</title>', f'<title>{html.escape(title)}</title>', head)
head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(META_DESC)}">', head)
# add h3 to the heading rules (same family and weight as h1/h2; a size between h2 and body)
head = head.replace(f'#{NEW_ID} h1,\n#{NEW_ID} h2{{', f'#{NEW_ID} h1,\n#{NEW_ID} h2,\n#{NEW_ID} h3{{')
head = head.replace(f'#{NEW_ID} h2{{\n  margin-top:0;\n  margin-bottom:24px;\n  font-size:28px;\n  line-height:1.18;\n  letter-spacing:-.025em;\n}}',
 f'#{NEW_ID} h2{{\n  margin-top:0;\n  margin-bottom:24px;\n  font-size:28px;\n  line-height:1.18;\n  letter-spacing:-.025em;\n}}\n\n#{NEW_ID} h3{{\n  margin-top:34px;\n  margin-bottom:16px;\n  font-size:21px;\n  line-height:1.3;\n  letter-spacing:-.015em;\n}}')
assert f'#{NEW_ID} h3{{' in head, 'h3 rule not inserted'

body = []
body.append(f'<body>\n\n<div id="{NEW_ID}-stage">\n\n<article id="{NEW_ID}" aria-labelledby="{NEW_ID}-title">\n\n<div class="fm-intro">\n\n<h1 id="{NEW_ID}-title">{html.escape(title)}</h1>\n')
for kind, payload in intro:
    body.append(f'<p>{inline(payload)}</p>\n')
body.append('</div>\n')
body.append(fig_html('hero'))
body.append('<nav class="fm-toc" aria-label="Article contents">\n\n<p class="fm-toc-label">Contents</p>\n\n<ol>')
for s in sections:
    body.append(f'<li><a href="#{s["id"]}">{html.escape(s["title"])}</a></li>')
body.append('</ol>\n\n</nav>\n\n')
for s in sections:
    body.append(render_section(s))
body.append('</article>\n\n</div>\n\n</body>\n</html>\n')

open(OUT, 'w', encoding='utf-8').write(head + '</head>\n\n' + '\n'.join(body))
print('written', OUT)
