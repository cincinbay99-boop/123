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
# kept under 160 characters so search engines show it whole
META_DESC = ("Why an overlocked seam still frays, and what stops it: settings for fabric that sheds, "
             "securing the chain at both ends, and slippage beside intact stitches.")
assert len(META_DESC) <= 160, len(META_DESC)

# figure definitions: (class suffix, src, width, height, alt, eager)
# width/height are the pixel size of the original file (the template carries them on every image);
# the base figure crops to 3:2 with object-fit:cover, so a square or portrait photo shows its middle band.
FIG = {
 'hero': ('', 'https://images.pexels.com/photos/7998331/pexels-photo-7998331.jpeg?auto=compress&cs=tinysrgb&w=1600', 5616, 3744,
          'Hands feeding fabric through an overlocker', True),
 'machine': ('', 'https://images.pexels.com/photos/38561617/pexels-photo-38561617.jpeg?auto=compress&cs=tinysrgb&w=1600', 5152, 5152,
          'Close-up of an overlocker threaded with black thread', False),
 'frayed': ('', 'https://www.fashionme.com/wp-content/uploads/2026/09/fm-frayed-raw-edge-on-satin-fabric-b6a473141e.jpg', 2048, 2048,
          'Frayed raw edge on a woven fabric', False),
 # portrait original; the 3:2 crop keeps the dials and loses the spool holders at the bottom, so the alt names only the dials
 'dials': ('', 'https://images.pexels.com/photos/9850425/pexels-photo-9850425.jpeg?auto=compress&cs=tinysrgb&w=1600', 4052, 6078,
          'Tension dials on an overlocker seen from above', False),
 'cones': ('--portrait', 'https://images.pexels.com/photos/7256903/pexels-photo-7256903.jpeg?auto=compress&cs=tinysrgb&w=1200', 4016, 6016,
          'Cones of black thread on an overlocker', False),
 'presser': ('', 'https://www.fashionme.com/wp-content/uploads/2026/09/fm-fine-silk-fabric-under-a-sewing-machine-presser-foot-53d0f6451c.webp', 1000, 1000,
          'Fabric under a sewing machine presser foot', False),
 'slippage': ('', 'https://www.fashionme.com/wp-content/uploads/2026/09/fm-seam-being-pulled-to-show-slippage-beside-the-stitch-line-41ca44b6cc.jpg', 404, 720,
          'A seam pulled open to show slippage beside the stitch line', False),
 'wash': ('', 'https://www.fashionme.com/wp-content/uploads/2026/10/Garment-Wash-Test-Reference.jpg', 1600, 1067,
          'Washing machine drum used for a wash test', False),
 'ripper': ('', 'https://images.pexels.com/photos/32641558/pexels-photo-32641558.jpeg?auto=compress&cs=tinysrgb&w=1600', 6000, 4000,
          'Unpicking a seam with a seam ripper', False),
 'sewing': ('', 'https://www.fashionme.com/wp-content/uploads/2026/10/Sewing-Seam-Close-Up.jpg', 1600, 1068,
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

FIGURES_USED = set()

def fig_html(key):
    FIGURES_USED.add(key)
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

def smart_quotes(t):
    # the template's body is typeset with ’ “ ”; the Markdown keeps straight quotes (pandoc does the same conversion for the docx)
    t = t.replace("'", '’')
    return re.sub(r'"([^"]*)"', '“\\1”', t)

# [text](url); the URL may contain one level of parentheses, as in wiki/Overlock_(stitch)
LINK = re.compile(r'\[([^\]]+)\]\((https?://(?:[^()\s]|\([^()\s]*\))+)\)')

def inline(t):
    t = smart_quotes(html.escape(t, quote=False))
    return LINK.sub(r'<a href="\2">\1</a>', t)

def slug(s):
    s = re.sub(r"[^a-z0-9 ]", "", s.lower())
    return re.sub(r"\s+", "-", s.strip())

lines = open(SRC, encoding='utf-8').read().split('\n')
title = lines[0][2:].strip()
assert lines[0].startswith('# '), 'first line must be the # title'

# This is a small parser for the subset of Markdown the article uses: # title, ## and ### headings,
# paragraphs, pipe tables, flat - and 1. lists, [text](url) links. Pandoc (which makes the docx) accepts
# much more; anything it would render differently is refused here so the two outputs cannot drift apart.
MARKER = re.compile(r'^(#{2,3} |\||\d+\. |- )')
for n, ln in enumerate(lines[1:], start=2):
    if not ln.strip():
        continue
    if ln[0].isspace():
        sys.exit(f'line {n}: indented line (nested list or code block) is not supported')
    if '`' in ln or '*' in ln or '\\|' in ln:
        sys.exit(f'line {n}: inline code, emphasis and escaped pipes are not supported')
    if ln.startswith('#') and not MARKER.match(ln):
        sys.exit(f'line {n}: only ## and ### headings are supported after the title')

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
            if not all(c and set(c) <= set(':-') for c in cells):   # skip the |---|:---| separator row
                rows.append(cells)
            i += 1
        widths = {len(r) for r in rows}
        if len(widths) != 1:
            sys.exit(f'table ending at line {i}: rows have different cell counts {sorted(widths)}')
        blocks.append(('table', rows)); continue
    if re.match(r'^(\d+\. |- )', ln):
        items = []
        while i < len(lines) and re.match(r'^(\d+\. |- )', lines[i]):
            items.append(re.sub(r'^(\d+\. |- )', '', lines[i])); i += 1
        blocks.append(('list', items)); continue
    # paragraph: consecutive non-blank lines up to the next blank line or block marker are one paragraph, as in pandoc
    para = [ln.strip()]; i += 1
    while i < len(lines) and lines[i].strip() and not MARKER.match(lines[i]):
        para.append(lines[i].strip()); i += 1
    blocks.append(('p', ' '.join(para)))

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
    # bold the first sentence: up to the first full stop that is followed by a space (so "2.5 mm" does not end it)
    m = re.match(r'^(.+?\.)\s+(\S.*)$', item)
    if m:
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
# keep an h3 with the paragraph that follows it when printed, as the template does for h2
head = head.replace(f'  #{NEW_ID} h2{{\n    break-after:avoid;\n  }}',
                    f'  #{NEW_ID} h2,\n  #{NEW_ID} h3{{\n    break-after:avoid;\n  }}')
assert f'#{NEW_ID} h3{{\n    break-after:avoid' in head, 'print rule for h3 not inserted'

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

# every figure in FIG must have found its place; a paragraph edit that shifts the counts in PLACE would otherwise drop one silently
missing = set(FIG) - FIGURES_USED
assert not missing, f'figures not placed (check PLACE against the paragraphs): {sorted(missing)}'

open(OUT, 'w', encoding='utf-8').write(head + '</head>\n\n' + '\n'.join(body))
print('written', OUT)
