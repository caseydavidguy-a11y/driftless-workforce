// Small client-side pipeline board for V1. Data is intentionally local/read-only until persistence is connected.
const demo=[
 {employer:'Great Lakes Cheese',score:73,priority:'Pursue',status:'NEW',next_action:'Research HR/Talent Acquisition or plant leadership'},
 {employer:'Trane Technologies',score:68,priority:'Monitor',status:'NEW',next_action:'Research HR/Talent Acquisition or operations leadership'},
 {employer:'Wis-Pak',score:48,priority:'Monitor',status:'NEW',next_action:'Monitor hiring activity'}
];
const stages=['NEW','RESEARCHING','CONTACT IDENTIFIED','CONTACTED','ENGAGED','CLIENT'];
const key='driftless_pipeline_v1';
let rows=JSON.parse(localStorage.getItem(key)||'null')||demo;
function save(){localStorage.setItem(key,JSON.stringify(rows));}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
function move(name,status){const r=rows.find(x=>x.employer===name);if(r){r.status=status;save();render();}}
function render(){const el=document.getElementById('board');el.innerHTML=stages.map(stage=>{const cards=rows.filter(r=>(r.status||'NEW')===stage).map(r=>`<article class="pipeline-card"><strong>${esc(r.employer)}</strong><div class="meta">${esc(r.priority)} · ${r.score}/100</div><div class="action">${esc(r.next_action||'Research decision-maker')}</div><select aria-label="Move ${esc(r.employer)}" onchange="move(${JSON.stringify(r.employer)},this.value)">${stages.map(s=>`<option ${s===stage?'selected':''}>${s}</option>`).join('')}</select></article>`).join('');return `<section class="lane"><div class="lane-head"><h2>${stage}</h2><span>${rows.filter(r=>(r.status||'NEW')===stage).length}</span></div>${cards||'<div class="empty-lane">No prospects</div>'}</section>`}).join('')}
render();
