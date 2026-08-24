const demoSignals=[
 {employer:'Great Lakes Cheese',kind:'volume_increase',severity:'high',message:'Openings increased from 3 to 8 (167% increase)',metric:'+5 / 167%'},
 {employer:'Trane Technologies',kind:'leadership_new',severity:'high',message:'New leadership opening detected',metric:'Leadership'}
];
async function loadSignals(){let signals=demoSignals;try{const r=await fetch('../data/signals.json',{cache:'no-store'});if(r.ok){const d=await r.json();if(Array.isArray(d))signals=d;else if(Array.isArray(d.signals))signals=d.signals}}catch(_){}const root=document.getElementById('alerts');if(!root)return;root.innerHTML=signals.length?signals.map(s=>`<article class="alert ${s.severity}"><div><div class="alert-kicker">${String(s.severity).toUpperCase()} SIGNAL · ${String(s.kind).replaceAll('_',' ')}</div><strong>${escapeHtml(s.employer)}</strong><p>${escapeHtml(s.message)}</p></div><span>${escapeHtml(s.metric||'')}</span></article>`).join(''):'<div class="empty">No new hiring signals.</div>'}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}loadSignals();
