#!/usr/bin/env python3
"""Builds the Driftless Workforce Group website.

  python3 build.py            -> out/      full site, ready for any static host (GitHub Pages, Netlify, a domain)
                                 preview/  the same site packaged for a claude.ai preview artifact
                                 apps-script/Code.gs + Inbox.html  the forms backend and private inbox

Update SITE below to change contact details, then rebuild.
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

ROLES = ['Maintenance technician', 'CNC machinist / machine operator', 'Production / assembly', 'Welder / fabricator',
         'Warehouse / forklift operator', 'Production supervisor / lead', 'Janitorial / sanitation', 'Other']
SHIFTS = ['1st shift', '2nd shift', '3rd shift', 'Weekends', 'Rotating / 12-hour']

FORMS = {
  'employer': dict(tab='Employer requests', id='request-form', submit='Submit Request',
    done_title='Request received', done_text='Thank you. We will contact you shortly to discuss the position.',
    fields=[
      ('text', 'company', 'Company', dict(auto='organization', half=True, msg='Company is required.')),
      ('text', 'name', 'Contact name', dict(auto='name', half=True, msg='Contact name is required.')),
      ('email', 'email', 'Work email', dict(auto='email', half=True, msg='Work email is required.')),
      ('tel', 'phone', 'Phone', dict(auto='tel', half=True, msg='Phone is required.')),
      ('text', 'title', 'Job title', dict(auto='organization-title', half=True, optional=True)),
      ('text', 'location', 'Job location', dict(half=True, ph='City or facility', msg='Job location is required.')),
      ('checks', 'roles', 'Positions needed', dict(options=ROLES, msg='At least one position is required.')),
      ('number', 'openings', 'Number of openings', dict(half=True, min=1, max=500, msg='Number of openings is required.')),
      ('select', 'timing', 'Target start date', dict(half=True, options=['Immediately', 'Within 30 days', 'Within 60 to 90 days', 'Future planning'], msg='Target start date is required.')),
      ('checks', 'shifts', 'Shifts', dict(options=SHIFTS, optional=True)),
      ('text', 'pay', 'Pay range', dict(optional=True, half=True, ph='$24 to $30 per hour')),
      ('select', 'service', 'Service of interest', dict(optional=True, half=True, options=['Not sure yet', 'Single search', 'Priority search', 'Recruiting retainer'])),
      ('textarea', 'notes', 'Additional details', dict(optional=True, hint='Required skills, certifications, schedule or other requirements')),
    ]),
  'candidate': dict(tab='Job seekers', id='apply-form', submit='Submit',
    done_title='Information received', done_text='Thank you. We will contact you when a position matches your experience. Your information is never shared with an employer without your permission.',
    fields=[
      ('text', 'name', 'Full name', dict(auto='name', half=True, msg='Full name is required.')),
      ('tel', 'phone', 'Phone', dict(auto='tel', half=True, msg='Phone is required.')),
      ('email', 'email', 'Email', dict(auto='email', half=True, msg='Email is required.')),
      ('text', 'zip', 'ZIP code', dict(auto='postal-code', half=True, inputmode='numeric', pattern='[0-9]{5}', pattern_msg='ZIP code must be 5 digits.', msg='ZIP code is required.')),
      ('checks', 'work', 'Positions of interest', dict(options=ROLES, msg='At least one position is required.')),
      ('select', 'experience', 'Experience', dict(half=True, options=['No experience, willing to learn', 'Less than 1 year', '1 to 3 years', '3 to 10 years', 'More than 10 years'], msg='Experience is required.')),
      ('select', 'start', 'Availability', dict(half=True, options=['Immediately', 'Within 2 weeks', 'Within 30 days', 'Exploring options'], msg='Availability is required.')),
      ('checks', 'shifts', 'Shifts available', dict(options=SHIFTS, msg='At least one shift is required.')),
      ('select', 'license', "Driver's license", dict(half=True, options=["Valid driver's license", 'CDL Class A', 'CDL Class B', 'None'], msg="Driver's license is required.")),
      ('text', 'pay', 'Desired pay', dict(optional=True, half=True, ph='$22 per hour')),
      ('text', 'certs', 'Certifications', dict(optional=True, hint='Forklift, welding, OSHA 10, electrical, CNC, food safety')),
      ('file', 'resume', 'Resume', dict(optional=True, hint='PDF or Word, up to 5 MB')),
      ('textarea', 'notes', 'Additional information', dict(optional=True)),
      ('consent', 'consent', 'I agree to be contacted by Driftless Workforce Group about job opportunities by phone, text or email. I may opt out at any time.', dict(msg='Consent is required to submit this form.')),
    ]),
  'question': dict(tab='Questions', id='contact-form', submit='Send Message',
    done_title='Message sent', done_text='Thank you. We will respond as soon as possible.',
    fields=[
      ('text', 'name', 'Name', dict(auto='name', half=True, msg='Name is required.')),
      ('email', 'email', 'Email', dict(auto='email', half=True, msg='Email is required.')),
      ('tel', 'phone', 'Phone', dict(auto='tel', half=True, optional=True)),
      ('select', 'who', 'I am a', dict(half=True, options=['Employer', 'Job seeker', 'Other'], msg='This field is required.')),
      ('textarea', 'message', 'Message', dict(msg='Message is required.')),
    ]),
  'report': dict(tab='Report sign-ups', id='report-form', submit='Subscribe',
    done_title='Subscription confirmed', done_text='Thank you. The October report and future editions will be sent to your email.',
    fields=[
      ('text', 'name', 'Name', dict(auto='name', half=True, msg='Name is required.')),
      ('email', 'email', 'Work email', dict(auto='email', half=True, msg='Work email is required.')),
      ('text', 'company', 'Company', dict(auto='organization', half=True, msg='Company is required.')),
      ('text', 'title', 'Job title', dict(auto='organization-title', half=True, optional=True)),
      ('consent', 'consent', 'I would like to receive the Coulee Region Industrial Hiring Report by email each quarter. I may unsubscribe at any time.', dict(msg='Consent is required to subscribe.')),
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
        if o.get('ph'): attrs += f' placeholder="{E(o["ph"])}"'
        if kind == 'number': attrs += f' min="{o.get("min", "")}" max="{o.get("max", "")}" inputmode="numeric"'
        return (f'<div {common} data-kind="input"><label for="{fid}">{E(label)}{opt_txt}</label>{hint}'
                f'<input class="input" id="{fid}" name="{name}" type="{kind}"{attrs}{desc}{req}></div>')
    if kind == 'select':
        opts = '<option value="">Select</option>' + ''.join(f'<option>{E(x)}</option>' for x in o['options'])
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


NAV = [('employers.html', 'Employers'), ('retainer.html', 'Retainer'), ('job-seekers.html', 'Job Seekers'),
       ('report.html', 'Hiring Report'), ('about.html', 'About'), ('contact.html', 'Contact')]


def form_html(key):
    F = FORMS[key]
    fid = F['id']
    fallback = f' data-fallback="You can also reach us at {E(SITE["email"])}."' if SITE['email'] else ''
    rows = ''.join(field_html(fid, f) for f in F['fields'])
    enc = ' enctype="multipart/form-data"' if any(f[0] == 'file' for f in F['fields']) else ''
    return (f'<form id="{fid}" name="{key}" method="POST" data-netlify="true" netlify-honeypot="website_url"{enc} class="form-card" data-form="{key}" data-done="{fid}-done"{fallback} aria-label="{E(F["submit"])}">'
            f'<input type="hidden" name="form-name" value="{key}">'
                        f'<div class="fields">{rows}</div>'
            f'<div class="hp" aria-hidden="true"><label for="{fid}-website">Website</label>'
            f'<input id="{fid}-website" name="website_url" type="text" tabindex="-1" autocomplete="off"></div>'
            f'<div class="form-actions"><button class="btn" type="submit">{E(F["submit"])}</button>'
            f'<span class="small"><a href="privacy.html">Privacy policy</a></span></div>'
            f'</form>'
            f'<div id="{fid}-done" class="form-card form-done" hidden><div class="done-icon">{I["bigcheck"]}</div>'
            f'<h3>{E(F["done_title"])}</h3><p>{E(F["done_text"])}</p>'
            f'<p class="notice preview" hidden>Preview only. This form is not connected, so nothing was sent.</p>'
            f'<button type="button" class="btn secondary small" data-reset="{fid}">New submission</button></div>')

# ---------------------------------------------------------------- report data (October 2026 edition)
POSTINGS = [('Maintenance', 145), ('Production', 141), ('Warehouse', 86), ('Forklift', 49), ('CDL', 39), ('Machinist', 26),
            ('CNC', 25), ('Mechanic', 11), ('Welder', 7), ('Custodian', 7), ('Electrician', 4), ('Assembler', 2)]
WAGES = [('Electricians', 37.87, 22.02, 52.34), ('Production supervisors', 34.19, 23.91, 46.73),
         ('Industrial machinery mechanics', 31.03, 24.28, 46.59), ('Machinists', 30.27, 17.83, 38.67),
         ('Heavy truck drivers', 28.99, 22.60, 39.17), ('Welders and brazers', 28.27, 23.45, 37.65),
         ('CNC tool operators', 26.15, 20.07, 32.71), ('Maintenance and repair, general', 25.56, 17.59, 34.18),
         ('Assemblers and fabricators', 22.18, 17.92, 28.53), ('Packaging machine operators', 22.06, 17.78, 23.41),
         ('Forklift operators', 21.45, 18.91, 27.09), ('Hand laborers and material movers', 20.58, 14.89, 26.75),
         ('Janitors and cleaners', 17.37, 14.36, 22.39), ('Stockers and order fillers', 16.42, 13.98, 22.51)]
OPEN_ROLES = [('Maintenance technician', '', 'March 30, 2026', 196),
              ('CNC lathe machinist / machine operator', '3rd shift', 'April 15, 2026', 180),
              ('CNC lathe machinist / machine operator', '2nd shift', 'April 15, 2026', 180),
              ('Welder', '', 'April 23, 2026', 172), ('Gas welder / brazer', '', 'April 23, 2026', 172),
              ('Material handler', '', 'April 23, 2026', 172)]


def chart_postings():
    y0, rh, x0, w = 16, 28, 130, 700
    peak = max(v for _, v in POSTINGS)
    H = y0 + len(POSTINGS) * rh + 8
    out = [f'<svg viewBox="0 0 900 {H}" role="img" aria-labelledby="c1t"><title id="c1t">Job postings by keyword: '
           + '; '.join(f'{k} {v}' for k, v in POSTINGS) + '.</title>']
    for i, (k, v) in enumerate(POSTINGS):
        y = y0 + i * rh
        bw = v / peak * w
        out.append(f'<text x="{x0-10}" y="{y+18}" text-anchor="end" font-size="13" fill="var(--ink)">{E(k)}</text>'
                   f'<rect x="{x0}" y="{y+5}" width="{bw:.1f}" height="18" rx="2" fill="var(--river)"/>'
                   f'<text x="{x0+bw+8:.1f}" y="{y+18}" font-size="13" font-weight="600" fill="var(--ink)">{v}</text>')
    out.append(f'<path d="M{x0} {y0} V{y0+len(POSTINGS)*rh}" stroke="var(--ink-2)" stroke-width="1"/></svg>')
    return ''.join(out)


def chart_wages():
    y0, rh, x0, w, cap = 40, 30, 250, 300, 55
    sx = lambda v: x0 + v / cap * w
    H = y0 + len(WAGES) * rh + 8
    out = [f'<svg viewBox="0 0 760 {H}" role="img" aria-labelledby="c2t"><title id="c2t">Median hourly wage and 10th to 90th percentile range by occupation, La Crosse-Onalaska metro, May 2025: '
           + '; '.join(f'{r} ${m:.2f} (${lo:.0f} to ${hi:.0f})' for r, m, lo, hi in WAGES) + '.</title>',
           f'<rect x="{x0}" y="10" width="22" height="12" rx="2" fill="var(--river)"/>'
           f'<text x="{x0+30}" y="20" font-size="12" fill="var(--ink-2)">Median</text>'
           f'<path d="M{x0+100} 16 H{x0+130} M{x0+100} 11 V21 M{x0+130} 11 V21" stroke="var(--ink)" stroke-width="1.5" opacity=".7"/>'
           f'<text x="{x0+138}" y="20" font-size="12" fill="var(--ink-2)">10th to 90th percentile</text>',
           f'<text x="660" y="20" text-anchor="end" font-size="12" fill="var(--ink-2)">Median</text>',
           f'<text x="750" y="20" text-anchor="end" font-size="12" fill="var(--ink-2)">Range</text>']
    for i, (r, m, lo, hi) in enumerate(WAGES):
        y = y0 + i * rh
        out.append(f'<text x="{x0-10}" y="{y+19}" text-anchor="end" font-size="14" fill="var(--ink)">{E(r)}</text>'
                   f'<rect x="{x0}" y="{y+6}" width="{sx(m)-x0:.1f}" height="18" rx="2" fill="var(--river)"/>'
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
            f'<a class="brand" href="./" aria-label="Driftless Workforce Group home"><span class="brand-name"><b>Driftless</b><span>Workforce Group</span></span></a>'
            f'<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav">{MENU_ICON}Menu</button>'
            f'<nav id="site-nav" class="nav" aria-label="Main" data-open="true">{links}'
            f'<a class="btn small" href="employers.html#request">Request Talent</a></nav>'
            f'</div></header>')


def footer(preview):
    contact = [f'<li>{E(SITE["city"])}</li>']
    if SITE['phone']: contact.append(f'<li><a href="tel:+1{"".join(c for c in SITE["phone"] if c.isdigit())}">{E(SITE["phone"])}</a></li>')
    if SITE['email']: contact.append(f'<li><a href="mailto:{E(SITE["email"])}">{E(SITE["email"])}</a></li>')
    staff = SITE['inbox_url'] or ('inbox.html' if preview else '')
    staff_link = f'<a href="{E(staff)}" rel="nofollow">Staff Login</a>' if staff else ''
    return (f'<footer class="site-footer"><div class="wrap"><div class="foot-grid">'
            f'<div><div class="foot-brand"><b>Driftless Workforce Group</b></div>'
            f'<p>Direct-hire recruiting for manufacturing, warehouse, maintenance and janitorial positions in the La Crosse area.</p></div>'
            f'<div><h2>Employers</h2><ul><li><a href="employers.html">Services</a></li><li><a href="retainer.html">Recruiting Retainer</a></li>'
            f'<li><a href="employers.html#request">Request Talent</a></li><li><a href="report.html">Hiring Report</a></li></ul></div>'
            f'<div><h2>Job Seekers</h2><ul><li><a href="job-seekers.html">How It Works</a></li><li><a href="job-seekers.html#apply">Submit Your Information</a></li>'
            f'<li><a href="about.html">About</a></li></ul></div>'
            f'<div><h2>Contact</h2><ul>{"".join(contact)}</ul></div>'
            f'</div><div class="foot-base"><span>&copy; {SITE["year"]} Driftless Workforce Group LLC. All rights reserved.</span>'
            f'<span class="foot-links"><a href="privacy.html">Privacy Policy</a>{staff_link}</span></div></div></footer>')


# ---------------------------------------------------------------- page bodies
def role_cards():
    cards = [
        ('factory', 'Manufacturing and production', 'CNC machinists, machine operators, assemblers, welders, fabricators, production leads and supervisors.'),
        ('boxes', 'Warehousing and logistics', 'Forklift operators, material handlers, shipping and receiving, inventory and warehouse leads.'),
        ('wrench', 'Maintenance and facilities', 'Industrial maintenance technicians, mechanics, facilities technicians and building maintenance staff.'),
        ('bucket', 'Janitorial and sanitation', 'Custodians, plant sanitation crews, facility cleaning staff and leads.'),
    ]
    return ''.join(f'<article class="card"><div class="icon">{I[ic]}</div><h3>{E(t)}</h3><p class="role-list">{E(d)}</p></article>' for ic, t, d in cards)


def steps_employer():
    s = [('Consultation', 'We discuss the position, schedule, pay and requirements with you.'),
         ('Recruiting and screening', 'We source local candidates, verify skills and check references.'),
         ('Interviews', 'You meet a short list of qualified finalists.'),
         ('Placement', 'Your new employee starts on your payroll, covered by our replacement guarantee.')]
    return '<ol class="steps">' + ''.join(f'<li><h3>{E(a)}</h3><p>{E(b)}</p></li>' for a, b in s) + '</ol>'


def contact_line():
    parts = []
    if SITE['phone']:
        parts.append(f'<span>Phone: <a href="tel:+1{"".join(c for c in SITE["phone"] if c.isdigit())}">{E(SITE["phone"])}</a> (call or text)</span>')
    if SITE['email']:
        parts.append(f'<span>Email: <a href="mailto:{E(SITE["email"])}">{E(SITE["email"])}</a></span>')
    return f'<p class="contact-lines">{"".join(parts)}</p>'



def home():
    roles = ['Maintenance technicians', 'CNC machinists', 'Welders and fabricators', 'Production and assembly', 'Forklift and warehouse',
             'Production supervisors', 'Facilities technicians', 'Janitorial and sanitation']
    chips = ''.join(f'<li>{E(r)}</li>' for r in roles)
    return f'''
<section class="hero split"><div class="wrap">
  <div class="hero-copy">
    <span class="eyebrow">Direct-hire recruiting &middot; La Crosse region</span>
    <h1>Hiring talent that stays. Right here in the Driftless.</h1>
    <p class="lede">Driftless Workforce Group connects manufacturers, warehouses and facilities across the Coulee Region with reliable, job-ready people from the local community. Our service is employer-paid and always free for job seekers.</p>
  </div>
  <div class="doors">
    <article class="door"><span class="eyebrow">Employers</span><h2>Hiring?</h2>
      <p>We recruit maintenance, production, warehouse and janitorial staff for direct hire.</p>
      <div class="btn-row"><a class="btn" href="employers.html#request">Request Talent</a><a class="btn secondary" href="employers.html">Our Services</a></div></article>
    <article class="door seek"><span class="eyebrow">Job Seekers</span><h2>Looking for work?</h2>
      <p>Submit your information once and we will contact you when a position matches your skills. There is never a fee.</p>
      <div class="btn-row"><a class="btn" href="job-seekers.html#apply">Submit Your Information</a><a class="btn secondary" href="job-seekers.html">How It Works</a></div></article>
  </div>
  <p class="chips-label">Positions we recruit for</p>
  <ul class="chips">{chips}</ul>
</div></section>

<section class="section tint" aria-labelledby="market-h"><div class="wrap">
  <div class="report-strip">
    <div><span class="eyebrow">Hiring report &middot; October 2026</span><h2 id="market-h">Coulee Region Industrial Hiring Report</h2>
    <p class="lede">Hiring activity, hard-to-fill positions and local pay rates within 25 miles of La Crosse. Published quarterly and free to employers.</p>
    <div class="btn-row"><a class="btn" href="report.html">Read the Report</a><a class="btn secondary" href="report.html#subscribe">Subscribe</a></div></div>
    <div class="stats stack">
      <div class="stat"><b>500+</b><span>Open job postings within 25 miles of La Crosse</span></div>
      <div class="stat"><b>3.0%</b><span>Unemployment rate, La Crosse&#8211;Onalaska metro, August 2026</span></div>
      <div class="stat"><b>196 days</b><span>Longest-open maintenance technician posting</span></div>
    </div>
  </div>
</div></section>

<section class="section" aria-labelledby="roles-h"><div class="wrap">
  <div class="section-head"><h2 id="roles-h">Industries we serve</h2></div>
  <div class="grid four">{role_cards()}</div>
</div></section>

<section class="section tint" aria-labelledby="how-h"><div class="wrap">
  <div class="section-head"><h2 id="how-h">How it works</h2></div>
  {steps_employer()}
  <div class="btn-row" style="margin-top:24px"><a class="btn" href="employers.html#request">Request Talent</a><a class="btn secondary" href="employers.html">Our Services</a></div>
</div></section>

<section class="section" aria-labelledby="ret-h"><div class="wrap">
  <div class="grid two" style="align-items:center">
    <div><h2 id="ret-h">Recruiting retainer</h2>
    <p class="lede">For employers with ongoing hiring needs. One flat monthly fee covers recruiting for an agreed set of positions, and every hire is employed directly by you.</p>
    <a class="btn" href="retainer.html">Learn More</a></div>
    <ul class="ticks">
      <li>Job profiles and postings for each position</li>
      <li>Local sourcing, screening and skills checks</li>
      <li>A pool of pre-screened candidates for recurring roles</li>
      <li>Weekly status updates and a monthly pay report</li>
      <li>Replacement guarantee on every placement</li>
    </ul>
  </div>
</div></section>

<section class="section tint" aria-labelledby="why-h"><div class="wrap">
  <div class="section-head"><h2 id="why-h">We know the work because we've done it.</h2>
  <p class="lede">National agencies place names off a screen. We place neighbors.</p></div>
  <div class="grid three">
    <article class="card"><div class="icon">{I["pin"]}</div><h3>Local knowledge</h3><p>We live and work in the Coulee Region and know its employers, commutes and shift patterns.</p></article>
    <article class="card"><div class="icon">{I["chart"]}</div><h3>Market data</h3><p>We track local job postings and wage data and publish the findings in a free quarterly report for employers.</p></article>
    <article class="card"><div class="icon">{I["shield"]}</div><h3>Direct hire</h3><p>Candidates are hired directly by you. Terms are confirmed in writing before we begin, and every placement includes a replacement guarantee.</p></article>
  </div>
</div></section>

<section class="band insights section" aria-labelledby="ins-h"><div class="wrap">
  <div class="section-head"><h2 id="ins-h">From the October 2026 hiring report</h2></div>
  <div class="grid three">
    <article class="card"><h3>Skilled positions stay open longest</h3><p>The six longest-open plant postings near La Crosse had been listed for 172 to 196 days.</p><a href="report.html#open-h">Longest-open postings</a></article>
    <article class="card"><h3>Trade wages are near the national average</h3><p>Installation, maintenance and repair occupations average $30.27 an hour in the La Crosse metro, compared with $30.44 nationally.</p><a href="report.html#pay-h">Pay by occupation</a></article>
    <article class="card"><h3>Off-shift machining roles are hard to fill</h3><p>Two of the six longest-open postings are 2nd- and 3rd-shift CNC machining positions.</p><a href="report.html#find-h">Key findings</a></article>
  </div>
</div></section>

<section class="section quote-band" aria-label="Our approach"><div class="wrap">
  <blockquote class="quote"><p>&#8220;When we send you a candidate, it's someone we'd vouch for in our own community.&#8221;</p>
  <footer>Driftless Workforce Group</footer></blockquote>
</div></section>

<section class="section tint" aria-labelledby="start-h"><div class="wrap">
  <div class="section-head"><h2 id="start-h">If you're hiring, or looking to be hired, we'd like to help.</h2></div>
  <div class="choose">
    <article class="card"><span class="eyebrow">Employers</span><h3>Open positions</h3><p>Every request receives a follow-up call to discuss the position.</p><a class="btn" href="employers.html#request">Request Talent</a></article>
    <article class="card"><span class="eyebrow">Job Seekers</span><h3>Find your next job</h3><p>We contact candidates when a position matches their experience. There is never a fee.</p><a class="btn" href="job-seekers.html#apply">Submit Your Information</a></article>
  </div>
</div></section>'''


def employers():
    services = [
        ('Contingent', 'Single search', 'Recruiting for one position. The placement fee is due only after your new employee starts.',
         'Ideal for maintenance technicians, shift leads and warehouse supervisors.', False),
        ('Engaged', 'Priority search', 'For positions that have been open for an extended period. An initial engagement fee secures priority recruiting and is credited toward the placement fee.',
         'Ideal for CNC machinists, industrial maintenance and plant management.', True),
        ('Ongoing', 'Recruiting retainer', 'A flat monthly fee for continuous recruiting across multiple positions, including sourcing, screening, scheduling and reporting.',
         'Ideal for steady hiring, new shifts and expansions. <a href="retainer.html">Retainer details</a>', False),
    ]
    sv = ''.join(f'<article class="card service{" featured" if feat else ""}"><span class="tag">{E(tag)}</span><h3>{E(t)}</h3><p>{E(d)}</p><p class="best">{b}</p></article>'
                 for tag, t, d, b, feat in services)
    faqs = [
        ('Do you provide temporary staffing?', 'No. We specialize in direct hire. Candidates we place are your employees from their first day, with no hourly markup or conversion fee.'),
        ('Who pays the fee?', 'The employer. There is never a cost to job seekers.'),
        ('Do you use a written agreement?', 'Yes. Fees, payment terms and the replacement guarantee are confirmed in writing before we present any candidates.'),
        ('How does the replacement guarantee work?', 'If a placement does not work out within the guarantee period, we recruit a replacement at no additional charge. The guarantee period is specified in your agreement.'),
        ('What area do you serve?', 'La Crosse, Onalaska, Holmen, West Salem, Sparta, Tomah, Viroqua, Westby, Coon Valley and the surrounding Coulee Region.'),
        ('What is the difference between a single search and a retainer?', 'A single search fills one position, and the fee is due when the hire starts. A retainer covers ongoing recruiting for multiple positions for a flat monthly fee.'),
    ]
    fq = ''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in faqs)
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">Employers</span>
  <h1>Recruiting that understands your floor, not just your job posting.</h1>
  <p class="lede">Driftless Workforce Group recruits maintenance technicians, machinists, welders, production and warehouse staff, and janitorial crews for employers across the Coulee Region. Every candidate is screened before you receive a resume.</p>
  <div class="btn-row" style="margin-top:24px"><a class="btn" href="#request">Request Talent</a><a class="btn secondary" href="report.html">Hiring Report</a></div>
</div></section>

<section class="section" aria-labelledby="svc-h"><div class="wrap">
  <div class="section-head"><h2 id="svc-h">Services</h2>
  <p class="lede">All placements are direct hire. Fees are quoted after an initial consultation and confirmed in a written agreement.</p></div>
  <div class="grid three">{sv}</div>
</div></section>

<section class="section tint" aria-labelledby="proc-h"><div class="wrap">
  <div class="section-head"><h2 id="proc-h">How it works</h2></div>
  {steps_employer()}
</div></section>

<section class="section" aria-labelledby="get-h"><div class="wrap">
  <div class="grid two">
    <div><h2 id="get-h">What's included</h2>
    <ul class="ticks">
      <li>Candidates interviewed by our team</li>
      <li>Skills and certifications verified against your requirements</li>
      <li>Reference checks before an offer</li>
      <li>Pay and scheduling guidance based on local market data</li>
      <li>Regular progress updates</li>
      <li>Replacement guarantee on every placement</li>
    </ul></div>
    <div><h2>Positions we fill</h2>
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
  <div class="section-head"><h2 id="faq-h">Frequently asked questions</h2></div>
  <div class="faq">{fq}</div>
</div></section>

<section class="section form-section" id="request" aria-labelledby="req-h"><div class="wrap form-layout">
  <div><h2 id="req-h">Request talent</h2>
    <p class="lede">Every request receives a follow-up call to discuss the position, schedule and pay.</p>
    {contact_line()}
  </div>
  <div>{form_html("employer")}</div>
</div></section>'''


def retainer():
    inc = [('clipboard', 'Intake and job profiles', 'Requirements for each position, defined with your hiring managers.'),
           ('list', 'Job postings', 'Postings with pay, schedule and shift details for each position.'),
           ('route', 'Local sourcing', 'Job boards, referrals, technical colleges and candidates who are not actively searching.'),
           ('search', 'Candidate screening', 'Phone screens, skills checks and reference checks.'),
           ('boxes', 'Candidate pipeline', 'Pre-screened candidates for positions you fill on a recurring basis.'),
           ('chart', 'Reporting', 'Weekly status updates and a monthly local pay report.')]
    cards = ''.join(f'<article class="card"><div class="icon">{I[ic]}</div><h3>{E(t)}</h3><p>{E(d)}</p></article>' for ic, t, d in inc)
    rows = [('Fee structure', 'Markup on every hour worked', 'Fee per hire', 'Flat monthly fee'),
            ('Employer of record', 'The agency, until conversion', 'Your company', 'Your company'),
            ('Cost as hiring grows', 'Increases with hours worked', 'Increases with each hire', 'Fixed, so cost per hire decreases'),
            ('Best suited for', 'Short-term demand', 'A single hard-to-fill role', 'Continuous hiring')]
    trs = ''.join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td><td>{E(c)}</td><td><strong>{E(d)}</strong></td></tr>' for a, b, c, d in rows)
    weeks = [('Week 1', 'Site visit, meetings with hiring managers and job profiles for each position.'),
             ('Week 2', 'Job postings published and candidate sourcing under way.'),
             ('Weeks 3 to 4', 'First screened candidates presented for interviews.'),
             ('Day 30', 'First monthly report on the candidate pipeline, hires and local pay rates.')]
    wk = '<ol class="steps plain">' + ''.join(f'<li><span class="eyebrow" style="color:var(--river)">{E(a)}</span><p>{E(b)}</p></li>' for a, b in weeks) + '</ol>'
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">Recruiting Retainer</span>
  <h1>Ongoing recruiting for a flat monthly fee.</h1>
  <p class="lede">For manufacturers and warehouses with continuous hiring needs. We work as an extension of your HR team, and every hire is employed directly by you.</p>
  <div class="btn-row" style="margin-top:24px"><a class="btn" href="employers.html#request">Request a Consultation</a><a class="btn secondary" href="report.html">Hiring Report</a></div>
</div></section>

<section class="section" aria-labelledby="why-r-h"><div class="wrap">
  <div class="section-head"><h2 id="why-r-h">Regional hiring conditions</h2></div>
  <div class="stats">
    <div class="stat"><b>172&#8211;196</b><span>Days open for the six longest-listed plant postings near La Crosse, October 2026</span></div>
    <div class="stat"><b>39 days</b><span>National median time to fill a non-executive position</span></div>
    <div class="stat"><b>+25%</b><span>Change in U.S. manufacturing job openings, August 2025 to August 2026</span></div>
  </div>
  <p class="stats-note">Sources: Job Center of Wisconsin; SHRM Recruiting Benchmarking, 2026; U.S. Bureau of Labor Statistics, Job Openings and Labor Turnover Survey.</p>
</div></section>

<section class="section tint" aria-labelledby="inc-h"><div class="wrap">
  <div class="section-head"><h2 id="inc-h">What's included</h2></div>
  <div class="grid three">{cards}</div>
  <p style="margin-top:24px">All placements include a replacement guarantee. Fees and terms are confirmed in writing before work begins.</p>
</div></section>

<section class="section" aria-labelledby="cmp-h"><div class="wrap">
  <div class="section-head"><h2 id="cmp-h">Comparison of options</h2></div>
  <div class="table-scroll"><table><thead><tr><th scope="col"><span class="hp">Category</span></th><th scope="col">Temporary staffing</th><th scope="col">Single search</th><th scope="col">Driftless retainer</th></tr></thead>
  <tbody>{trs}</tbody></table></div>
  <p class="small muted" style="margin-top:12px">Driftless Workforce Group offers single searches and retainers. We do not provide temporary staffing.</p>
</div></section>

<section class="section tint" aria-labelledby="first-h"><div class="wrap">
  <div class="section-head"><h2 id="first-h">The first 30 days</h2></div>
  {wk}
</div></section>

<section class="section" aria-labelledby="fit-h"><div class="wrap">
  <div class="grid two">
    <div><h2 id="fit-h">Who it's for</h2>
    <ul class="ticks"><li>Employers with monthly openings in production, maintenance, warehouse or janitorial</li><li>Companies adding a shift, a production line or a new facility</li><li>Organizations with a small HR team</li><li>Employers with positions open 90 days or longer</li></ul></div>
    <div class="card"><h3>Pricing</h3><p>The monthly fee depends on the number of positions and how difficult they are to fill. A quote is provided after an initial consultation.</p>
    <a class="btn" href="employers.html#request">Request a Consultation</a></div>
  </div>
</div></section>'''


def job_seekers():
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">Job Seekers</span>
  <h1>Manufacturing, warehouse and maintenance jobs close to home.</h1>
  <p class="lede">Driftless Workforce Group recruits for employers across the Coulee Region that are hiring maintenance, machining, production, warehouse and janitorial staff. Our service is always free for job seekers.</p>
  <div class="btn-row" style="margin-top:24px"><a class="btn" href="#apply">Submit Your Information</a></div>
</div></section>

<section class="section" aria-labelledby="exp-h"><div class="wrap">
  <div class="section-head"><h2 id="exp-h">How it works</h2></div>
  <ol class="steps">
    <li><h3>Your information</h3><p>Your experience, the type of work you want and your shift availability.</p></li>
    <li><h3>Initial conversation</h3><p>We call to learn about your skills, pay expectations and goals.</p></li>
    <li><h3>Matching</h3><p>We present you only for positions that fit, and only with your permission.</p></li>
    <li><h3>Hiring</h3><p>You are hired directly by the employer, with their pay and benefits.</p></li>
  </ol>
</div></section>

<section class="section tint" aria-labelledby="why-js-h"><div class="wrap">
  <h2 id="why-js-h" class="hp">Why work with us</h2>
  <div class="grid three">
    <article class="card"><div class="icon">{I["dollar"]}</div><h3>No cost to you</h3><p>Employers pay our fee. Job seekers never pay to work with us.</p></article>
    <article class="card"><div class="icon">{I["route"]}</div><h3>Local positions</h3><p>Openings in La Crosse, Onalaska, Holmen, Sparta, Tomah, Viroqua and nearby communities.</p></article>
    <article class="card"><div class="icon">{I["list"]}</div><h3>Entry-level openings</h3><p>Some employers train candidates who are new to the trade.</p></article>
  </div>
</div></section>

<section class="section form-section" id="apply" aria-labelledby="apply-h"><div class="wrap form-layout">
  <div><h2 id="apply-h">Submit your information</h2>
    <p class="lede">Detailed information helps us match you with the right position.</p>
    {contact_line()}
    <p class="small muted">Driftless Workforce Group is an equal opportunity recruiter. All candidates are considered without regard to race, color, religion, sex, national origin, age, disability, veteran status or any other status protected by law.</p>
  </div>
  <div>{form_html("candidate")}</div>
</div></section>'''


def report():
    rows = ''.join(f'<tr><td>{E(r)}</td><td>{E(s) if s else "&#8212;"}</td><td>{E(d)}</td><td class="n">{n}</td></tr>' for r, s, d, n in OPEN_ROLES)
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">Quarterly Report &middot; October 2026</span>
  <h1>Coulee Region Industrial Hiring Report</h1>
  <p class="lede">Hiring activity, hard-to-fill positions and pay rates for manufacturing, warehouse and maintenance jobs within 25 miles of La Crosse.</p>
</div></section>

<section class="section" aria-labelledby="glance-h"><div class="wrap">
  <div class="section-head"><h2 id="glance-h">Summary</h2></div>
  <div class="stats">
    <div class="stat"><b>500+</b><span>Open job postings within 25 miles of La Crosse, October 12, 2026</span></div>
    <div class="stat"><b>3.0%</b><span>Unemployment rate, La Crosse&#8211;Onalaska metro, August 2026 (preliminary)</span></div>
    <div class="stat"><b>172&#8211;196</b><span>Days open for the six longest-listed plant postings</span></div>
  </div>
</div></section>

<section class="section tint" aria-labelledby="find-h"><div class="wrap">
  <div class="section-head"><h2 id="find-h">Key findings</h2></div>
  <div class="grid two findings">
    <div class="finding"><h3>Skilled trades take the longest to fill</h3><p>Of 135 postings reviewed, 10 had been open more than 90 days. The six longest-open were maintenance, CNC machining, welding and material handling positions.</p></div>
    <div class="finding"><h3>Trade wages are near the national average</h3><p>The metro's average wage across all occupations is 10% below the U.S. average. Installation, maintenance and repair occupations average $30.27 an hour locally, compared with $30.44 nationally.</p></div>
    <div class="finding"><h3>Employers are hiring trainees</h3><p>Six machining postings were open to entry-level candidates.</p></div>
    <div class="finding"><h3>Off-shift schedules are common</h3><p>Open postings include 2nd-shift, 3rd-shift, weekend and rotating 12-hour schedules.</p></div>
  </div>
  <figure class="figure" style="margin-top:32px"><h3 class="fig-title">Job postings by keyword</h3>
    <div class="chart">{chart_postings()}</div>
    <figcaption>Source: Job Center of Wisconsin, October 12, 2026.</figcaption></figure>
</div></section>

<section class="section" aria-labelledby="pay-h"><div class="wrap">
  <div class="section-head"><h2 id="pay-h">Pay by occupation</h2>
  <p class="lede">Median hourly wages, La Crosse&#8211;Onalaska metro.</p></div>
  <figure class="figure"><div class="chart">{chart_wages()}</div>
  <figcaption>Source: U.S. Bureau of Labor Statistics, Occupational Employment and Wage Statistics, May 2025.</figcaption></figure>
</div></section>

<section class="section tint" aria-labelledby="open-h"><div class="wrap">
  <div class="section-head"><h2 id="open-h">Longest-open postings</h2></div>
  <div class="table-scroll"><table><caption class="hp">Longest-open postings, October 12, 2026</caption>
  <thead><tr><th scope="col">Position</th><th scope="col">Shift</th><th scope="col">Posted</th><th scope="col" class="n">Days open</th></tr></thead>
  <tbody>{rows}</tbody></table></div>
  <p class="small muted" style="margin-top:12px">Source: Job Center of Wisconsin, October 12, 2026.</p>
</div></section>

<section class="section" aria-labelledby="src-h"><div class="wrap">
  <div class="section-head"><h2 id="src-h">Sources</h2></div>
  <ul class="sources">
    <li><a href="https://jobcenterofwisconsin.com" rel="noopener">Job Center of Wisconsin</a>, Wisconsin Department of Workforce Development. Job postings within 25 miles of ZIP code 54601, retrieved October 12, 2026.</li>
    <li><a href="https://www.bls.gov/regions/midwest/news-release/2026/occupationalemploymentandwages_lacrosse_20260803.htm" rel="noopener">U.S. Bureau of Labor Statistics, Occupational Employment and Wages in La Crosse&#8211;Onalaska, May 2025</a>. Released August 3, 2026.</li>
    <li><a href="https://www.bls.gov/eag/eag.wi_lacrosse_msa.htm" rel="noopener">U.S. Bureau of Labor Statistics, Economy at a Glance: La Crosse&#8211;Onalaska, WI-MN</a>. August 2026, preliminary.</li>
  </ul>
</div></section>

<section class="section tint form-section" id="subscribe" aria-labelledby="sub-h"><div class="wrap form-layout">
  <div><h2 id="sub-h">Subscribe</h2>
    <p class="lede">The Coulee Region Industrial Hiring Report is published quarterly and is free to employers.</p></div>
  <div>{form_html("report")}</div>
</div></section>'''


def contact():
    phone = (f'<div class="aside-item"><div class="icon">{I["phone"]}</div><div><h3>Phone</h3><p><a href="tel:+1{"".join(c for c in SITE["phone"] if c.isdigit())}">{E(SITE["phone"])}</a> (call or text)</p></div></div>'
             if SITE['phone'] else '')
    email = (f'<div class="aside-item"><div class="icon">{I["mail"]}</div><div><h3>Email</h3><p><a href="mailto:{E(SITE["email"])}">{E(SITE["email"])}</a></p></div></div>'
             if SITE['email'] else '')
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">Contact</span>
  <h1>Contact us</h1>
  <p class="lede">We're local, we're responsive, and there's no cost to start a conversation.</p>
</div></section>
<section class="section form-section" aria-labelledby="c-h"><div class="wrap form-layout">
  <div><h2 id="c-h">Get in touch</h2>
    <div class="aside-list">
      <div class="aside-item"><div class="icon">{I["pin"]}</div><div><h3>Location</h3><p>{E(SITE["city"])}, serving the Coulee Region</p></div></div>
      {phone}{email}
      <div class="aside-item"><div class="icon">{I["factory"]}</div><div><h3>Employers</h3><p>Open positions can be submitted through the <a href="employers.html#request">talent request form</a>.</p></div></div>
      <div class="aside-item"><div class="icon">{I["clipboard"]}</div><div><h3>Job seekers</h3><p>Candidates can <a href="job-seekers.html#apply">submit their information</a> for current and future openings.</p></div></div>
    </div>
  </div>
  <div>{form_html("question")}</div>
</div></section>'''


def about():
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">About</span>
  <h1>Built here. For here.</h1>
  <p class="lede">Driftless Workforce Group is a recruiting firm based in La Crosse, Wisconsin. Most recruiters serving this region work from outside it. We work from here.</p>
</div></section>
<section class="section"><div class="wrap">
  <div class="grid three">
    <article class="card"><div class="icon">{I["wrench"]}</div><h3>Our background</h3><p>We came to recruiting from the worker's side, after years in production, line and kitchen jobs. We understand the work, so we can judge who will show up, fit in and stay.</p></article>
    <article class="card"><div class="icon">{I["pin"]}</div><h3>Our region</h3><p>The La Crosse area and the Driftless are home, not a market. National agencies place names off a screen. We place neighbors.</p></article>
    <article class="card"><div class="icon">{I["shield"]}</div><h3>Our commitment</h3><p>Our service is employer-paid and free for job seekers. Every placement includes a guarantee, and we focus on long-term relationships with employers and candidates.</p></article>
  </div>
</div></section>
<section class="section tint"><div class="wrap">
  <div class="grid two" style="align-items:center">
    <div><span class="eyebrow">Founder</span><h2>Casey Guy</h2><p class="lede">Founder, Driftless Workforce Group LLC</p>
    {contact_line()}</div>
    <div class="choose stack">
      <article class="card"><span class="eyebrow">Employers</span><h3>Open positions</h3><a class="btn" href="employers.html#request">Request Talent</a></article>
      <article class="card"><span class="eyebrow">Job Seekers</span><h3>Find your next job</h3><a class="btn" href="job-seekers.html#apply">Submit Your Information</a></article>
    </div>
  </div>
</div></section>'''


def privacy():
    return f'''
<section class="page-hero"><div class="wrap"><span class="eyebrow">Privacy Policy</span><h1>Privacy policy</h1>
<p class="lede">Last updated October 2026</p></div></section>
<section class="section"><div class="wrap prose">
<p>This policy applies to Driftless Workforce Group LLC, a Wisconsin limited liability company based in La Crosse, and to information submitted through this website.</p>
<h2>Information we collect</h2>
<p>We collect the information you submit through our forms: your name and contact details, information about an open position or the work you are seeking, and any resume you upload.</p>
<h2>How we use your information</h2>
<p>We use your information to respond to inquiries, recruit for positions employers ask us to fill, match job seekers with those positions, and send the hiring report to subscribers.</p>
<h2>How we share your information</h2>
<p>We do not sell personal information. A job seeker's resume or personal details are shared with an employer only with that person's permission.</p>
<h2>How we store your information</h2>
<p>Form submissions and resumes are stored with our website hosting provider in an account accessible only to Driftless Workforce Group LLC.</p>
<h2>Equal opportunity</h2>
<p>All candidates are considered without regard to race, color, religion, sex, national origin, age, disability, veteran status or any other status protected by law.</p>
<h2>Your choices</h2>
<p>You may request that we update or delete your information, or stop contacting you, at any time through our <a href="contact.html">contact page</a>.</p>
</div></section>'''


def not_found():
    return '''<section class="page-hero"><div class="wrap"><span class="eyebrow">404</span><h1>Page not found</h1>
<p class="lede">The page you requested does not exist or has moved.</p>
<div class="btn-row" style="margin-top:24px"><a class="btn" href="./">Home</a><a class="btn secondary" href="employers.html">Employers</a><a class="btn secondary" href="job-seekers.html">Job Seekers</a></div></div></section>'''


PAGES = [
    ('index.html', 'Driftless Workforce Group | Direct-Hire Recruiting in La Crosse, WI',
     'Direct-hire recruiting for manufacturing, warehouse, maintenance and janitorial positions in La Crosse and the Coulee Region.', home, ''),
    ('retainer.html', 'Recruiting Retainer | Driftless Workforce Group',
     'Ongoing recruiting for manufacturers and warehouses for a flat monthly fee. Every hire is employed directly by you.', retainer, 'retainer.html'),
    ('employers.html', 'Employers | Driftless Workforce Group',
     'Direct-hire recruiting for maintenance technicians, machinists, welders, production, warehouse and janitorial positions.', employers, 'employers.html'),
    ('job-seekers.html', 'Job Seekers | Driftless Workforce Group',
     'Manufacturing, warehouse, maintenance and janitorial jobs in the La Crosse area. Always free for job seekers.', job_seekers, 'job-seekers.html'),
    ('report.html', 'Coulee Region Industrial Hiring Report, October 2026 | Driftless Workforce Group',
     'Hiring activity, hard-to-fill positions and pay rates within 25 miles of La Crosse. Published quarterly.', report, 'report.html'),
    ('contact.html', 'Contact | Driftless Workforce Group', 'Contact Driftless Workforce Group in La Crosse, Wisconsin.', contact, 'contact.html'),
    ('about.html', 'About | Driftless Workforce Group', 'Driftless Workforce Group is a direct-hire recruiting firm based in La Crosse, Wisconsin.', about, 'about.html'),
    ('privacy.html', 'Privacy Policy | Driftless Workforce Group', 'Privacy policy for Driftless Workforce Group LLC.', privacy, ''),
    ('404.html', 'Page Not Found | Driftless Workforce Group', 'Page not found.', not_found, ''),
]



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



import re
def smart(markup):
    """Typographic apostrophes in page text and attribute values (scripts and styles are left as is)."""
    out, skip = [], False
    for part in re.split(r'(<[^>]+>)', markup):
        if part.startswith('<'):
            low = part[:8].lower()
            if low.startswith(('<script', '<style')): skip = True
            elif low.startswith(('</script', '</style')): skip = False
            out.append(re.sub(r"(?<=[A-Za-z])&#x27;(?=[A-Za-z])", "’", part))
        else:
            out.append(part if skip else re.sub(r"(?<=[A-Za-z])(?:'|&#x27;)(?=[A-Za-z])", "’", part))
    return ''.join(out)

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
        main_html = smart(fn())
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
