"""Hand-drawn SVG graphics for the Driftless site. Objects and landscape only, no people."""

LOGO = ('<svg viewBox="0 0 40 40" aria-hidden="true" focusable="false">'
        '<rect width="40" height="40" rx="10" fill="#1f5f6b"/>'
        '<path d="M5 28 L12.5 17.5 L17 22 L23.5 12 L35 28 Z" fill="#f7f2e7"/>'
        '<path d="M5 31.5 C12 28.5 19 34 26 31 C29 29.8 32 29.6 35 30.4" fill="none" stroke="#d99a1e" stroke-width="2.6" stroke-linecap="round"/>'
        '</svg>')

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E"
           "%3Crect width='40' height='40' rx='9' fill='%231f5f6b'/%3E"
           "%3Ctext x='20' y='29' text-anchor='middle' font-family='Georgia,serif' font-size='26' font-weight='700' fill='%23f7f2e7'%3ED%3C/text%3E"
           "%3C/svg%3E")

def icon(paths):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + paths + '</svg>')

I = {
    'factory': icon('<path d="M3 20.5V11l5 3.2V11l5 3.2V11l5 3.2V4.5h3v16z"/><path d="M6.5 17.5h2M11 17.5h2M15.5 17.5h2"/>'),
    'boxes': icon('<rect x="4" y="10.5" width="7.2" height="6.5" rx=".8"/><rect x="12.8" y="10.5" width="7.2" height="6.5" rx=".8"/>'
                  '<rect x="8.4" y="3.5" width="7.2" height="6.5" rx=".8"/><path d="M3 17h18M3 20.5h18M5 17v3.5M12 17v3.5M19 17v3.5"/>'),
    'wrench': icon('<path d="M14.6 4.1a4.7 4.7 0 0 0-5 6.4l-6 6a1.9 1.9 0 0 0 2.7 2.7l6-6a4.7 4.7 0 0 0 6.4-5l-2.7 2.7-2.6-.4-.4-2.6z"/>'),
    'bucket': icon('<path d="M5 10.5h14l-1.6 9.5H6.6z"/><path d="M7.4 10.5a4.6 4.6 0 0 1 9.2 0"/><path d="M19.5 3v3.4M17.8 4.7h3.4M4.5 4v2.4M3.3 5.2h2.4"/>'),
    'clipboard': icon('<rect x="5" y="4.5" width="14" height="16" rx="2"/><path d="M9 4.5V3.4h6v1.1"/><path d="M8.5 10h7M8.5 13.5h7M8.5 17h4"/>'),
    'search': icon('<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/>'),
    'list': icon('<path d="M9.5 7h10.5M9.5 12h10.5M9.5 17h10.5"/><path d="M4 7l1.3 1.3L7.5 6M4 12l1.3 1.3L7.5 11M4 17l1.3 1.3L7.5 16"/>'),
    'shield': icon('<path d="M12 3l7.5 3v5.5c0 4.6-3.2 8-7.5 9.5-4.3-1.5-7.5-4.9-7.5-9.5V6z"/><path d="M8.6 12l2.4 2.4 4.5-4.7"/>'),
    'pin': icon('<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>'),
    'chart': icon('<path d="M4 4v16h16"/><path d="M8.5 16v-4M12.5 16V8M16.5 16v-6"/>'),
    'check': icon('<circle cx="12" cy="12" r="9"/><path d="M8 12.3l2.7 2.7L16 9.5"/>'),
    'bigcheck': icon('<path d="M5 12.5l4.5 4.5L19 7.5"/>'),
    'dollar': icon('<circle cx="12" cy="12" r="9"/><path d="M14.8 9.4c-.5-1-1.5-1.5-2.8-1.5-1.6 0-2.8.8-2.8 2.1 0 3 5.8 1.6 5.8 4.4 0 1.3-1.3 2.2-3 2.2-1.4 0-2.5-.6-3-1.7M12 6.4v1.5M12 16.6v1.5"/>'),
    'clock': icon('<circle cx="12" cy="12" r="9"/><path d="M12 7.2V12l3.2 2"/>'),
    'mail': icon('<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="M3.6 7l8.4 6 8.4-6"/>'),
    'lock': icon('<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>'),
    'route': icon('<circle cx="6" cy="18" r="2.2"/><circle cx="18" cy="6" r="2.2"/><path d="M8 18h6.5a3.5 3.5 0 0 0 0-7h-5a3.5 3.5 0 0 1 0-7H16"/>'),
    'calendar': icon('<rect x="4" y="5.5" width="16" height="15" rx="2"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/>'),
    'phone': icon('<path d="M6.6 3.5h2.8l1.4 4-2 1.3a11.5 11.5 0 0 0 6.4 6.4l1.3-2 4 1.4v2.8a2 2 0 0 1-2.1 2A16.6 16.6 0 0 1 4.6 5.6a2 2 0 0 1 2-2.1z"/>'),
    'menu': icon('<path d="M4 7h16M4 12h16M4 17h16"/>'),
    'arrow': icon('<path d="M5 12h14M13 6l6 6-6 6"/>'),
}

HERO = '''<svg viewBox="0 0 560 420" role="img" aria-labelledby="hero-art-t">
<title id="hero-art-t">Illustration: river bluffs above a plant with a sawtooth roof, a water tower, a warehouse with loading doors, a rail line and the Mississippi</title>
<rect width="560" height="420" fill="var(--paper-2)"/>
<circle cx="430" cy="104" r="48" fill="var(--lamp)" opacity=".28"/>
<path d="M0 226 C40 198 72 168 112 172 C152 176 168 136 212 132 C252 128 272 162 312 158 C352 154 382 118 432 122 C482 126 520 160 560 166 L560 420 L0 420Z" fill="var(--bluff-1)"/>
<g fill="var(--moss)" opacity=".55">
  <path d="M96 182 l6 -14 6 14z"/><path d="M110 178 l5 -12 5 12z"/><path d="M200 140 l6 -15 6 15z"/><path d="M214 138 l5 -12 5 12z"/>
  <path d="M420 128 l6 -15 6 15z"/><path d="M434 130 l5 -12 5 12z"/><path d="M300 162 l5 -12 5 12z"/>
</g>
<path d="M0 268 C50 248 90 214 140 220 C180 226 202 198 242 203 C292 210 322 242 372 236 C422 230 462 204 512 212 C532 216 548 226 560 230 L560 420 L0 420Z" fill="var(--bluff-2)"/>
<path d="M0 300 H560 V420 H0Z" fill="var(--paper-3)"/>
<g fill="#4a3a28">
  <rect x="40" y="250" width="104" height="50"/>
  <path d="M36 252 L92 236 L148 252Z"/>
</g>
<g fill="var(--paper-2)"><rect x="52" y="270" width="18" height="30"/><rect x="78" y="270" width="18" height="30"/><rect x="104" y="270" width="18" height="30"/></g>
<g fill="#3a2c1c">
  <path d="M156 300 V236 L156 212 L190 236 V212 L224 236 V212 L258 236 V212 L292 236 V212 L326 236 V300Z"/>
  <rect x="304" y="156" width="14" height="82"/>
</g>
<rect x="304" y="164" width="14" height="6" fill="var(--brick)"/>
<g fill="var(--lamp)" opacity=".85">
  <rect x="168" y="254" width="12" height="9"/><rect x="190" y="254" width="12" height="9"/><rect x="212" y="254" width="12" height="9"/>
  <rect x="234" y="254" width="12" height="9"/><rect x="256" y="254" width="12" height="9"/><rect x="278" y="254" width="12" height="9"/><rect x="300" y="254" width="12" height="9"/>
</g>
<g stroke="#3a2c1c" stroke-width="4" stroke-linecap="round"><path d="M404 300 L414 242"/><path d="M444 300 L434 242"/><path d="M408 276 H440"/></g>
<rect x="400" y="212" width="48" height="32" rx="10" fill="#3a2c1c"/>
<path d="M398 215 L424 198 L450 215Z" fill="#3a2c1c"/>
<g stroke="#3a2c1c" stroke-width="2.5"><path d="M0 312 H560"/></g>
<g stroke="#3a2c1c" stroke-width="2" opacity=".55"><path d="M14 308v8M44 308v8M74 308v8M104 308v8M134 308v8M164 308v8M194 308v8M224 308v8M254 308v8M284 308v8M314 308v8M344 308v8M374 308v8M404 308v8M434 308v8M464 308v8M494 308v8M524 308v8M554 308v8"/></g>
<path d="M0 352 C120 332 220 374 340 354 C430 339 500 346 560 338 L560 420 L0 420Z" fill="var(--river)"/>
<g fill="none" stroke="#e2edef" stroke-width="2" stroke-linecap="round" opacity=".55">
  <path d="M60 378 C90 372 120 374 150 380"/><path d="M250 392 C290 384 330 386 370 390"/><path d="M430 372 C460 366 490 366 520 370"/>
</g>
</svg>'''

REPORT_ART = '''<svg viewBox="0 0 320 220" aria-hidden="true" focusable="false">
<rect x="30" y="20" width="230" height="180" rx="10" fill="#efe6d2"/>
<rect x="46" y="38" width="120" height="10" rx="3" fill="#a8956d"/>
<rect x="46" y="56" width="80" height="7" rx="3" fill="#cbb98f"/>
<g fill="#cbb98f"><rect x="58" y="130" width="22" height="50"/><rect x="92" y="112" width="22" height="68"/><rect x="160" y="140" width="22" height="40"/><rect x="194" y="150" width="22" height="30"/></g>
<rect x="126" y="86" width="22" height="94" fill="#1f5f6b"/>
<path d="M46 180 H246" stroke="#5c5040" stroke-width="2"/>
<rect x="210" y="8" width="84" height="84" rx="42" fill="#d99a1e" opacity=".9"/>
<text x="252" y="48" text-anchor="middle" font-family="Fraunces, Georgia, serif" font-weight="700" font-size="22" fill="#241c13">Q4</text>
<text x="252" y="68" text-anchor="middle" font-family="IBM Plex Sans, Arial, sans-serif" font-size="12" font-weight="600" fill="#241c13">2026</text>
</svg>'''
