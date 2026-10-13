import os, re, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(HERE, 'overlock-seams-that-stop-fraying.md'), encoding='utf-8').read()
body = t.split('\n## Sources')[0]   # everything before the Sources heading
words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'’/.%-]*", body)
print('body words:', len(words))
print('double quotes:', body.count('"'))
print('em dash:', body.count('—'), 'en dash:', body.count('–'))
print('hyphen ranges (should be en dashes):', re.findall(r'\b\d+(?:\.\d+)?-\d+(?:\.\d+)?\b', body))
print('exclamation:', body.count('!'))
print('"X to Y" numeric ranges:', len(re.findall(r'\b\d+(?:\.\d+)?\s+to\s+\d+', body)))
print('word ranges (four to six etc):', re.findall(r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\s+to\s+(?:one|two|three|four|five|six|seven|eight|nine|ten)\b', body))
# paragraphs: prose only, skip headings, tables, list items
paras = [p.strip() for p in body.split('\n\n') if p.strip() and not p.startswith(('#','|','-','1.','2.','3.','4.','5.'))]
first_lens=[]; rest_lens=[]; short_total=0; short_first=0
for p in paras:
    sents = re.split(r'(?<=[.?!])\s+(?=[A-Z"])', p)
    for i,s in enumerate(sents):
        n = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’/.%-]*", s))
        if n==0: continue
        (first_lens if i==0 else rest_lens).append(n)
        if n<=6:
            short_total+=1
            if i==0: short_first+=1
print('prose paragraphs:', len(paras))
print('mean first-sentence length:', round(statistics.mean(first_lens),1), ' mean other sentences:', round(statistics.mean(rest_lens),1))
print('sentences <=6 words:', short_total, ' of which paragraph-first:', short_first)
print('first sentence lengths:', first_lens)
