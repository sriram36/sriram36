"""Builds this profile: README.md and the dark SVG graphics it is made of.

Everything visible is generated here, so no outside widget can break and nothing is typed by hand twice:
  banner.svg         a curl line types out, then the response fades in
  career.svg         my internships drawn as a git graph (branches, merges, the Zennith pause)
  card-*.svg         one card per featured project
  heartbeat.svg      my public pushes over the last 60 days, drawn as an ECG line (live data)
  hire.svg           the closing POST /hire card
A GitHub Action runs this every Monday.

Usage:  python build.py        (set GITHUB_TOKEN to avoid the unauthenticated API rate limit)
Standard library only.
"""
import datetime, json, os, sys, textwrap, time, urllib.request
from html import escape
from pathlib import Path

USER = 'sriram36'
HERE = Path(__file__).resolve().parent

BG = '#000000'
ACC = '#6ee7b7'                      # the one accent: only for things that are live
W1, W2, W3 = '#fafafa', '#c4c4c4', '#8a8a8a'
TXT, MUT, DIM = '#fafafa', '#a3a3a3', '#5f5f5f'
MINT, BLUE, VIOLET, AMBER = ACC, W2, W1, W3   # old names, now mapped onto the black palette
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "'Segoe UI',system-ui,-apple-system,Helvetica,Arial,sans-serif"


# ----------------------------------------------------------------------------- helpers
CACHE_FILE = HERE / '.api_cache.json'   # local runs only: spares the 60-calls-an-hour limit while iterating
CACHE_TTL = 6 * 3600


def api(path, retries=0):
    cache = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
    hit = cache.get(path)
    if hit and time.time() - hit[0] < CACHE_TTL:
        return hit[1]
    req = urllib.request.Request('https://api.github.com' + path,
                                 headers={'User-Agent': 'profile-readme-build', 'Accept': 'application/vnd.github+json'})
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    for attempt in range(retries + 1):
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
            if r.status == 202 and attempt < retries:   # GitHub is still computing a statistic
                time.sleep(3)
                continue
            data = json.loads(body) if body.strip() else None
        break
    if data and not token:   # never cache an empty answer: GitHub returns {} while it is still computing a statistic
        cache[path] = [time.time(), data]
        CACHE_FILE.write_text(json.dumps(cache))
    return data


def fade(begin, dur=0.5):
    return '<animate attributeName="opacity" from="0" to="1" begin="%ss" dur="%ss" fill="freeze"/>' % (begin, dur)


def text(x, y, s, size=14, fill=TXT, family=MONO, weight=None, anchor=None, begin=None, extra=''):
    a = ' font-family="%s" font-size="%s" fill="%s"' % (family, size, fill)
    if weight: a += ' font-weight="%s"' % weight
    if anchor: a += ' text-anchor="%s"' % anchor
    if begin is not None:
        return '<text x="%s" y="%s"%s opacity="0"%s>%s%s</text>' % (x, y, a, extra, escape(s), fade(begin))
    return '<text x="%s" y="%s"%s%s>%s</text>' % (x, y, a, extra, escape(s))


def frame(w, h, title, body, glow=None):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-labelledby="t">\n'
            '<title id="t">%s</title>\n'
            '<defs><linearGradient id="sh" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#fff" stop-opacity=".07"/>'
            '<stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>\n'
            '<rect width="%d" height="%d" rx="16" fill="%s"/><rect width="%d" height="%d" rx="16" fill="url(#sh)"/>'
            '<rect x=".5" y=".5" width="%d" height="%d" rx="15.5" fill="none" stroke="#fff" stroke-opacity=".14"/>\n'
            '%s\n</svg>\n'
            % (w, h, w, h, escape(title), w, h, BG, w, h, w - 1, h - 1, body))


def draw(d, color, begin, dur, width=2.5, extra=''):
    """A path that draws itself once and stays."""
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"%s>'
            '<animate attributeName="stroke-dashoffset" from="1" to="0" begin="%ss" dur="%ss" fill="freeze"/></path>' % (d, color, width, extra, begin, dur))


def dot(x, y, color, begin, r=5.5):
    return ('<circle cx="%.1f" cy="%d" r="%s" fill="%s" stroke="%s" stroke-width="2.5" opacity="0">%s</circle>' % (x, y, r, color, BG, fade(begin, 0.3)))


# ----------------------------------------------------------------------------- banner
def banner(version):
    W, H = 830, 250
    cmd = 'curl -i github.com/sriram36'
    cw = 14 * 0.6
    n = len(cmd)
    steps = ';'.join('%.1f' % (i * cw + (40 if i == n else 0)) for i in range(n + 1))
    kt = ';'.join('%.4f' % (i / n) for i in range(n + 1))
    body = (
        '<clipPath id="c"><rect x="52" y="30" width="0" height="26"><animate attributeName="width" values="%s" keyTimes="%s" calcMode="discrete" begin="0.5s" dur="1.5s" fill="freeze"/></rect></clipPath>' % (steps, kt)
        + text(36, 48, '$', 14, MINT) + text(52, 48, cmd, 14, MUT, extra=' clip-path="url(#c)"')
        + text(36, 76, 'HTTP/1.1 200 OK', 14, MINT, begin=2.1)
        + ''.join(text(W - 36, 48 + i * 19, h, 12.5, DIM, anchor='end', begin=2.3 + i * 0.2) for i, h in enumerate(
            ['x-location: india', 'x-internships: 3', 'x-deployed-apps: 2', 'x-version: ' + version]))
        + text(36, 140, 'Sriram Kolli', 54, TXT, SANS, 600, begin=2.4, extra=' letter-spacing="-1.5"')
        + text(36, 176, 'Backend-focused full-stack engineer. FastAPI, PostgreSQL, agentic AI.', 19, MUT, SANS, begin=2.9)
        + '<g opacity="0"><circle cx="42" cy="210" r="4.5" fill="%s"/>'
          '<circle cx="42" cy="210" r="4.5" fill="none" stroke="%s"><animate attributeName="r" values="4.5;12" dur="2.4s" repeatCount="indefinite"/>'
          '<animate attributeName="stroke-opacity" values=".7;0" dur="2.4s" repeatCount="indefinite"/></circle>' % (MINT, MINT)
        + text(60, 215, 'Open to internships and entry-level roles. India or remote.', 15, '#c9d1d9', SANS)
        + fade(3.4) + '</g>'
        # a thin light that sweeps along the bottom edge now and then
        + '<defs><linearGradient id="sw"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".7"/>'
          '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
          '<rect x="-240" y="%d" width="240" height="1.5" fill="url(#sw)"><animate attributeName="x" values="-240;%d;%d" keyTimes="0;.37;1" begin="4s" dur="7s" repeatCount="indefinite"/></rect>'
          % (H - 2, W, W))
    return frame(W, H, 'sriram. Backend-focused full-stack engineer in India. Open to internships and entry-level roles.', body)


# ----------------------------------------------------------------------------- career as a git graph
def career(today):
    W, H = 830, 316
    X0, PX = 64, 27.4

    def mi(y, m, d=1):
        return (y - 2024) * 12 + (m - 10) + (d - 1) / 30

    def X(v):
        return X0 + v * PX

    LY = {'main': 84, 'px': 140, 'zn': 196, 'ac': 252}
    GREY = '#cbd5e1'
    now = mi(today.year, today.month, today.day)

    def branch(xs, xe, y, color, begin, merge=True):
        d = 'M%.1f %d C%.1f %d %.1f %d %.1f %d H%.1f' % (xs, LY['main'], xs + 16, LY['main'], xs, y, xs + 20, y, xe - (20 if merge else 0))
        if merge:
            d += ' C%.1f %d %.1f %d %.1f %d' % (xe, y, xe - 16, LY['main'], xe, LY['main'])
        return draw(d, color, begin, 1.1)

    s = []
    s.append(text(36, 38, '$', 14, MINT) + text(52, 38, 'git log --graph --all', 14, MUT))
    # year gridlines
    for yr, v in (('2025', mi(2025, 1)), ('2026', mi(2026, 1))):
        s.append('<line x1="%.1f" y1="60" x2="%.1f" y2="286" stroke="#fff" stroke-opacity=".07" stroke-dasharray="3 5"/>' % (X(v), X(v)))
        s.append(text('%.1f' % (X(v) + 6), 302, yr, 11, DIM))
    # main
    s.append(draw('M%.1f %d H%.1f' % (X0, LY['main'], X(26.4)), GREY, 0, 1.6, 2.5, ' stroke-opacity=".55"'))
    s.append(text(X0, LY['main'] - 16, 'main  B.Tech, Computer Science and IT, SRKR (2023-2027)', 12, MUT, begin=0.4))
    # project tags on main
    for label, v in (('LeaveFlow', mi(2025, 12, 9)), ('FinSight', mi(2026, 10, 24))):
        s.append('<circle cx="%.1f" cy="%d" r="4" fill="%s" stroke="%s" stroke-width="1.5" opacity="0">%s</circle>' % (X(v), LY['main'], BG, GREY, fade(1.6, 0.3)))
        s.append(text('%.1f' % X(v), LY['main'] + 22, label, 11, GREY, anchor='middle', begin=1.7))
    # PixelTests
    xs, xe = X(mi(2024, 12)), X(mi(2025, 5, 31))
    s.append(branch(xs, xe, LY['px'], BLUE, 0.7))
    s.append(dot(xs + 20, LY['px'], BLUE, 1.5) + dot(xe - 20, LY['px'], BLUE, 1.7))
    s.append('<line x1="%.1f" y1="%d" x2="390" y2="%d" stroke="%s" stroke-opacity=".3" stroke-dasharray="2 5" opacity="0">%s</line>' % (xe + 6, LY['px'], LY['px'], BLUE, fade(1.8, 0.4)))
    s.append(text(398, LY['px'] - 2, 'PixelTests', 12, BLUE, begin=1.8) + text(398, LY['px'] + 15, 'feat: whatsapp support bot', 11, MUT, begin=1.9) + text(398, LY['px'] + 30, 'tickets down 80%', 11, MUT, begin=2.0))
    # Zennith: solid, dashed pause, solid
    xs = X(mi(2025, 9))
    p0, p1, xn = X(mi(2026, 6)), X(mi(2026, 8)), X(now)
    d1 = 'M%.1f %d C%.1f %d %.1f %d %.1f %d H%.1f' % (xs, LY['main'], xs + 16, LY['main'], xs, LY['zn'], xs + 20, LY['zn'], p0)
    s.append(draw(d1, MINT, 1.3, 1.3))
    s.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2.5" stroke-dasharray="3 6" stroke-linecap="round" opacity="0">%s</line>'
             % (p0, LY['zn'], p1, LY['zn'], MINT, fade(3.0, 0.4)))
    s.append(text(800, LY['ac'] + 24, 'Zennith paused for Accenture, Jun-Jul 2026', 11, DIM, anchor='end', begin=3.6))
    s.append(draw('M%.1f %d H%.1f' % (p1, LY['zn'], xn), MINT, 3.4, 1.0))
    s.append(dot(xs + 20, LY['zn'], MINT, 2.0))
    s.append(text('%.1f' % (xs - 14), LY['zn'] + 4, 'Zennith AI  feat: document extraction pipeline', 12, MINT, anchor='end', begin=2.1))
    # HEAD
    s.append('<circle cx="%.1f" cy="%d" r="5.5" fill="%s" stroke="%s" stroke-width="2.5" opacity="0">%s</circle>' % (xn, LY['zn'], MINT, BG, fade(4.3, 0.3)))
    s.append('<circle cx="%.1f" cy="%d" r="5.5" fill="none" stroke="%s" opacity="0">%s<animate attributeName="r" values="5.5;15" begin="4.4s" dur="2.4s" repeatCount="indefinite"/>'
             '<animate attributeName="stroke-opacity" values=".7;0" begin="4.4s" dur="2.4s" repeatCount="indefinite"/></circle>' % (xn, LY['zn'], MINT, fade(4.3, 0.1)))
    s.append(text('%.1f' % xn, LY['zn'] - 14, 'HEAD', 11, MINT, anchor='middle', begin=4.5))
    # Accenture
    xs, xe = X(mi(2026, 6)), X(mi(2026, 7, 31))
    s.append(branch(xs, xe, LY['ac'], VIOLET, 2.5))
    s.append(dot(xs + 20, LY['ac'], VIOLET, 3.3) + dot(xe - 20, LY['ac'], VIOLET, 3.4))
    s.append(text('%.1f' % (xs - 14), LY['ac'] + 4, 'Accenture  feat: agentic pharma compliance', 12, VIOLET, anchor='end', begin=3.5))
    return frame(W, H, 'Career as a git graph. Main is the B.Tech. PixelTests, Zennith AI and Accenture are branches; Zennith was paused for Accenture.', '\n'.join(s), BLUE)


# ----------------------------------------------------------------------------- project cards
def weekly(repo, weeks=26):
    """Commits per week for the last `weeks` weeks, or None when GitHub has not computed the statistic."""
    try:
        data = api('/repos/%s/%s/stats/commit_activity' % (USER, repo), retries=3)
    except Exception:
        return None
    if not data:
        return None
    return [w['total'] for w in data[-weeks:]]


def card(name, status, colour, desc, pills, foot, pulse, flow, spark=None):
    W, H = 266, 240
    size = 22 if len(name) <= 12 else 16
    s = ['<line x1="22" y1=".5" x2="244" y2=".5" stroke="#fff" stroke-opacity=".5"/>']
    if spark and max(spark) > 0:
        top = max(spark)
        for i, v in enumerate(spark):
            h = 2 + 20 * v / top
            last = i == len(spark) - 1
            s.append('<rect x="%.1f" y="%.1f" width="2.4" height="%.1f" rx="1" fill="%s" fill-opacity="%s"/>'
                     % (150 + i * 3.7, 44 - h, h, ACC if last else '#fff', 1 if last else .45))
        s.append(text(244, 58, 'weekly commits', 10.5, DIM, anchor='end'))
    s.append('<circle cx="27" cy="31" r="4" fill="%s"/>' % colour)
    if pulse:
        s.append('<circle cx="27" cy="31" r="4" fill="none" stroke="%s"><animate attributeName="r" values="4;11" dur="2.4s" repeatCount="indefinite"/>'
                 '<animate attributeName="stroke-opacity" values=".7;0" dur="2.4s" repeatCount="indefinite"/></circle>' % colour)
    s.append(text(40, 35, status, 12, colour))
    s.append(text(22, 74, name, size, TXT, SANS, 700, extra=' letter-spacing="-.3"'))
    for i, line in enumerate(textwrap.wrap(desc, 30)[:3]):
        s.append(text(22, 102 + i * 19, line, 13.5, MUT, SANS))
    s.append(text(22, 160, flow, 11, DIM))
    x = 22
    for p in pills:
        w = len(p) * 6.4 + 16
        s.append('<rect x="%d" y="%d" width="%.1f" height="22" rx="11" fill="none" stroke="#fff" stroke-opacity=".22"/>' % (x, H - 62, w))
        s.append(text('%.1f' % (x + w / 2), H - 47, p, 11, TXT, anchor='middle'))
        x += w + 7
    s.append(text(22, H - 18, foot, 12, DIM))
    s.append(text(W - 22, H - 18, 'open', 12, colour, anchor='end'))
    return frame(W, H, '%s. %s' % (name, desc), '\n'.join(s))


CARDS = [
    ('card-leaveflow.svg', 'LeaveFlow', 'deployed', ACC, 'Leave requests over WhatsApp, approvals on a web dashboard.', ['FastAPI', 'PostgreSQL', 'Next.js'], '65 backend tests', True,
     'https://github.com/sriram36/LeaveFlow', 'whatsapp > fastapi > postgres'),
    ('card-finsight.svg', 'FinSight', 'deployed', ACC, 'Money advice where the model never does the arithmetic. A verifier checks every number.', ['FastAPI', 'Next.js', 'Postgres'], '60 tests', True,
     'https://github.com/sriram36/FinSight', 'python math > llm advice > verifier'),
    ('card-pharma.svg', 'pharma-mlr-compliance', 'code only', W3, 'A grader that is boring on purpose: 16 rules, a cache and a safe LLM fallback.', ['LangGraph', 'Azure OpenAI'], '16 rules', False,
     'https://github.com/sriram36/pharma-mlr-compliance', 'dictionary > disk cache > llm'),
]


# ----------------------------------------------------------------------------- heartbeat (live data)
def pushes(days=60):
    events = []
    for page in (1, 2, 3):
        batch = api('/users/%s/events/public?per_page=100&page=%d' % (USER, page))
        events += batch
        if len(batch) < 100:
            break
    cutoff = datetime.date.today() - datetime.timedelta(days=days - 1)
    per_day, n_push = {}, 0
    for e in events:
        if e.get('type') != 'PushEvent':
            continue
        d = datetime.date.fromisoformat(e['created_at'][:10])
        if d < cutoff:
            continue
        per_day[d] = per_day.get(d, 0) + ((e.get('payload') or {}).get('size') or 1)
        n_push += 1
    return per_day, n_push


def heartbeat(per_day, n_push, days=60):
    peak = max(per_day.items(), key=lambda kv: kv[1]) if per_day else None
    W, H = 410, 236
    today = datetime.date.today()
    x0, x1, base = 26, 384, 156
    dx = (x1 - x0) / (days - 1)
    pts = ['M%d %d' % (x0, base)]
    for i in range(days):
        d = today - datetime.timedelta(days=days - 1 - i)
        c = per_day.get(d, 0)
        x = x0 + i * dx
        if c:
            h = min(84, 18 + c * 5)
            pts.append('L%.1f %d L%.1f %d L%.1f %d L%.1f %d L%.1f %d' % (x - 3, base, x - 1.5, base + 6, x, base - h, x + 1.5, base + 10, x + 3, base))
    pts.append('L%d %d' % (x1, base))
    callout = ''
    if peak:
        pi = (peak[0] - (today - datetime.timedelta(days=days - 1))).days
        px, ph = x0 + pi * dx, min(84, 18 + peak[1] * 5)
        left = px < 200
        callout = text('%.1f' % (px + (10 if left else -10)), base - ph + 4,
                       'busiest: %d commits, %s' % (peak[1], peak[0].strftime('%b %d').replace(' 0', ' ')),
                       11, MUT, anchor='start' if left else 'end', begin=4.2)
    path = ' '.join(pts)
    commits = sum(per_day.values())
    s = [text(30, 38, '$', 14, MINT) + text(46, 38, 'git log --since="60 days ago"', 14, MUT)]
    for y in (72, 100, 128, 156, 184):
        s.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#fff" stroke-opacity=".05"/>' % (x0, y, x1, y))
    s.append('<path d="%s" fill="none" stroke="%s" stroke-width="7" stroke-opacity=".10" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
             '<animate attributeName="stroke-dashoffset" from="1" to="0" begin="0.3s" dur="3.5s" fill="freeze"/></path>' % (path, W1))
    s.append('<path id="hb" d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
             '<animate attributeName="stroke-dashoffset" from="1" to="0" begin="0.3s" dur="3.5s" fill="freeze"/></path>' % (path, W1))
    s.append(callout)
    s.append('<circle r="3.5" fill="%s" opacity="0"><animateMotion path="%s" begin="4s" dur="7s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.05;.95;1" begin="4s" dur="7s" repeatCount="indefinite"/></circle>' % (ACC, path))
    s.append(text(x0, 218, '60 days ago', 11, DIM) + text(x1, 218, 'today', 11, DIM, anchor='end'))
    s.append(text('%d' % (W / 2), 218, '%d commits, %d pushes' % (commits, n_push), 12, MUT, anchor='middle'))
    return frame(W, H, 'My public GitHub pushes over the last 60 days as a heartbeat line: %d commits in %d pushes.' % (commits, n_push), '\n'.join(s))


# ----------------------------------------------------------------------------- languages (live data)
def languages():
    """Bytes of code per language across my public, non-fork repos."""
    total = {}
    for g in api('/users/%s/repos?per_page=100' % USER):
        if g['fork']:
            continue
        try:
            counts = api('/repos/%s/%s/languages' % (USER, g['name'])) or {}
        except Exception as e:   # one repo failing should not lose the whole tile
            print('skipped languages for %s: %s' % (g['name'], e), file=sys.stderr)
            continue
        for lang, n in counts.items():
            total[lang] = total.get(lang, 0) + n
    if not total:
        raise SystemExit('GitHub returned no language data; leaving the profile as it was')
    return sorted(total.items(), key=lambda kv: -kv[1])


def languages_tile(rows):
    W, H = 410, 236
    whole = sum(n for _, n in rows)
    top = rows[:6]
    rest = whole - sum(n for _, n in top)
    if rest > 0:
        top.append(('other', rest))
    big = top[0][1]
    s = [text(30, 38, '$', 14, MINT) + text(46, 38, 'cat languages.txt', 14, MUT)]
    alt = []
    for i, (name, n) in enumerate(top):
        y = 76 + i * 20
        pct = 100 * n / whole
        w = max(2.0, 170 * n / big)
        b = 0.3 + i * 0.15
        s.append(text(30, y + 4, name, 12, TXT if name != 'other' else DIM, begin=b))
        s.append('<rect x="136" y="%d" width="0" height="8" rx="4" fill="%s" fill-opacity="%s">'
                 '<animate attributeName="width" from="0" to="%.1f" begin="%ss" dur="0.9s" fill="freeze"/></rect>'
                 % (y - 4, ACC if i == 0 else '#fff', 1 if i == 0 else .55, w, b))
        s.append(text(382, y + 4, '%.0f%%' % pct if pct >= 1 else '<1%', 12, MUT, anchor='end', begin=b + 0.3))
        alt.append('%s %.0f%%' % (name, pct))
    s.append(text(30, 218, 'by bytes of code, public repos', 11, DIM))
    return frame(W, H, 'Languages by bytes of code in my public repos: ' + ', '.join(alt) + '.', '\n'.join(s)), alt


# ----------------------------------------------------------------------------- stack panel
STACK = [
    ('languages', ['Python', 'TypeScript', 'JavaScript', 'Java', 'SQL']),
    ('backend', ['FastAPI', 'Django', 'Node.js', 'PostgreSQL', 'WebSockets', 'JWT', 'Pytest']),
    ('frontend', ['Next.js', 'React', 'Tailwind CSS']),
    ('ai', ['LangGraph', 'Azure OpenAI', 'RAG', 'LLM evaluation']),
    ('tools', ['Docker', 'Git', 'Playwright', 'n8n']),
]
STACK_ALT = 'Stack. ' + ' '.join('%s: %s.' % (c.capitalize(), ', '.join(i)) for c, i in STACK)


def stack():
    W, H = 830, 236
    s = [text(36, 38, '$', 14, ACC) + text(52, 38, 'ls ~/stack', 14, MUT)]
    for r, (cat, items) in enumerate(STACK):
        y = 82 + r * 31
        b = 0.3 + r * 0.25
        s.append(text(36, y + 4, cat, 12.5, DIM, begin=b))
        x = 150
        g = ['<g opacity="0">']
        for it in items:
            w = len(it) * 6.8 + 18
            g.append('<rect x="%.1f" y="%d" width="%.1f" height="24" rx="12" fill="none" stroke="#fff" stroke-opacity=".22"/>' % (x, y - 12, w))
            g.append(text('%.1f' % (x + w / 2), y + 4, it, 12, TXT, anchor='middle'))
            x += w + 8
        g.append(fade(b + 0.1, 0.5) + '</g>')
        s.append(''.join(g))
    return frame(W, H, STACK_ALT, '\n'.join(s))


# ----------------------------------------------------------------------------- hire card
def hire():
    W, H = 830, 150
    s = [
        text(36, 44, '$', 14, ACC) + text(52, 44, 'curl -X POST github.com/sriram36/hire', 14, MUT),
        text(36, 76, '{ "wanted": "internship, entry-level backend or full-stack", "where": "India or remote" }', 13, '#c9d1d9', begin=0.6),
        text(36, 108, 'HTTP/1.1 202 Accepted', 14, ACC, begin=1.4),
        text(36, 132, 'kollisriram6@gmail.com', 14, TXT, begin=1.9),
    ]
    return frame(W, H, 'POST /hire returns 202 Accepted. Email kollisriram6@gmail.com.', '\n'.join(s))


# ----------------------------------------------------------------------------- link buttons
LINKS = [
    ('pill-portfolio.svg', 'Portfolio', 'https://portfolio.kollisriram6.workers.dev', True),
    ('pill-decisions.svg', 'Decisions I would defend', 'https://portfolio.kollisriram6.workers.dev/#decisions', False),
    ('pill-linkedin.svg', 'LinkedIn', 'https://www.linkedin.com/in/sriram-kolli-979723219', False),
    ('pill-email.svg', 'Email', 'mailto:kollisriram6@gmail.com', False),
]


def pill(label, primary):
    """A real button: natural size, so it stays tappable and readable on a phone."""
    w, h = int(len(label) * 8.4 + 52), 44
    fg, bg = ('#000', '#fafafa') if primary else (TXT, '#000')
    arrow = ('<path d="M%d 17 L%d 22 L%d 27" fill="none" stroke="%s" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
             % (w - 26, w - 20, w - 26, fg))
    body = ('<rect x=".75" y=".75" width="%.2f" height="%.2f" rx="21.25" fill="%s" stroke="#fff" stroke-opacity="%s" stroke-width="1.5"/>' % (w - 1.5, h - 1.5, bg, .9 if primary else .3)
            + text(22, 27.5, label, 14.5, fg, SANS, 600))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-labelledby="t"><title id="t">%s</title>%s%s</svg>\n'
            % (w, h, w, h, escape(label), body, arrow))


# ----------------------------------------------------------------------------- README
README ="""<img src="banner.svg" alt="sriram. Backend-focused full-stack engineer in India. Open to internships and entry-level roles." width="100%">

<p align="center">
{pills}
</p>

<img src="career.svg" alt="Career as a git graph. Main is the B.Tech at SRKR, 2023 to 2027. PixelTests (Dec 2024 to May 2025), Zennith AI (Sep 2025 to now, paused Jun to Jul 2026) and Accenture (Jun to Jul 2026) are branches." width="100%">

<p align="center">
{cards}
</p>

<p align="center">
<img src="languages.svg" width="49%" alt="Languages by bytes of code in my public repos: {langs}.">
<img src="heartbeat.svg" width="49%" alt="My public pushes over the last 60 days as a heartbeat line: {commits} commits in {pushes} pushes.">
</p>

<img src="stack.svg" alt="{stack_alt}" width="100%">

<img src="hire.svg" alt="POST /hire returns 202 Accepted. Email kollisriram6@gmail.com." width="100%">

<details>
<summary>Read this page as plain text</summary>

<br>

**Sriram Kolli.** Backend-focused full-stack engineer in India. Final-year B.Tech in Computer Science and Information Technology (SRKR Engineering College, 2023 to 2027). I build FastAPI and PostgreSQL services, agentic AI pipelines and workflow automation. Open to software engineering internships and entry-level backend or full-stack roles, in India or remote.

**Experience**

- Zennith AI, Full Stack Developer Intern, Sep 2025 to now (paused Jun to Jul 2026 for Accenture): a document-extraction pipeline on FastAPI and Next.js components for upload and results.
- Accenture, Associate Software Engineer Intern, Jun to Jul 2026: CI/CD for FastAPI and PostgreSQL services, then an agentic pharma compliance review system.
- PixelTests, Software Development Intern, Dec 2024 to May 2025: a WhatsApp support pipeline that cut manual tickets by 80%. Employer numbers are my word.

**Projects**

- [LeaveFlow](https://github.com/sriram36/LeaveFlow) ([live](https://leave-flow-cyan.vercel.app)): leave requests over WhatsApp, approvals on a web dashboard. FastAPI, PostgreSQL, WebSockets, Next.js. 65 backend tests.
- [FinSight](https://github.com/sriram36/FinSight) ([live](https://finsight-wine-tau.vercel.app)): money advice where the model never does the arithmetic. A verifier checks every number against cited transactions. 60 tests.
- [pharma-mlr-compliance](https://github.com/sriram36/pharma-mlr-compliance): a rule-based grader, 16 rules, one optionally LLM-assisted. Lookups go dictionary, then disk cache, then LLM.

**Stack.** {stack_text}

**Latest pushes.** {latest}

**Contact.** kollisriram6@gmail.com | [LinkedIn](https://www.linkedin.com/in/sriram-kolli-979723219) | [Portfolio](https://portfolio.kollisriram6.workers.dev)

</details>

<p align="center"><sub>Generated by <a href="build.py">build.py</a> and rebuilt every Monday by a GitHub Action.</sub></p>
"""


def write(name, content):
    (HERE / name).write_text(content, encoding='utf-8', newline='\n')


def main():
    today = datetime.date.today()
    per_day, n_push = pushes()
    repos = [g for g in api('/users/%s/repos?sort=pushed&per_page=30' % USER) if not g['fork'] and g['name'] != USER][:5]
    if not repos:
        raise SystemExit('GitHub returned no repos; leaving the profile as it was')
    write('banner.svg', banner(today.strftime('%Y.%m')))
    write('career.svg', career(today))
    for fn, name, status, colour, desc, pills, foot, pulse, link, flow in CARDS:
        write(fn, card(name, status, colour, desc, pills, foot, pulse, flow, weekly(link.rsplit('/', 1)[1])))
    write('heartbeat.svg', heartbeat(per_day, n_push))
    lang_svg, lang_alt = languages_tile(languages())
    write('languages.svg', lang_svg)
    write('stack.svg', stack())
    write('hire.svg', hire())
    for fn, label, _, primary in LINKS:
        write(fn, pill(label, primary))
    pills = '\n'.join('<a href="%s"><img src="%s" alt="%s"></a>' % (href, fn, label) for fn, label, href, _ in LINKS)
    stack_text = ' '.join('%s: %s.' % (c.capitalize(), ', '.join(i)) for c, i in STACK)
    cards ='\n'.join('<a href="%s"><img src="%s" width="32%%" alt="%s: %s"></a>' % (c[8], c[0], c[1], c[4]) for c in CARDS)
    latest = ' | '.join('[%s](https://github.com/%s/%s)' % (g['name'], USER, g['name']) for g in repos)
    write('README.md', README.format(stack_alt=STACK_ALT, stack_text=stack_text, pills=pills, langs=', '.join(lang_alt), cards=cards, commits=sum(per_day.values()), pushes=n_push, latest=latest))
    print('built: %d commits in %d pushes, %d recent repos' % (sum(per_day.values()), n_push, len(repos)))


if __name__ == '__main__':
    sys.exit(main())
