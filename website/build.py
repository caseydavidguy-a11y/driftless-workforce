#!/usr/bin/env python3
"""Builds the Driftless Workforce Group website.

  python3 build.py            -> out/      full site, ready for any static host (GitHub Pages, Netlify, a domain)
                                 preview/  the same site packaged for a claude.ai preview artifact
                                 apps-script/Code.gs + Inbox.html  the forms backend and private inbox

Edit SITE below when the phone, email, web address or forms endpoint are known, then rebuild.
"""
import html, json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import FAVICON, I

ROOT = os.path.dirname(os.path.abspath(__file__))

SITE = {
    'name': 'Driftless Workforce Group',
    'city': 'La Crosse, Wisconsin',
    'phone': '608-397-1754',
    'email': 'info@driftlessworkforcegroup.com',
    'base_url': 'https://driftlessworkforcegroup.com/',
    'endpoint': '',       # Google Apps Script "Forms" web app address; blank = forms run in preview mode
    'inbox_url': 'https://app.netlify.com/projects/driftless-workforce-group/forms',  # the back door
    'year': '2026',
}

E = html.escape
NAV = [('employers.html', 'Employers'), ('retainer.html', 'Retainer'), ('job-seekers.html', 'Job seekers'),
       ('report.html', 'Hiring report'), ('about.html', 'About'), ('contact.html', 'Contact')]

# ---------------------------------------------------------------- forms (one definition feeds the page AND the backend)
ROLES = ['Maintenance technician', 'CNC machinist or machine operator', 'Production or assembly', 'Welder or fabricator',
         'Warehouse or forklift', 'Production supervisor or lead', 'Janitorial or sanitation', 'Something else']
SHIFTS = ['1st shift', '2nd shift', '3rd shift', 'Weekends', 'Rotating or 12-hour shifts']

FORMS = {
  'employer': dict(tab='Employer requests', id='request-form', submit='Send request',
    intro='Tell us about the role. Casey will call you to talk it through. All fields are required unless marked optional.',
    done_title='Request received', done_text='Thank you. Casey will reach out to set up a short call about the role.',
    fields=[
      ('text', 'company', 'Company', dict(auto='organization', half=True, msg='Enter your company name.')),
      ('text', 'name', 'Your name', dict(auto='name', half=True, msg='Enter your name.')),
      ('email', 'email', 'Work email', dict(auto='email', half=True, msg='Enter your work email.')),
      ('tel', 'phone', 'Phone', dict(auto='tel', half=True, msg='Enter a phone number.')),
      ('text', 'title', 'Your job title', dict(auto='organization-title', half=True, optional=True)),
      ('text', 'location', 'Where is the job?', dict(half=True, hint='Town or plant location', msg='Enter where the job is.')),
      ('checks', 'roles', 'What do you need to hire?', dict(options=ROLES, hint='Choose all that apply.', msg='Choose at least one kind of role.')),
      ('number', 'openings', 'How many openings?', dict(half=True, min=1, max=500, msg='Enter how many people you need.')),
      ('select', 'timing', 'When do you need them?', dict(half=True, options=['As soon as possible', 'Within 30 days', 'Within 90 days', 'Planning ahead'], msg='Choose when you need them.')),
      ('checks', 'shifts', 'Shifts', dict(options=SHIFTS, optional=True)),
      ('text', 'pay', 'Pay range', dict(optional=True, half=True, hint='For example, $24 to $30 an hour')),
      ('select', 'service', 'What kind of help?', dict(optional=True, half=True, options=["Not sure yet, let's talk", 'A single search', 'A priority search for a hard-to-fill role', 'Ongoing recruiting (monthly retainer)'])),
      ('textarea', 'notes', 'Anything else we should know?', dict(optional=True, hint='Must-have skills or certifications, what has not worked so far, anything that makes the job stand out.')),
    ]),
  'candidate': dict(tab='Job seekers', id='apply-form', submit='Send my information',
    intro='It takes about three minutes. All fields are required unless marked optional.',
    done_title='Got it, thank you', done_text='Casey will look over your information and reach out when there is a job that fits. We never send your information to an employer without asking you first.',
    fields=[
      ('text', 'name', 'Full name', dict(auto='name', half=True, msg='Enter your full name.')),
      ('tel', 'phone', 'Phone', dict(auto='tel', half=True, msg='Enter your phone number.')),
      ('email', 'email', 'Email', dict(auto='email', half=True, msg='Enter your email address.')),
      ('text', 'zip', 'ZIP code', dict(auto='postal-code', half=True, inputmode='numeric', pattern='[0-9]{5}', pattern_msg='Enter a 5-digit ZIP code.', msg='Enter your ZIP code.')),
      ('checks', 'work', 'What kind of work do you want?', dict(options=ROLES, hint='Choose all that apply.', msg='Choose at least one kind of work.')),
      ('select', 'experience', 'Experience in this kind of work', dict(half=True, options=['New to it and ready to learn', 'Less than 1 year', '1 to 3 years', '3 to 10 years', 'More than 10 years'], msg='Choose your experience.')),
      ('select', 'start', 'When can you start?', dict(half=True, options=['Right away', 'Within 2 weeks', 'Within a month', 'Just looking for now'], msg='Choose when you can start.')),
      ('checks', 'shifts', 'Shifts you can work', dict(options=SHIFTS, msg='Choose at least one shift.')),
      ('select', 'license', "Driver's license", dict(half=True, options=["Valid driver's license", 'CDL Class A', 'CDL Class B', 'No license right now'], msg="Choose your driver's license status.")),
      ('text', 'pay', 'Pay you are looking for', dict(optional=True, half=True, hint='For example, $22 an hour')),
      ('text', 'certs', 'Certifications or training', dict(optional=True, hint='Forklift, welding, OSHA 10, electrical, CNC, food safety and so on')),
      ('file', 'resume', 'Resume', dict(optional=True, hint='PDF or Word file, up to 5 MB. No resume? You can still send this form.')),
      ('textarea', 'notes', 'Anything else?', dict(optional=True)),
      ('consent', 'consent', 'Driftless Workforce Group may contact me about jobs by phone, text or email. I can ask them to stop at any time.', dict(msg='Tick this box so we can contact you about jobs.')),
    ]),
  'question': dict(tab='Questions', id='contact-form', submit='Send message',
    intro='Ask anything. Every message goes straight to Casey Guy, the founder. All fields are required unless marked optional.',
    done_title='Message sent', done_text='Thank you. Casey will get back to you soon.',
    fields=[
      ('text', 'name', 'Your name', dict(auto='name', half=True, msg='Enter your name.')),
      ('email', 'email', 'Email', dict(auto='email', half=True, msg='Enter your email address.')),
      ('tel', 'phone', 'Phone', dict(auto='tel', half=True, optional=True)),
      ('select', 'who', 'I am', dict(half=True, options=['An employer', 'Looking for work', 'Something else'], msg='Choose one.')),
      ('textarea', 'message', 'Your question', dict(msg='Enter your question.')),
    ]),
  'report': dict(tab='Report sign-ups', id='report-form', submit='Send me the report',
    intro='Free, once a quarter, by email. All fields are required unless marked optional.',
    done_title="You're on the list", done_text='Thank you. Casey will email you the full October report, and each new edition when it comes out.',
    fields=[
      ('text', 'name', 'Your name', dict(auto='name', half=True, msg='Enter your name.')),
      ('email', 'email', 'Work email', dict(auto='email', half=True, msg='Enter your work email.')),
      ('text', 'company', 'Company', dict(auto='organization', half=True, msg='Enter your company name.')),
      ('text', 'title', 'Your job title', dict(auto='organization-title', half=True, optional=True)),
      ('consent', 'consent', 'Email me the Coulee Region Industrial Hiring Report each quarter. I can unsubscribe at any time.', dict(msg='Tick this box so we can email you the report.')),
    ]),
}


def field_html(fid_prefix, f):
    kind, name, label, o = f
    fid = f'{fid_prefix}-{name}'
    half = ' half' if o.get('half') else ''
    opt_attr = ' data-optional' if o.get('optional') else ''
    opt_txt = ' <span class="opt">(optional)</span>' if o.get('optional') else ''
    msg = f' data-msg="{E(o["msg"])}"' if o.get('msg') else ''
    pmsg = f' data-pattern-msg="{E(o["pattern_msg"])}"' if o.get('pattern_msg') else ''
    hint_txt = o.get('hint')
    hint = f'<p class="hint" id="{fid}-hint">{E(hint_txt)}</p>' if hint_txt and hint_txt.strip() else ''
    if hint_txt == ' ':
        hint = '<p class="hint" aria-hidden="true">&nbsp;</p>'
    desc = f' aria-describedby="{fid}-hint"' if hint_txt and hint_txt.strip() else ''
    req = '' if o.get('optional') else ' aria-required="true"'
    common = f'class="field{half}" id="{fid}-wrap" data-label="{E(label)}"{opt_attr}{msg}{pmsg}'

    if kind in ('text', 'email', 'tel', 'number'):
        attrs = f' autocomplete="{o["auto"]}"' if o.get('auto') else ' autocomplete="off"'
        if o.get('inputmode'): attrs += f' inputmode="{o["inputmode"]}"'
        if kind == 'tel': attrs += ' inputmode="tel"'
        if o.get('pattern'): attrs += f' pattern="{o["pattern"]}"'
        if kind == 'number': attrs += f' min="{o.get("min", "")}" max="{o.get("max", "")}" inputmode="numeric"'
        return (f'<div {common} data-kind="input"><label for="{fid}">{E(label)}{opt_txt}</label>{hint}'
                f'<input class="input" id="{fid}" name="{name}" type="{kind}"{attrs}{desc}{req}></div>')
    if kind == 'select':
        opts = '<option value="">Choose one</option>' + ''.join(f'<option>{E(x)}</option>' for x in o['options'])
        return (f'<div {common} data-kind="input"><label for="{fid}">{E(label)}{opt_txt}</label>{hint}'
                f'<select class="select" id="{fid}" name="{name}"{desc}{req}>{opts}</select></div>')
    if kind == 'textarea':
        return (f'<div {common} data-kind="input"><label for="{fid}">{E(label)}{opt_txt}</label>{hint}'
                f'<textarea class="textarea" id="{fid}" name="{name}" rows="4"{desc}{req}></textarea></div>')
    if kind == 'checks':
        boxes = ''.join(f'<label class="choice"><input type="checkbox" id="{fid}-{i}" name="{name}" value="{E(x)}"><span>{E(x)}</span></label>'
                        for i, x in enumerate(o['options']))
        return (f'<fieldset {common} data-kind="checks"{desc}><legend>{E(label)}{opt_txt}</legend>{hint}'
                f'<div class="choices">{boxes}</div></fieldset>')
    if kind == 'file':
        return (f'<div {common} data-kind="file"><label for="{fid}">{E(label)}{opt_txt}</label>{hint}'
                f'<div class="file-drop"><input id="{fid}" name="{name}" type="file" accept=".pdf,.doc,.docx,.rtf,.txt,.odt"{desc}></div></div>')
    if kind == 'consent':
        return (f'<div {common} data-kind="consent"><label class="consent"><input type="checkbox" id="{fid}" name="{name}" value="Yes" data-single="true"{req}>'
                f'<span>{E(label)}</span></label></div>')
    raise ValueError(kind)


def form_html(key):
    F = FORMS[key]
    fid = F['id']
    fallback = f' data-fallback="Or email {E(SITE["email"])}."' if SITE['email'] else ''
    rows = ''.join(field_html(fid, f) for f in F['fields'])
    enc = ' enctype="multipart/form-data"' if any(f[0] == 'file' for f in F['fields']) else ''
    return (f'<form id="{fid}" name="{key}" method="POST" data-netlify="true" netlify-honeypot="website_url"{enc} class="form-card" data-form="{key}" data-done="{fid}-done"{fallback} aria-label="{E(F["submit"])}">'
            f'<input type="hidden" name="form-name" value="{key}">'
            f'<p class="form-intro">{E(F["intro"])}</p>'
            f'<div class="fields">{rows}</div>'
            f'<div class="hp" aria-hidden="true"><label for="{fid}-website">Leave this field empty</label>'
            f'<input id="{fid}-website" name="website_url" type="text" tabindex="-1" autocomplete="off"></div>'
            f'<div class="form-actions"><button class="btn" type="submit">{E(F["submit"])}</button>'
            f'<span class="small">See how we handle your information in our <a href="privacy.html">privacy notice</a>.</span></div>'
            f'</form>'
            f'<div id="{fid}-done" class="form-card form-done" hidden><div class="done-icon">{I["bigcheck"]}</div>'
            f'<h3>{E(F["done_title"])}</h3><p>{E(F["done_text"])}</p>'
            f'<p class="notice preview" hidden>Preview: this form is not connected yet, so nothing was sent.</p>'
            f'<button type="button" class="btn secondary small" data-reset="{fid}">Send another</button></div>')

# ---------------------------------------------------------------- report data (October 2026 edition)
POSTINGS = [('maintenance', 145), ('production', 141), ('warehouse', 86), ('forklift', 49), ('CDL', 39), ('machinist', 26),
            ('CNC', 25), ('mechanic', 11), ('welder', 7), ('custodian', 7), ('electrician', 4), ('assembler', 2)]
WAGES = [('Electricians', 37.87, 22.02, 52.34, False), ('Production supervisors', 34.19, 23.91, 46.73, False),
         ('Industrial machinery mechanics', 31.03, 24.28, 46.59, True), ('Machinists', 30.27, 17.83, 38.67, True),
         ('Heavy truck drivers', 28.99, 22.60, 39.17, False), ('Welders and brazers', 28.27, 23.45, 37.65, True),
         ('CNC tool operators', 26.15, 20.07, 32.71, False), ('Maintenance and repair, general', 25.56, 17.59, 34.18, False),
         ('Assemblers and fabricators', 22.18, 17.92, 28.53, False), ('Packaging machine operators', 22.06, 17.78, 23.41, False),
         ('Forklift operators', 21.45, 18.91, 27.09, False), ('Hand laborers and material movers', 20.58, 14.89, 26.75, False),
         ('Janitors and cleaners', 17.37, 14.36, 22.39, False), ('Stockers and order fillers', 16.42, 13.98, 22.51, False)]
OPEN_ROLES = [('Maintenance technician', '', 'March 30, 2026', 196),
              ('CNC lathe machinist / machine operator', '3rd shift, entry level or experienced', 'April 15, 2026', 180),
              ('CNC lathe machinist / machine operator', '2nd shift, entry level or experienced', 'April 15, 2026', 180),
              ('Welder', '', 'April 23, 2026', 172), ('Gas welder / brazer', '', 'April 23, 2026', 172),
              ('Material handler', '', 'April 23, 2026', 172)]


def chart_postings():
    y0, rh, x0, w = 16, 28, 130, 700
    peak = max(v for _, v in POSTINGS)
    lead = sorted(POSTINGS, key=lambda r: -r[1])[:2]
    H = y0 + len(POSTINGS) * rh + 8
    out = [f'<svg viewBox="0 0 900 {H}" role="img" aria-labelledby="c1t"><title id="c1t">Bar chart: state job bank postings that mention each word. '
           + '; '.join(f'{k} {v}' for k, v in POSTINGS) + '.</title>']
    for i, (k, v) in enumerate(POSTINGS):
        y = y0 + i * rh
        bw = v / peak * w
        fill = 'var(--river)' if (k, v) in lead else 'var(--bluff-2)'
        out.append(f'<text x="{x0-10}" y="{y+18}" text-anchor="end" font-size="13" fill="var(--ink)">{E(k)}</text>'
                   f'<rect x="{x0}" y="{y+5}" width="{bw:.1f}" height="18" rx="2" fill="{fill}"/>'
                   f'<text x="{x0+bw+8:.1f}" y="{y+18}" font-size="13" font-weight="600" fill="var(--ink)">{v}</text>')
    out.append(f'<path d="M{x0} {y0} V{y0+len(POSTINGS)*rh}" stroke="var(--ink-2)" stroke-width="1"/></svg>')
    return ''.join(out)


def chart_wages():
    y0, rh, x0, w, cap = 34, 30, 250, 300, 55
    sx = lambda v: x0 + v / cap * w
    H = y0 + len(WAGES) * rh + 8
    out = [f'<svg viewBox="0 0 760 {H}" role="img" aria-labelledby="c2t"><title id="c2t">Median hourly wage by role in the La Crosse-Onalaska metro, May 2025, with the 10th to 90th percentile range. '
           + '; '.join(f'{r} ${m:.2f} (${lo:.0f} to ${hi:.0f})' for r, m, lo, hi, _ in WAGES) + '.</title>',
           f'<text x="660" y="20" text-anchor="end" font-size="12" fill="var(--ink-2)">Median</text>',
           f'<text x="750" y="20" text-anchor="end" font-size="12" fill="var(--ink-2)">Low to high</text>']
    for i, (r, m, lo, hi, hot) in enumerate(WAGES):
        y = y0 + i * rh
        fill = 'var(--river)' if hot else 'var(--bluff-2)'
        out.append(f'<text x="{x0-10}" y="{y+19}" text-anchor="end" font-size="14" fill="var(--ink)">{E(r)}</text>'
                   f'<rect x="{x0}" y="{y+6}" width="{sx(m)-x0:.1f}" height="18" rx="2" fill="{fill}"/>'
                   f'<path d="M{sx(lo):.1f} {y+15} H{sx(hi):.1f} M{sx(lo):.1f} {y+10} V{y+20} M{sx(hi):.1f} {y+10} V{y+20}" stroke="var(--ink)" stroke-width="1.5" opacity=".7"/>'
                   f'<text x="660" y="{y+19}" text-anchor="end" font-size="14" font-weight="600" fill="var(--ink)">${m:.2f}</text>'
                   f'<text x="750" y="{y+19}" text-anchor="end" font-size="14" fill="var(--ink-2)">${lo:.0f}&#8211;${hi:.0f}</text>')
    out.append(f'<path d="M{x0} {y0} V{y0+len(WAGES)*rh}" stroke="var(--ink-2)" stroke-width="1"/></svg>')
    return ''.join(out)

# ---------------------------------------------------------------- shell
MENU_ICON = I['menu'].replace('<svg', '<svg width="20" height="20"', 1)


def header(current):
    links = ''.join(f'<a href="{href}"{" aria-current=" + chr(34) + "page" + chr(34) if href == current else ""}>{E(label)}</a>' for href, label in NAV)
    return (f'<a class="skip" href="#main">Skip to content</a>'
            f'<header class="site-header"><div class="wrap">'
            f'<a class="brand" href="./" aria-label="Driftless Workforce Group, home"><span class="brand-name"><b>Driftless</b><span>Workforce Group</span></span></a>'
            f'<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav">{MENU_ICON}Menu</button>'
            f'<nav id="site-nav" class="nav" aria-label="Main" data-open="true">{links}'
            f'<a class="btn small" href="employers.html#request">Request talent</a></nav>'
            f'</div></header>')


def footer(preview):
    contact = [f'<li>{E(SITE["city"])}</li>']
    if SITE['phone']: contact.append(f'<li><a href="tel:{"".join(c for c in SITE["phone"] if c.isdigit())}">{E(SITE["phone"])}</a></li>')
    if SITE['email']: contact.append(f'<li><a href="mailto:{E(SITE["email"])}">{E(SITE["email"])}</a></li>')
    contact.append('<li><a href="contact.html">Send us a message</a></li>')
    staff = SITE['inbox_url'] or ('inbox.html' if preview else '')
    staff_link = f' · <a href="{E(staff)}" rel="nofollow">Staff sign-in</a>' if staff else ''
    return (f'<footer class="site-footer"><div class="wrap"><div class="foot-grid">'
            f'<div><div class="foot-brand"><b>Driftless Workforce Group</b></div>'
            f'<p>Direct-hire recruiting for manufacturing, warehousing, maintenance and janitorial roles across the Coulee Region and the Driftless.</p></div>'
            f'<div><h2>Employers</h2><ul><li><a href="employers.html">How we work</a></li><li><a href="retainer.html">Recruiting retainer</a></li><li><a href="employers.html#request">Request talent</a></li>'
            f'<li><a href="report.html">Hiring report</a></li></ul></div>'
            f'<div><h2>Job seekers</h2><ul><li><a href="job-seekers.html">Find work</a></li><li><a href="job-seekers.html#apply">Send your information</a></li></ul></div>'
            f'<div><h2>Contact</h2><ul>{"".join(contact)}</ul></div>'
            f'</div><div class="foot-base"><span>&copy; {SITE["year"]} Driftless Workforce Group LLC. Free for job seekers; employers pay our fee. Equal opportunity in every search.</span>'
            f'<span><a href="privacy.html">Privacy</a>{staff_link}</span></div></div></footer>')


# The GitHub Pages copy forwards visitors to the real domain.
GH_REDIRECT = ('<script>if(/github\\.io$/.test(location.hostname)){location.replace("https://driftlessworkforcegroup.com/"'
               '+(location.pathname.split("/").pop()||"")+location.hash)}</script>')

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">')


def page(slug, title, desc, main, current, preview=False, bare=False, preview_title=None):
    body = f'{header(current)}<main id="main">{main}</main>{footer(preview)}<script src="assets/site.js" defer></script>'
    meta = (f'<meta name="description" content="{E(desc)}"><link rel="icon" href="{FAVICON}">'
            f'<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website">')
    if SITE['base_url']:
        meta += f'<link rel="canonical" href="{E(SITE["base_url"] + ("" if slug == "index.html" else slug))}">'
    if bare:  # artifact main page: the publisher adds doctype/html/head/body
        return f'<title>{E(preview_title or title)}</title><meta name="driftless-mode" content="preview">{FONTS}<link rel="stylesheet" href="assets/site.css">{body}'
    endpoint = '' if preview else SITE['endpoint']
    mode = '<meta name="driftless-mode" content="preview">' if preview else ''
    return (f'<!doctype html><html lang="en" data-endpoint="{E(endpoint)}" data-phone="{E(SITE["phone"])}"><head><meta charset="utf-8">{mode}'
            f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>{E(title)}</title>{meta}{GH_REDIRECT if not preview else ""}{FONTS}'
            f'<link rel="stylesheet" href="assets/site.css"></head><body>{body}</body></html>')

# ---------------------------------------------------------------- page bodies
def role_cards():
    cards = [
        ('factory', 'Manufacturing and production', 'CNC machinists, machine operators, assemblers, welders and fabricators, production leads and supervisors.'),
        ('boxes', 'Warehousing and logistics', 'Forklift operators, material handlers, shipping and receiving, inventory and warehouse leads.'),
        ('wrench', 'Maintenance and facilities', 'Industrial maintenance technicians, mechanics, facilities technicians and building maintenance staff.'),
        ('bucket', 'Janitorial and sanitation', 'Custodians, plant sanitation crews, facility cleaning staff and leads.'),
    ]
    return ''.join(f'<article class="card"><div class="icon">{I[ic]}</div><h3>{E(t)}</h3><p class="role-list">{E(d)}</p></article>' for ic, t, d in cards)


def steps_employer():
    s = [('Tell us about the role', 'A short call about the job, the shift, the pay and what has not worked so far.'),
         ('We search and screen', 'We look locally, check skills and references, and talk with every candidate before you do.'),
         ('You meet the best few', 'You interview a short list of people who fit, not a stack of resumes.'),
         ('Hire with confidence', 'Your new hire starts on your payroll, backed by our replacement guarantee.')]
    return '<ol class="steps">' + ''.join(f'<li><h3>{E(a)}</h3><p>{E(b)}</p></li>' for a, b in s) + '</ol>'


def home():
    roles = ['Maintenance technicians', 'CNC machinists', 'Welders and fabricators', 'Production and assembly', 'Forklift and warehouse',
             'Production supervisors', 'Facilities technicians', 'Janitorial and sanitation']
    chips = ''.join(f'<li>{E(r)}</li>' for r in roles)
    return f'''
<section class="hero split"><div class="wrap">
  <div class="hero-copy">
    <span class="eyebrow">Direct-hire recruiting &middot; La Crosse region</span>
    <h1>Hiring talent that stays. Right here in the Driftless.</h1>
    <p class="lede">We connect plants, warehouses and facilities from La Crosse to Sparta, Viroqua and across the Driftless with job-ready people from our own community. Employer-paid, and free for job seekers. Always.</p>
  </div>
  <div class="doors">
    <article class="door"><span class="eyebrow">Employers</span><h2>I need to hire</h2>
      <p>Maintenance, machining, production, warehouse and janitorial roles. Direct hire, on your payroll.</p>
      <div class="btn-row"><a class="btn" href="employers.html#request">Request talent</a><a class="btn secondary" href="retainer.html">See the retainer</a></div></article>
    <article class="door seek"><span class="eyebrow">Job seekers</span><h2>I'm looking for work</h2>
      <p>Send your information once and we'll call when a job fits. It never costs you anything.</p>
      <div class="btn-row"><a class="btn" href="job-seekers.html#apply">Send my information</a><a class="btn secondary" href="job-seekers.html">How it works</a></div></article>
  </div>
  <p class="chips-label">Roles we recruit for</p>
  <ul class="chips">{chips}</ul>
</div></section>

<section class="section tint" aria-labelledby="market-h"><div class="wrap">
  <div class="report-strip">
    <div><span class="eyebrow">New &middot; October 2026</span><h2 id="market-h">Coulee Region Industrial Hiring Report</h2>
    <p class="lede">Who is hiring, which roles stay open, and what they pay within 25 miles of La Crosse. Free to employers every quarter.</p>
    <div class="btn-row"><a class="btn" href="report.html">Read the report</a><a class="btn secondary" href="report.html#subscribe">Get it by email</a></div></div>
    <div class="stats stack">
      <div class="stat"><b>500+</b><span>open postings on the state job bank within 25 miles of La Crosse</span></div>
      <div class="stat"><b>3.0%</b><span>metro unemployment, August 2026 (preliminary)</span></div>
      <div class="stat"><b>196 days</b><span>the longest-open maintenance technician posting we found</span></div>
    </div>
  </div>
</div></section>

<section class="section" aria-labelledby="roles-h"><div class="wrap">
  <div class="section-head"><span class="eyebrow">What we recruit for</span><h2 id="roles-h">The roles that keep this region running.</h2>
  <p class="lede">We stay in our lane: the people who build, move, maintain and clean the plants and warehouses of the region.</p></div>
  <div class="grid four">{role_cards()}</div>
</div></section>

<section class="section tint" aria-labelledby="how-h"><div class="wrap">
  <div class="section-head"><span class="eyebrow">How it works</span><h2 id="how-h">Simple, and built around your team.</h2></div>
  {steps_employer()}
  <div class="btn-row" style="margin-top:24px"><a class="btn" href="employers.html#request">Request talent</a><a class="btn secondary" href="employers.html">Services for employers</a></div>
</div></section>

<section class="section" aria-labelledby="ret-h"><div class="wrap">
  <div class="grid two" style="align-items:center">
    <div><span class="eyebrow">For plants that hire every month</span><h2 id="ret-h">Your recruiting team, on retainer.</h2>
    <p class="lede">One flat monthly fee puts a recruiter on your openings every week: production, maintenance, warehouse and janitorial. Everyone we place works for you from day one.</p>
    <a class="btn" href="retainer.html">How the retainer works</a></div>
    <ul class="ticks">
      <li>Scorecards and postings for every role</li>
      <li>Local sourcing, screening and skills checks</li>
      <li>A warm bench for the roles you fill again and again</li>
      <li>A weekly pipeline update and a monthly market-pay report</li>
      <li>A replacement guarantee on every placement</li>
    </ul>
  </div>
</div></section>

<section class="section tint" aria-labelledby="why-h"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Why Driftless</span><h2 id="why-h">We know the work because we've done it.</h2>
  <p class="lede">National agencies place names off a screen. We place neighbors.</p></div>
  <div class="grid three">
    <article class="card"><div class="icon">{I["pin"]}</div><h3>We are from here</h3><p>We know the towns, the drive times, the shifts and the plants people talk about. That matters when you are asking someone to change jobs.</p></article>
    <article class="card"><div class="icon">{I["chart"]}</div><h3>Straight answers on pay</h3><p>We tell you what the market pays, using public data, and where your offer lands. Our quarterly report is free to every employer in the region.</p></article>
    <article class="card"><div class="icon">{I["shield"]}</div><h3>Built on direct hire</h3><p>The people we place work for you from day one. Terms are in writing before we send anyone, and every placement carries a replacement guarantee.</p></article>
  </div>
</div></section>

<section class="band insights section" aria-labelledby="ins-h"><div class="wrap">
  <div class="section-head"><span class="eyebrow" style="color:var(--lamp)">From the hiring report</span><h2 id="ins-h">What the numbers say this quarter</h2></div>
  <div class="grid three">
    <article class="card"><h3>Skilled roles stay open longest</h3><p>The six oldest plant postings near La Crosse had been open 172 to 196 days: maintenance, CNC machining, welding and material handling.</p><a href="report.html#open-h">The longest-open roles</a></article>
    <article class="card"><h3>Trade pay here is close to national pay</h3><p>Installation, maintenance and repair jobs average $30.27 an hour in the La Crosse metro, against $30.44 nationally.</p><a href="report.html#pay-h">What these roles pay</a></article>
    <article class="card"><h3>The hard shifts are the open ones</h3><p>Open postings name 2nd shift, 3rd shift, weekend nights and rotating 12-hour shifts.</p><a href="report.html#find-h">All four findings</a></article>
  </div>
</div></section>

<section class="section quote-band" aria-label="Our promise"><div class="wrap">
  <blockquote class="quote"><p>&#8220;When we send you a candidate, it's someone we'd vouch for in our own community.&#8221;</p>
  <footer>We are likely to see the people we place around town. That is the point of recruiting locally.</footer></blockquote>
</div></section>

<section class="section tint" aria-labelledby="start-h"><div class="wrap">
  <div class="section-head"><h2 id="start-h">If you're hiring, or looking to be hired, we'd like to help.</h2></div>
  <div class="choose">
    <article class="card"><span class="eyebrow">Employers</span><h3>I need to hire</h3><p>Tell us about the role and we will call you to talk it through.</p><a class="btn" href="employers.html#request">Request talent</a></article>
    <article class="card"><span class="eyebrow">Job seekers</span><h3>I'm looking for work</h3><p>Send your information once. We will reach out when a job fits, and it never costs you anything.</p><a class="btn" href="job-seekers.html#apply">Send my information</a></article>
  </div>
</div></section>'''


def employers():
    services = [
        ('Pay on hire', 'A single search', 'One role, filled. We search, screen and send you finalists. You pay our fee only when your new hire starts.',
         'Best for: a maintenance tech, a shift lead, a warehouse supervisor.', False),
        ('Hard-to-fill roles', 'A priority search', 'For the role that has been open for months. An up-front commitment puts the search at the top of our list, and it is credited against the final fee.',
         'Best for: CNC machinists, industrial maintenance, plant leadership.', True),
        ('Year-round hiring', 'A recruiting retainer', 'We act as your recruiting team for one flat monthly fee: sourcing, screening, scheduling and reporting, across as many roles as you need.',
         'Best for: plants that hire every month, or a new line or expansion. <a href="retainer.html">How the retainer works</a>', False),
    ]
    sv = ''.join(f'<article class="card service{" featured" if feat else ""}"><span class="tag">{E(tag)}</span><h3>{E(t)}</h3><p>{E(d)}</p><p class="best">{b}</p></article>'
                 for tag, t, d, b, feat in services)
    faqs = [
        ('Do you provide temporary workers?', 'No. We recruit for direct hire. The people we place work for you, on your payroll, from their first day. That means no hourly markup and no temp-to-hire conversion fee.'),
        ('Who pays the fee?', 'The employer. Our service is always free for job seekers.'),
        ('Is there a written agreement?', 'Yes. Fees, the replacement guarantee and payment terms are set in writing before we send you any candidates.'),
        ('What does the replacement guarantee cover?', 'If a placement doesn\'t work out within the guarantee period, we make it right: we search for a replacement at no additional fee. The exact period is set in your agreement before the search starts.'),
        ('What areas do you cover?', 'La Crosse, Onalaska, Holmen, West Salem, Sparta, Tomah, Viroqua, Westby, Coon Valley and the rest of the Coulee Region and the Driftless.'),
        ('How is a retainer different from a single search?', 'A single search fills one role and is paid on hire. A retainer is a flat monthly fee for ongoing recruiting across many roles, so you have a recruiter working on your openings every week.'),
    ]
    fq = ''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in faqs)
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">For employers</span>
  <h1>Recruiting that understands your floor, not just your job posting.</h1>
  <p class="lede">Maintenance technicians, machinists, welders, production and warehouse staff, and janitorial crews, recruited locally and screened before you ever see a resume.</p>
  <div class="btn-row" style="margin-top:24px"><a class="btn" href="#request">Request talent</a><a class="btn secondary" href="report.html">See what the market pays</a></div>
</div></section>

<section class="section" aria-labelledby="svc-h"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Services</span><h2 id="svc-h">Three ways to work with us</h2>
  <p class="lede">Every option is direct hire: your employee, on your payroll. We quote every fee after a short call and put it in writing before we start.</p></div>
  <div class="grid three">{sv}</div>
</div></section>

<section class="section tint" aria-labelledby="proc-h"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Process</span><h2 id="proc-h">What happens after you reach out</h2></div>
  {steps_employer()}
</div></section>

<section class="section" aria-labelledby="get-h"><div class="wrap">
  <div class="grid two">
    <div><span class="eyebrow">What you get</span><h2 id="get-h">More than a stack of resumes</h2>
    <ul class="ticks">
      <li>Candidates we have talked with, not just found</li>
      <li>Skills and certifications checked against your must-haves</li>
      <li>References checked before you make an offer</li>
      <li>Honest advice on pay and shifts, based on public market data</li>
      <li>Regular updates on every open search</li>
      <li>A replacement guarantee on every placement</li>
    </ul></div>
    <div><span class="eyebrow">Roles we fill</span><h2>Plant, warehouse and facility roles</h2>
    <ul class="ticks">
      <li>Industrial maintenance technicians and mechanics</li>
      <li>CNC machinists and machine operators</li>
      <li>Welders and fabricators</li>
      <li>Production workers, assemblers and leads</li>
      <li>Forklift operators and material handlers</li>
      <li>Shipping, receiving and warehouse leads</li>
      <li>Production and warehouse supervisors</li>
      <li>Custodians and plant sanitation crews</li>
    </ul></div>
  </div>
</div></section>

<section class="section tint" aria-labelledby="faq-h"><div class="wrap">
  <div class="section-head"><h2 id="faq-h">Common questions</h2></div>
  <div class="faq">{fq}</div>
</div></section>

<section class="section form-section" id="request" aria-labelledby="req-h"><div class="wrap form-layout">
  <div><span class="eyebrow">Request talent</span><h2 id="req-h">Tell us who you need.</h2>
    <p class="lede">A few details now saves time on the call.</p>
    <div class="aside-list">
      <div class="aside-item"><div class="icon">{I["clock"]}</div><div><h3>Quick to fill out</h3><p>About three minutes. Only the basics are required; skip anything marked optional.</p></div></div>
      <div class="aside-item"><div class="icon">{I["calendar"]}</div><div><h3>Next step: a short call</h3><p>We talk through the role, the shift and the pay before we start.</p></div></div>
      <div class="aside-item"><div class="icon">{I["lock"]}</div><div><h3>Kept private</h3><p>Your request is seen only by Driftless Workforce Group.</p></div></div>
    </div>
  </div>
  <div>{form_html("employer")}</div>
</div></section>'''


def retainer():
    inc = [('clipboard', 'Intake and scorecards', 'A clear must-have list for every role, agreed with the hiring manager.'),
           ('list', 'Postings that sell', 'Pay, shift and schedule up front, written for each role.'),
           ('route', 'Local sourcing', 'The state job bank, referrals, trade programs and people not yet looking.'),
           ('search', 'Screened finalists', 'Phone screens, skills checks and references before you meet anyone.'),
           ('boxes', 'A warm bench', 'A ready list of screened people for the roles you fill again and again.'),
           ('chart', 'Reporting', 'A weekly pipeline update and a monthly report with local market pay.')]
    cards = ''.join(f'<article class="card"><div class="icon">{I[ic]}</div><h3>{E(t)}</h3><p>{E(d)}</p></article>' for ic, t, d in inc)
    rows = [('How you pay', 'A markup on every hour worked', 'A fee per hire', 'One flat monthly fee'),
            ('Who they work for', 'The agency, until you convert them', 'You', 'You'),
            ('As you hire more', 'Cost grows with every hour', 'Cost grows with every hire', 'Fee stays flat, so each hire costs less'),
            ('Best for', 'Short-term spikes', 'One hard-to-fill role', 'Plants that hire every month')]
    trs = ''.join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td><td>{E(c)}</td><td><strong>{E(d)}</strong></td></tr>' for a, b, c, d in rows)
    weeks = [('Week 1', 'We walk the floor, meet your hiring managers and write a scorecard for each role.'),
             ('Week 2', 'New postings go live and sourcing is under way.'),
             ('Weeks 3 to 4', 'Your first screened finalists, ready to interview.'),
             ('Day 30', 'Your first monthly report: pipeline, hires and local pay.')]
    wk = '<ol class="steps plain">' + ''.join(f'<li><span class="eyebrow" style="color:var(--river)">{E(a)}</span><p>{E(b)}</p></li>' for a, b in weeks) + '</ol>'
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">Recruiting retainer</span>
  <h1>Your recruiting team, on retainer.</h1>
  <p class="lede">For plants and warehouses that hire every month. One flat monthly fee puts a recruiter on your openings every week, and everyone we place works for you from day one.</p>
  <div class="btn-row" style="margin-top:24px"><a class="btn" href="employers.html#request">Talk about a retainer</a><a class="btn secondary" href="report.html">See what the market pays</a></div>
</div></section>

<section class="section" aria-labelledby="why-r-h"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Why now</span><h2 id="why-r-h">Hiring one opening at a time is too slow for this market.</h2></div>
  <div class="stats">
    <div class="stat"><b>172&#8211;196</b><span>days the six oldest plant postings near La Crosse had been open, October 2026</span></div>
    <div class="stat"><b>39 days</b><span>national median time to fill a non-executive job</span></div>
    <div class="stat"><b>+25%</b><span>U.S. manufacturing job openings, August 2026 against a year earlier</span></div>
  </div>
  <p class="stats-note">Sources: Driftless hiring report (Job Center of Wisconsin data); SHRM Recruiting Benchmarking, 2026; U.S. Bureau of Labor Statistics, JOLTS, August 2026.</p>
</div></section>

<section class="section tint" aria-labelledby="inc-h"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Included every month</span><h2 id="inc-h">A whole recruiting function, not just resumes</h2></div>
  <div class="grid three">{cards}</div>
  <p style="margin-top:24px;font-weight:600">Every placement carries a replacement guarantee, and fees and terms are set in writing before we send any candidates.</p>
</div></section>

<section class="section" aria-labelledby="cmp-h"><div class="wrap">
  <div class="section-head"><span class="eyebrow">How it compares</span><h2 id="cmp-h">Three ways to pay for hiring</h2></div>
  <div class="table-scroll"><table><thead><tr><th scope="col"><span class="hp">Question</span></th><th scope="col">Temp agency</th><th scope="col">Single search</th><th scope="col">Driftless retainer</th></tr></thead>
  <tbody>{trs}</tbody></table></div>
  <p class="small muted" style="margin-top:12px">Driftless offers the single search and the retainer. We do not do temp staffing.</p>
</div></section>

<section class="section tint" aria-labelledby="first-h"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Getting started</span><h2 id="first-h">The first 30 days</h2></div>
  {wk}
</div></section>

<section class="section" aria-labelledby="fit-h"><div class="wrap">
  <div class="grid two">
    <div><span class="eyebrow">Who it is for</span><h2 id="fit-h">A good fit if you have</h2>
    <ul class="ticks"><li>Openings every month in production, maintenance, warehouse or janitorial</li><li>A new line, a new shift or an expansion coming</li><li>An HR team of one or two people doing everything</li><li>Roles that have been open 90 days or more</li></ul></div>
    <div class="card"><h3>What it costs</h3><p>One flat monthly fee, set by how many roles you have open and how hard they are to fill. We quote it after a short call about your openings.</p>
    <a class="btn" href="employers.html#request">Talk about a retainer</a></div>
  </div>
</div></section>'''


def job_seekers():
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">For job seekers</span>
  <h1>Better plant jobs, close to home. Free to you.</h1>
  <p class="lede">We recruit for plants, warehouses and facilities across the Coulee Region that need maintenance, machining, production, warehouse and janitorial staff. Send your information once, and we will reach out when a job fits.</p>
  <div class="btn-row" style="margin-top:24px"><a class="btn" href="#apply">Send my information</a></div>
</div></section>

<section class="section" aria-labelledby="exp-h"><div class="wrap">
  <div class="section-head"><span class="eyebrow">What to expect</span><h2 id="exp-h">How it works for you</h2></div>
  <ol class="steps">
    <li><h3>Send your information</h3><p>Tell us what you do, what you want, and the shifts you can work.</p></li>
    <li><h3>We talk first</h3><p>A real conversation about your skills, pay and what matters to you.</p></li>
    <li><h3>We match you</h3><p>We only bring you jobs that fit, and we never send your information to an employer without asking you.</p></li>
    <li><h3>You get hired</h3><p>You work directly for the employer, with their pay and benefits, from day one.</p></li>
  </ol>
</div></section>

<section class="section tint" aria-labelledby="why-js-h"><div class="wrap">
  <div class="grid three">
    <article class="card"><div class="icon">{I["dollar"]}</div><h3 id="why-js-h">Never a cost to you</h3><p>Employers pay our fee. You never pay to work with us.</p></article>
    <article class="card"><div class="icon">{I["route"]}</div><h3>Jobs near home</h3><p>We focus on La Crosse, Onalaska, Holmen, Sparta, Tomah, Viroqua and the towns in between.</p></article>
    <article class="card"><div class="icon">{I["list"]}</div><h3>Room to grow</h3><p>Some employers here now hire people who are ready to learn. Tell us if you are new to the trade.</p></article>
  </div>
</div></section>

<section class="section form-section" id="apply" aria-labelledby="apply-h"><div class="wrap form-layout">
  <div><span class="eyebrow">Send your information</span><h2 id="apply-h">Let's find your next job.</h2>
    <p class="lede">The more we know, the better the match.</p>
    <div class="aside-list">
      <div class="aside-item"><div class="icon">{I["lock"]}</div><div><h3>Your information stays private</h3><p>Only Driftless Workforce Group sees it. We ask before sharing it with any employer.</p></div></div>
      <div class="aside-item"><div class="icon">{I["clipboard"]}</div><div><h3>No resume needed</h3><p>Attach one if you have it. If not, send the form anyway.</p></div></div>
      <div class="aside-item"><div class="icon">{I["shield"]}</div><div><h3>Equal opportunity</h3><p>We recruit without regard to race, color, religion, sex, national origin, age, disability, veteran status or any other status protected by law.</p></div></div>
    </div>
  </div>
  <div>{form_html("candidate")}</div>
</div></section>'''


def report():
    rows = ''.join(f'<tr><td>{E(r)}</td><td>{E(s) if s else "&#8212;"}</td><td>{E(d)}</td><td class="n">{n}</td></tr>' for r, s, d, n in OPEN_ROLES)
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">Quarterly &middot; October 2026</span>
  <h1>Coulee Region Industrial Hiring Report</h1>
  <p class="lede">What plant and warehouse hiring looks like within 25 miles of La Crosse, from public job postings and federal wage data. Free to employers every quarter.</p>
</div></section>

<section class="section" aria-labelledby="glance-h"><div class="wrap">
  <div class="section-head"><h2 id="glance-h">At a glance</h2>
  <p class="lede">The region is still short on skilled plant workers. The jobs that sit open longest are the ones that keep a line running.</p></div>
  <div class="stats">
    <div class="stat"><b>500+</b><span>open postings within 25 miles of La Crosse on October 12, 2026 (538+ openings)</span></div>
    <div class="stat"><b>3.0%</b><span>metro unemployment in August 2026, preliminary</span></div>
    <div class="stat"><b>172&#8211;196</b><span>days open for the six oldest postings we found, all plant roles</span></div>
  </div>
</div></section>

<section class="section tint" aria-labelledby="find-h"><div class="wrap">
  <div class="section-head"><h2 id="find-h">Four findings</h2></div>
  <div class="grid two findings">
    <div class="finding"><h3>Skilled roles stay open longest</h3><p>Of 135 postings we read, 10 had been listed more than 90 days. The six oldest were maintenance, CNC machining, welding and material handling jobs.</p></div>
    <div class="finding"><h3>Trade pay here is close to national pay</h3><p>The metro's average wage for all jobs is 10% below the U.S. average, but installation, maintenance and repair jobs pay at par: $30.27 an hour here against $30.44 nationally.</p></div>
    <div class="finding"><h3>Employers are opening skilled roles to trainees</h3><p>At least six machining postings now say &#8220;entry level or experienced.&#8221;</p></div>
    <div class="finding"><h3>The hard shifts are the open ones</h3><p>Open postings name 2nd shift, 3rd shift, weekend nights and rotating 12-hour shifts.</p></div>
  </div>
  <figure class="figure" style="margin-top:32px"><figcaption style="margin:0 0 10px;font-weight:600;color:var(--ink);font-size:1.05rem">Maintenance and production each appear in about 140 postings</figcaption>
    <div class="chart">{chart_postings()}</div>
    <figcaption>State job bank postings that mention each word, within 25 miles of ZIP 54601, October 12, 2026. Searches overlap, and a word can appear in an unrelated posting. Source: Job Center of Wisconsin.</figcaption></figure>
</div></section>

<section class="section" aria-labelledby="pay-h"><div class="wrap">
  <div class="section-head"><h2 id="pay-h">What these roles pay</h2>
  <p class="lede">The trades that stay open pay $28 to $31 an hour at the median. These are May 2025 figures, the newest available; treat them as a floor.</p></div>
  <figure class="figure"><div class="chart">{chart_wages()}</div>
  <figcaption>Hourly wages in the La Crosse&#8211;Onalaska metro, May 2025. Bar = median, line = 10th to 90th percentile, blue = roles that stay open longest. Source: U.S. Bureau of Labor Statistics, Occupational Employment and Wage Statistics.</figcaption></figure>
</div></section>

<section class="section tint" aria-labelledby="open-h"><div class="wrap">
  <div class="section-head"><h2 id="open-h">The longest-open roles</h2><p class="lede">No employer is named in this report.</p></div>
  <div class="table-scroll"><table><caption class="hp">The six longest-open postings found on October 12, 2026</caption>
  <thead><tr><th scope="col">Role</th><th scope="col">Shift noted</th><th scope="col">Listed since</th><th scope="col" class="n">Days open</th></tr></thead>
  <tbody>{rows}</tbody></table></div>
  <p class="small muted" style="margin-top:12px">Posting dates are those shown by the state site. A reposted job can show a newer date, so real time-to-fill can be longer.</p>
</div></section>

<section class="section" aria-labelledby="mean-h"><div class="wrap">
  <div class="section-head"><h2 id="mean-h">What this means for employers</h2></div>
  <div class="grid two">
    <ul class="ticks">
      <li><strong>Price skilled roles against the market,</strong> not the area average for all jobs.</li>
      <li><strong>Treat 90 days open as a signal</strong> to change the pay, the shift, the requirements or the search.</li>
      <li><strong>Hire for trainability</strong> where you can, and back it with a written training plan.</li>
      <li><strong>Sell the shift:</strong> schedule, shift premium and days off in the first lines of the posting.</li>
      <li><strong>Move fast:</strong> a same-week interview often decides it.</li>
    </ul>
    <div class="card"><h3>How this report was made</h3>
      <p class="small muted">Job postings: Job Center of Wisconsin, the Wisconsin DWD public job board; 16 keyword searches and one open search within 25 miles of ZIP 54601 on October 12, 2026. Wages: U.S. Bureau of Labor Statistics, Occupational Employment and Wage Statistics, May 2025, La Crosse&#8211;Onalaska WI-MN metro (released August 3, 2026). Labor market: BLS Economy at a Glance, August 2026, preliminary. Not every employer posts on the state board, so these figures understate total hiring.</p></div>
  </div>
</div></section>

<section class="section tint form-section" id="subscribe" aria-labelledby="sub-h"><div class="wrap form-layout">
  <div><span class="eyebrow">Free every quarter</span><h2 id="sub-h">Get the full report by email.</h2>
    <p class="lede">The full October edition, then each new one as it comes out. Written for plant, operations and HR managers.</p></div>
  <div>{form_html("report")}</div>
</div></section>'''


def contact():
    phone = f'<div class="aside-item"><div class="icon">{I["phone"]}</div><div><h3>Call or text</h3><p>{E(SITE["phone"])}</p></div></div>' if SITE['phone'] else ''
    email = f'<div class="aside-item"><div class="icon">{I["mail"]}</div><div><h3>Email</h3><p>{E(SITE["email"])}</p></div></div>' if SITE['email'] else ''
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">Contact</span>
  <h1>Talk with Driftless.</h1>
  <p class="lede">We're local, we're responsive, and there's no cost to start a conversation.</p>
</div></section>
<section class="section form-section" aria-labelledby="c-h"><div class="wrap form-layout">
  <div><h2 id="c-h">Send a message</h2>
    <div class="aside-list">
      <div class="aside-item"><div class="icon">{I["pin"]}</div><div><h3>Where we are</h3><p>{E(SITE["city"])}, serving the Coulee Region and the Driftless.</p></div></div>
      {phone}{email}
      <div class="aside-item"><div class="icon">{I["factory"]}</div><div><h3>Hiring?</h3><p>The <a href="employers.html#request">talent request form</a> gets your role started fastest.</p></div></div>
      <div class="aside-item"><div class="icon">{I["clipboard"]}</div><div><h3>Looking for work?</h3><p><a href="job-seekers.html#apply">Send your information</a> and we will reach out when a job fits.</p></div></div>
    </div>
  </div>
  <div>{form_html("question")}</div>
</div></section>'''


def about():
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">About</span>
  <h1>Built here. For here.</h1>
  <p class="lede">Driftless Workforce Group started from a simple observation: most of the recruiters serving this region aren't from it. They work from databases and job boards. We work from here.</p>
</div></section>
<section class="section"><div class="wrap">
  <div class="grid three">
    <article class="card"><div class="icon">{I["wrench"]}</div><h3>Our approach</h3><p>We came to recruiting from the worker's side, after years in floor, line and kitchen jobs. We know the work because we've done it, so we can judge who will show up, fit in and stay.</p></article>
    <article class="card"><div class="icon">{I["pin"]}</div><h3>The regional advantage</h3><p>The La Crosse area and the Driftless are home, not a market. National agencies place names off a screen. We place neighbors.</p></article>
    <article class="card"><div class="icon">{I["shield"]}</div><h3>Our commitment</h3><p>Employer-paid, and job seekers never pay a fee. Every placement is backed by a guarantee, and we are in it for long-term relationships, not one-off fills.</p></article>
  </div>
</div></section>
<section class="section tint"><div class="wrap">
  <div class="grid two" style="align-items:center">
    <div><span class="eyebrow">Founder</span><h2>Casey Guy</h2><p class="lede">Founder of Driftless Workforce Group LLC, based in La Crosse, Wisconsin.</p>
    <p>Call or text {E(SITE["phone"])}{(" or email " + E(SITE["email"])) if SITE["email"] else ""}.</p></div>
    <div class="choose">
      <article class="card"><span class="eyebrow">Employers</span><h3>I need to hire</h3><a class="btn" href="employers.html#request">Request talent</a></article>
      <article class="card"><span class="eyebrow">Job seekers</span><h3>I'm looking for work</h3><a class="btn" href="job-seekers.html#apply">Send my information</a></article>
    </div>
  </div>
</div></section>'''


def privacy():
    return '''
<section class="page-hero"><div class="wrap"><span class="eyebrow">Privacy</span><h1>How we handle your information</h1>
<p class="lede">Plain language, no surprises.</p></div></section>
<section class="section"><div class="wrap prose">
<p>This notice covers Driftless Workforce Group LLC, a Wisconsin company based in La Crosse.</p>
<h2>What we collect</h2>
<p>Only what you send us through this site: your name and contact details, and what you tell us about a job you want to fill or the work you are looking for. If you attach a resume, we keep that file too.</p>
<h2>How we use it</h2>
<p>To answer you, to recruit for the roles employers ask us to fill, and to match job seekers with those roles. If you sign up for the hiring report, we use your email to send it.</p>
<h2>Who sees it</h2>
<p>Driftless Workforce Group LLC only. We never sell your information. We send a job seeker's resume or personal details to an employer only after that person agrees.</p>
<h2>Where it is kept</h2>
<p>Form submissions and resumes are stored in a private account that only Driftless Workforce Group LLC can open. Our website host keeps them for us and does not use them for anything else.</p>
<h2>Fair treatment</h2>
<p>We recruit and screen every candidate the same way, without regard to race, color, religion, sex, national origin, age, disability, veteran status or any other status protected by law.</p>
<h2>Your choices</h2>
<p>You can ask us to update or delete your information, or to stop contacting you, at any time. Use the <a href="contact.html">contact form</a> and we will take care of it.</p>
</div></section>'''


def not_found():
    return '''<section class="page-hero"><div class="wrap"><span class="eyebrow">Page not found</span><h1>That page isn't here.</h1>
<p class="lede">It may have moved. Try one of these instead.</p>
<div class="btn-row" style="margin-top:24px"><a class="btn" href="./">Home</a><a class="btn secondary" href="employers.html">For employers</a><a class="btn secondary" href="job-seekers.html">For job seekers</a></div></div></section>'''


PAGES = [
    ('index.html', 'Driftless Workforce Group | Plant and warehouse recruiting in La Crosse',
     'Direct-hire recruiting for manufacturing, warehousing, maintenance and janitorial roles across the Coulee Region.', home, ''),
    ('retainer.html', 'Recruiting retainer | Driftless Workforce Group',
     'One flat monthly fee for a recruiter on your plant and warehouse openings every week. Direct hire, on your payroll.', retainer, 'retainer.html'),
    ('employers.html', 'For employers | Driftless Workforce Group',
     'Recruiting for maintenance technicians, machinists, welders, production, warehouse and janitorial roles. Direct hire, on your payroll.', employers, 'employers.html'),
    ('job-seekers.html', 'Find plant and warehouse jobs | Driftless Workforce Group',
     'Maintenance, machining, production, warehouse and janitorial jobs near La Crosse. Always free for job seekers.', job_seekers, 'job-seekers.html'),
    ('report.html', 'Coulee Region Industrial Hiring Report, October 2026 | Driftless Workforce Group',
     'Who is hiring, which roles stay open and what they pay, within 25 miles of La Crosse. Free every quarter.', report, 'report.html'),
    ('contact.html', 'Contact | Driftless Workforce Group', 'Questions about hiring, a job, or the hiring report.', contact, 'contact.html'),
    ('about.html', 'About | Driftless Workforce Group', 'Built here. For here. A La Crosse recruiting firm that came to the work from the worker\'s side.', about, 'about.html'),
    ('privacy.html', 'Privacy | Driftless Workforce Group', 'How Driftless Workforce Group handles your information.', privacy, ''),
    ('404.html', 'Page not found | Driftless Workforce Group', 'Page not found.', not_found, ''),
]

# ---------------------------------------------------------------- backend schema for Apps Script (generated from FORMS)
def backend_schema():
    out = {}
    for key, F in FORMS.items():
        cols = [[name, (label if kind != 'consent' else 'Agreed to contact')] for kind, name, label, o in F['fields'] if kind != 'file']
        out[key] = {'tab': F['tab'], 'fields': cols, 'file': any(k == 'file' for k, *_ in F['fields'])}
    return out


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)


def main():
    out, prev = os.path.join(ROOT, 'out'), os.path.join(ROOT, 'preview')
    for d in (out, prev):
        shutil.rmtree(d, ignore_errors=True)
        shutil.copytree(os.path.join(ROOT, 'src', 'assets'), os.path.join(d, 'assets'))
    for slug, title, desc, fn, cur in PAGES:
        main_html = fn()
        write(os.path.join(out, slug), page(slug, title, desc, main_html, cur))
        if slug == 'index.html':
            write(os.path.join(prev, slug), page(slug, title, desc, main_html, cur, preview=True, bare=True, preview_title='Driftless Workforce Group'))
        else:
            write(os.path.join(prev, slug), page(slug, title, desc, main_html, cur, preview=True))
    write(os.path.join(out, '.nojekyll'), '')
    # Netlify: keep the old short addresses (/employers, /about ...) working
    write(os.path.join(out, '_redirects'), ''.join(f'/{s[:-5]}  /{s}  200\n' for s, *_ in PAGES if s not in ('index.html', '404.html')))
    # Backend
    tpl = open(os.path.join(ROOT, 'apps-script', 'Code.template.gs'), encoding='utf-8').read()
    write(os.path.join(ROOT, 'apps-script', 'Code.gs'), tpl.replace('/*SCHEMA*/{}', json.dumps(backend_schema(), indent=2)))
    inbox = open(os.path.join(ROOT, 'apps-script', 'Inbox.html'), encoding='utf-8').read()
    write(os.path.join(prev, 'inbox.html'), inbox.replace('/*SCHEMA*/{}', json.dumps(backend_schema())))
    print('built', len(PAGES), 'pages ->', out, 'and', prev)


if __name__ == '__main__':
    main()
