(()=>{'use strict';
/* ============ core ============ */
const S={me:null,schema:null,refs:{},dark:localStorage.theme==='dark'||(!localStorage.theme&&matchMedia('(prefers-color-scheme: dark)').matches),install:null};
const $=(s,e=document)=>e.querySelector(s);
const add=(e,k)=>{for(const c of k.flat(Infinity)){if(c==null||c===false)continue;e.append(c instanceof Node?c:document.createTextNode(String(c)))}};
function h(t,p,...k){const [t0,...cl]=t.split('.');const [tag,id]=t0.split('#');const e=document.createElement(tag||'div');if(id)e.id=id;if(cl.length)e.className=cl.join(' ');
 if(p&&(typeof p!=='object'||p instanceof Node||Array.isArray(p))){k.unshift(p);p=null}
 for(const [a,v] of Object.entries(p||{})){if(v==null||v===false)continue;
  if(a.startsWith('on'))e.addEventListener(a.slice(2),v);else if(a==='class')e.className+=' '+v;else if(a==='html')e.innerHTML=v;
  else if(a==='value'||a==='checked'||a==='disabled'||a==='selected')e[a]=v;else e.setAttribute(a,v===true?'':v)}
 add(e,k);return e}
const P={home:'<path d="M3 11l9-8 9 8"/><path d="M5 10v10h5v-6h4v6h5V10"/>',inbox:'<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.5 5h13l3.5 7v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-6z"/>',users:'<circle cx="9" cy="8" r="4"/><path d="M2 21v-1a6 6 0 0 1 6-6h2a6 6 0 0 1 6 6v1"/><path d="M17 4a4 4 0 0 1 0 8"/><path d="M22 21v-1a5 5 0 0 0-4-5"/>',target:'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',briefcase:'<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/>',file:'<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/>',check:'<path d="M9 11l3 3 8-8"/><path d="M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h9"/>',message:'<path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',megaphone:'<path d="M3 11v2a1 1 0 0 0 1 1h3l8 5V5L7 10H4a1 1 0 0 0-1 1z"/><path d="M19 8a5 5 0 0 1 0 8"/>',wallet:'<path d="M3 7a2 2 0 0 1 2-2h13v4"/><path d="M3 7v11a2 2 0 0 0 2 2h15V9H5a2 2 0 0 1-2-2z"/><circle cx="16.5" cy="14.5" r="1"/>',chart:'<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',sliders:'<path d="M4 6h10M18 6h2M4 12h2M10 12h10M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="8" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',card:'<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',shield:'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',plus:'<path d="M12 5v14M5 12h14"/>',menu:'<path d="M4 6h16M4 12h16M4 18h16"/>',x:'<path d="M6 6l12 12M18 6L6 18"/>',download:'<path d="M12 3v12M7 10l5 5 5-5"/><path d="M4 21h16"/>',logout:'<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5M21 12H9"/>',moon:'<path d="M21 13a9 9 0 1 1-10-10 7 7 0 0 0 10 10z"/>',board:'<rect x="3" y="3" width="5" height="18" rx="1"/><rect x="10" y="3" width="5" height="12" rx="1"/><rect x="17" y="3" width="4" height="8" rx="1"/>',list:'<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',print:'<path d="M6 9V3h12v6"/><rect x="3" y="9" width="18" height="9" rx="2"/><path d="M6 14h12v7H6z"/>',more:'<circle cx="5" cy="12" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/>',eye:'<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',tick:'<path d="M5 12l5 5 9-10"/>',search:'<circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/>'};
const ic=n=>h('span',{html:`<svg class="i" viewBox="0 0 24 24" aria-hidden="true">${P[n]||''}</svg>`,style:'display:inline-flex'});
const icH=n=>`<svg class="i" viewBox="0 0 24 24" aria-hidden="true">${P[n]||''}</svg>`;
async function api(m,u,b){
 const r=await fetch(u,{method:m,credentials:'same-origin',headers:{'X-Requested-With':'RITS',...(b?{'Content-Type':'application/json'}:{})},body:b?JSON.stringify(b):undefined});
 let d=null;try{d=await r.json()}catch(_){}
 if(!r.ok){const msg=(d&&(typeof d.detail==='string'?d.detail:Array.isArray(d.detail)?d.detail.map(x=>x.msg).join(', '):null))||'Something went wrong. Try again.';
  if(r.status===401&&S.me&&u!=='/api/me'){S.me=null;location.hash='#/login'}const e=new Error(msg);e.status=r.status;throw e}
 return d}
let tt;function toast(m,bad){document.querySelectorAll('.toast').forEach(x=>x.remove());const t=h('div.toast'+(bad?'.bad':''),{role:'status'},m);document.body.append(t);clearTimeout(tt);tt=setTimeout(()=>t.remove(),bad?5000:2600)}
const fail=e=>toast(e.message,1);
const fmtN=(n,d=0)=>n==null||n===''||isNaN(n)?'–':Number(n).toLocaleString('en-IN',{maximumFractionDigits:d,minimumFractionDigits:0});
const cur=()=>S.me.settings.currency_base;
const money=n=>n==null||n===''?'–':fmtN(n);
const MO=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const fmtD=v=>{if(!v)return '–';const d=new Date(String(v).slice(0,10)+'T00:00');return isNaN(d)?v:`${String(d.getDate()).padStart(2,'0')} ${MO[d.getMonth()]} ${d.getFullYear()}`};
const fmtDT=v=>v?fmtD(v)+' '+String(v).slice(11,16):'–';
const today=()=>{const d=new Date();return d.toISOString().slice(0,10)};
const nowLocal=()=>{const d=new Date();d.setMinutes(d.getMinutes()-d.getTimezoneOffset());return d.toISOString().slice(0,16)};
const OKS=new Set(['Qualified','Won','Paid','Done','Active','Green','Happy','On time','OK','Delivered','On track','Available','Completed','Approved','Free','Yes','active']);
const BADS=new Set(['Overdue','Red','Breached - respond now','Late','Over budget','Unpaid','Overloaded','At risk','Update overdue','Respond now','Lost','Churned','Blocked','Urgent','Not assigned','Resigned','Terminated','expired','suspended','rejected','Cancelled']);
const WRS=new Set(['Warm','Due today','Partial','Amber','Near limit','Busy','Due soon','No update yet','Neutral','Pending','No date set','High','Waiting on client','On hold','Onboarding','pending','trialing','Paused','On leave']);
const tone=v=>OKS.has(v)?'ok':BADS.has(v)?'bad':WRS.has(v)||/^Due in/.test(v)?'wr':(v==='Unqualified'||v==='Not scored'||v==='Closed'||v==='No due date'||v==='Free')?'n':'';
const chip=v=>v==null||v===''?'–':h('span.chip'+(tone(v)?'.'+tone(v):''),String(v));
const go=p=>{location.hash='#/'+p};
const ent=k=>S.schema.entities[k];
const can=(r,n='v')=>S.me&&S.me.perms[r]&&S.me.perms[r][n==='e'?'e':'v'];
const owner=()=>S.me.user.role==='owner';
const isoMonthLabel=m=>MO[+m.slice(5,7)-1]+' '+m.slice(2,4);
const lbl=(k,c)=>(S.refs[k]||{})[c]||c||'';

function modal(title,body,footer){
 const close=()=>mo.remove();
 const mo=h('div.mo',{onclick:e=>{if(e.target===mo)close()}},h('div.md',{role:'dialog','aria-modal':'true','aria-label':title},h('header',h('h2.grow',title),h('button.btn.g.ic',{onclick:close,'aria-label':'Close'},ic('x'))),h('div.bd',body),footer&&h('footer',footer)));
 document.body.append(mo);mo.close=close;return mo}
document.addEventListener('keydown',e=>{if(e.key==='Escape'){const m=[...document.querySelectorAll('.mo')].pop();if(m)m.remove()}});
function confirmBox(msg,okLabel='Delete'){return new Promise(res=>{const m=modal('Are you sure?',h('p',msg),[h('button.btn.d',{onclick:()=>{m.close();res(true)}},okLabel),h('button.btn',{onclick:()=>{m.close();res(false)}},'Cancel')])})}
const skeleton=()=>h('div',h('div.sk'),h('div.sk',{style:'height:180px'}),h('div.sk'));
const empty=(t,s)=>h('div.empty',h('span',{html:icH('inbox')}),h('h3',t),h('p',s||''));

/* ============ small components ============ */
const kpi=(l,v,s,t)=>h('div.kpi'+(t?'.'+t:''),h('div.l',l),h('div.v',v),s!=null&&h('div.s',s));
const kpis=(...k)=>h('div.kpis',k);
const card=(title,...body)=>h('div.card',title&&h('div.ch',h('h2',title)),body);
function barlist(items,fmt=v=>fmtN(v),toneFn){const mx=Math.max(1,...items.map(i=>i.v));return h('div',items.length?items.map(i=>h('div.brow',h('div.n',{title:i.n},i.n),h('div.bar'+(toneFn?'.'+toneFn(i):''),h('i',{style:`width:${Math.max(i.v?3:0,i.v/mx*100)}%`})),h('div.x',fmt(i.v)))):empty('Nothing yet'))}
function tbl(head,rows,o={}){const num=new Set(o.num||[]);return h('div.tw',h('table'+(o.rs?'.rs':''),h('thead',h('tr',head.map((x,i)=>h('th'+(num.has(i)?'.num':''),x)))),h('tbody',rows.map(r=>h('tr',{onclick:r.go?()=>go(r.go):r.click||null},r.c.map((c,i)=>h('td'+(num.has(i)?'.num':''),{'data-l':head[i]},c))))),o.foot&&h('tfoot',h('tr',o.foot.map((c,i)=>h('td'+(num.has(i)?'.num':''),c))))))}
function chart(ms,series){const W=720,H=190,L=4,bw=(W-L)/ms.length,g=bw*.74/series.length,mx=Math.max(1,...ms.flatMap(m=>series.map(s=>m[s.k]||0)));
 let s=`<svg viewBox="0 0 ${W} ${H+24}" width="100%" role="img" aria-label="Monthly chart">`;
 for(const f of [0,.5,1])s+=`<line x1="0" x2="${W}" y1="${H-f*H*.92}" y2="${H-f*H*.92}" stroke="currentColor" opacity=".12"/>`;
 ms.forEach((m,i)=>{series.forEach((se,j)=>{const v=m[se.k]||0,bh=v/mx*H*.92;s+=`<rect x="${L+i*bw+bw*.13+j*g}" y="${H-bh}" width="${g*.9}" height="${Math.max(bh,v?2:0)}" rx="3" fill="${se.c}"><title>${se.l} ${isoMonthLabel(m.month)}: ${fmtN(v)}</title></rect>`});s+=`<text x="${L+i*bw+bw/2}" y="${H+16}" font-size="11" text-anchor="middle" fill="currentColor" opacity=".6">${isoMonthLabel(m.month).slice(0,3)}</text>`});
 return h('div',{html:s+'</svg>'},);}
const legend=ss=>h('div.row.sm',{style:'margin-bottom:6px'},ss.map(s=>h('span.row',{style:'gap:6px'},h('i',{style:`width:10px;height:10px;border-radius:3px;background:${s.c};display:inline-block`}),s.l)));
const actions=(list)=>h('div',list.map(a=>h('div.act'+(a.n>0?'.hot':''),{onclick:()=>go(a.link==='today'?'today':'list/'+a.link)},h('div.cnt',a.n),h('div.grow',h('div',{style:'font-weight:600'},a.label),h('div.sm.mut',a.hint)),ic('tick'))));

/* ============ forms ============ */
function inputFor(f,val){
 let el;
 if(f.type==='text')el=h('textarea');
 else if(f.type==='select'||f.type==='ref'){el=h('select');el.append(h('option',{value:''},'—'));
  const opts=f.type==='ref'?Object.entries(S.refs[f.ref]||{}):(S.me.settings.lists[f.opt]||[]).map(x=>[x,x]);
  if(val&&!opts.some(o=>o[0]===val))opts.unshift([val,val]);
  for(const [v,l] of opts)el.append(h('option',{value:v},l))}
 else el=h('input',{type:f.type==='date'?'date':f.type==='datetime'?'datetime-local':(f.type==='int'||f.type==='float')?'number':'text'});
 if(f.type==='float'||f.type==='int'){el.step='any';el.setAttribute('inputmode','decimal')}
 el.value=val==null?'':val;return el}
const QUICK={
 lead:[['Log follow-up','followup',r=>({lead_code:r.code})],['Create client','client',r=>({lead_code:r.code})]],
 client:[['Add deal','deal',r=>({client_code:r.code})],['Add task','task',r=>({client_code:r.code})],['Add update','update',r=>({client_code:r.code})],['Client ad line','clientad',r=>({client_code:r.code})],['Open 360','@c360',r=>r.code]],
 deal:[['Add payment','payment',r=>({deal_code:r.code})],['Assign person','assignment',r=>({deal_code:r.code})]]};
async function refreshRefs(){S.refs=await api('GET','/api/refs')}
function openForm(kind,row,pre={},done){
 const E=ent(kind),edit=!!row,P_=can(kind,'e'),fields=E.fields.filter(f=>!f.only||f.only.includes(S.me.user.role)),els={};
 const grid=h('div.fg');
 for(const f of fields){
  let v=edit?row[f.name]:(pre[f.name]!==undefined?pre[f.name]:f.default==='now'?nowLocal():f.default==='today'?today():f.default);
  const el=inputFor(f,v);els[f.name]=el;if(!P_)el.disabled=true;
  grid.append(h('div.fld'+(f.wide?'.wide':''),h('label.f',f.label,f.req&&h('span.req',' *')),el))}
 const info=edit&&E.computed.length?h('div.row',{style:'margin-bottom:14px'},E.computed.filter(c=>c.fmt==='chip'&&row['c_'+c.key]).map(c=>h('span.row.sm',{style:'gap:6px'},h('span.mut',c.label),chip(row['c_'+c.key])))):null;
 const quick=edit&&QUICK[kind]?h('div.row',{style:'margin-bottom:14px'},QUICK[kind].filter(q=>q[1][0]==='@'||can(q[1],'e')).map(q=>h('button.btn.s',{onclick:()=>{mo.close();q[1][0]==='@'?go('c360/'+q[2](row)):openForm(q[1],null,q[2](row))}},q[0]))):null;
 const save=h('button.btn.p',{onclick:async()=>{
   const body={};for(const f of fields){const v=els[f.name].value;body[f.name]=v===''?null:v}
   save.disabled=true;try{const r=edit?await api('PUT',`/api/d/${kind}/${row.code}`,body):await api('POST',`/api/d/${kind}`,body);await refreshRefs();toast(edit?'Saved':`${E.one} ${r.code} created`);mo.close();done?done(r):route()}catch(e){fail(e);save.disabled=false}}},'Save');
 const del=edit&&P_?h('button.btn.d',{onclick:async()=>{if(!await confirmBox(`Delete ${row.code}? This cannot be undone.`))return;try{await api('DELETE',`/api/d/${kind}/${row.code}`);await refreshRefs();toast('Deleted');mo.close();route()}catch(e){fail(e)}}},'Delete'):null;
 const mo=modal(edit?`${E.one} ${row.code}`:`New ${E.one.toLowerCase()}`,[info,quick,grid,!P_&&h('p.mut.sm','You have view-only access here.')],[P_&&save,del,h('button.btn.right',{onclick:()=>mo.close()},P_?'Cancel':'Close')]);
 return mo}

/* ============ generic list & board ============ */
function cell(kind,r,key){const E=ent(kind);
 if(key.startsWith('c_')){const c=E.computed.find(x=>x.key===key.slice(2)),v=r[key];if(v==null||v==='')return '–';
  return c.fmt==='chip'?chip(v):c.fmt==='money'?money(v):c.fmt==='pct'?fmtN(v,0)+'%':c.fmt==='date'?fmtD(v):c.fmt==='num'?fmtN(v,1):c.fmt==='int'?fmtN(v):String(v)}
 const f=E.fields.find(x=>x.name===key);if(!f)return '';const v=r[key];if(v==null||v==='')return '–';
 return f.type==='ref'?lbl(f.ref,v):f.type==='date'?fmtD(v):f.type==='datetime'?fmtDT(v):f.type==='select'&&tone(v)?chip(v):f.type==='float'?fmtN(v,2):String(v)}
const isNum=(kind,key)=>{const E=ent(kind);if(key.startsWith('c_')){const c=E.computed.find(x=>x.key===key.slice(2));return ['money','pct','num','int'].includes(c.fmt)}const f=E.fields.find(x=>x.name===key);return f&&(f.type==='float'||f.type==='int')};
const colLabel=(kind,key)=>{const E=ent(kind);return key.startsWith('c_')?E.computed.find(x=>x.key===key.slice(2)).label:E.fields.find(x=>x.name===key).label};
async function pList(kind,q){
 const E=ent(kind),canE=can(kind,'e'),d=await api('GET','/api/d/'+kind);let rows=d.rows;const st={sort:E.sort,desc:E.desc,q:'',f:''};
 const view=q.view==='board'&&E.board?'board':'list';const box=h('div');
 const bf=E.board&&E.fields.find(f=>f.name===E.board);const opts=bf?S.me.settings.lists[bf.opt]||[]:[];
 const search=h('input',{type:'search',placeholder:'Search '+E.label.toLowerCase()+'…','aria-label':'Search',oninput:e=>{st.q=e.target.value.toLowerCase();draw()}});
 const filt=bf?h('select',{'aria-label':'Filter',onchange:e=>{st.f=e.target.value;draw()}},h('option',{value:''},'All '+bf.label.toLowerCase()),opts.map(o=>h('option',{value:o},o))):null;
 const hay=r=>Object.entries(r).map(([k,v])=>v==null?'':(String(v)+' '+(S.refs[(E.fields.find(f=>f.name===k)||{}).ref]||{})[v])).join(' ').toLowerCase();
 const val=(r,k)=>{const v=r[k];return v==null?'':v};
 function draw(){
  let L=rows.filter(r=>(!st.q||hay(r).includes(st.q))&&(!st.f||r[E.board]===st.f));
  L.sort((a,b)=>{const x=val(a,st.sort),y=val(b,st.sort);const c=(typeof x==='number'&&typeof y==='number')?x-y:String(x).localeCompare(String(y),undefined,{numeric:true});return st.desc?-c:c});
  box.replaceChildren();
  if(!L.length){box.append(empty(rows.length?'No matches':`No ${E.label.toLowerCase()} yet`,canE?`Press “New” to add the first ${E.one.toLowerCase()}.`:''));return}
  if(view==='board'){
   const cols=[...opts,...(rows.some(r=>!r[E.board])?['']:[])];
   box.append(h('div.board',cols.map(o=>{const items=L.filter(r=>(r[E.board]||'')===o);
    const col=h('div.col',{ondragover:e=>{e.preventDefault();col.classList.add('over')},ondragleave:()=>col.classList.remove('over'),ondrop:async e=>{e.preventDefault();col.classList.remove('over');const c=e.dataTransfer.getData('text');if(canE&&c)move(c,o)}},
     h('h3',o||'No '+bf.label.toLowerCase(),h('span.chip.n',items.length)),
     items.map(r=>h('div.bc',{draggable:canE,ondragstart:e=>e.dataTransfer.setData('text',r.code),onclick:e=>{if(e.target.tagName!=='SELECT')openForm(kind,r)}},
      h('div',{style:'font-weight:700'},E.title.map(k=>cell(kind,r,k))),h('div.sm.mut',E.sub.map(k=>cell(kind,r,k)).flatMap((x,i)=>i?[' · ',x]:[x])),
      canE&&h('select',{'aria-label':'Move to',onchange:e=>move(r.code,e.target.value)},opts.map(x=>h('option',{value:x,selected:x===r[E.board]},x))))));
    return col})));return}
  const th=E.cols.map(k=>h('th'+(isNum(kind,k)?'.num':''),{onclick:()=>{st.desc=st.sort===k?!st.desc:false;st.sort=k;draw()}},colLabel(kind,k),st.sort===k?(st.desc?' ↓':' ↑'):''));
  box.append(h('div.tw',h('table.rs',h('thead',h('tr',th)),h('tbody',L.slice(0,500).map(r=>h('tr',{onclick:()=>openForm(kind,r),tabindex:0,onkeydown:e=>{if(e.key==='Enter')openForm(kind,r)}},E.cols.map(k=>h('td'+(isNum(kind,k)?'.num':''),{'data-l':colLabel(kind,k)},cell(kind,r,k)))))))));
  if(L.length>500)box.append(h('p.mut.sm.tc','Showing 500 of '+L.length+'. Use search to narrow down.'))}
 async function move(code,to){try{await api('PUT',`/api/d/${kind}/${code}`,{[E.board]:to});toast('Moved to '+to);route()}catch(e){fail(e)}}
 const top=h('div.top',h('h1',E.label),h('span.chip.n',rows.length),
  E.board&&h('div.tabs',{style:'margin:0'},h('button'+(view==='list'?'.on':''),{onclick:()=>go('list/'+kind)},'List'),h('button'+(view==='board'?'.on':''),{onclick:()=>go('list/'+kind+'?view=board')},'Board')),
  h('a.btn',{href:`/api/export/${kind}.csv`,download:kind+'.csv','aria-label':'Export CSV'},ic('download'),h('span.hide-m','CSV')),
  canE&&h('button.btn.p',{onclick:()=>openForm(kind,null)},ic('plus'),'New'));
 const wrap=h('div',top,h('div.tools',search,filt),box);draw();
 if(q.new==='1'&&canE)setTimeout(()=>openForm(kind,null),50);
 return wrap}

/* ============ report pages ============ */
const bars=(arr,fn)=>barlist(arr.map(fn));
async function pDash(q){
 const y=new Date().getFullYear(),f=q.from||`${y}-01-01`,t=q.to||`${y}-12-31`,d=await api('GET',`/api/report/dashboard?from=${f}&to=${t}`),c=d.cards,C=cur();
 const df=h('input',{type:'date',value:f,'aria-label':'From',style:'width:auto'}),dt_=h('input',{type:'date',value:t,'aria-label':'To',style:'width:auto'});
 const top=h('div.top',h('h1','Sales dashboard'),h('div.row',df,h('span.mut','to'),dt_,h('button.btn',{onclick:()=>go(`?from=${df.value}&to=${dt_.value}`)},'Apply')));
 const k=kpis(kpi('Leads',fmtN(c.leads),`${fmtN(c.paid_leads)} from paid ads`),kpi('Qualified',fmtN(c.qualified),fmtN(c.leads?c.qualified/c.leads*100:0)+'% of leads','ok'),kpi('Clients won',fmtN(c.won),fmtN(c.leads?c.won/c.leads*100:0,1)+'% win rate','ok'),
  kpi(`Revenue booked (${C})`,money(c.revenue),`${c.deals} deals won`),kpi(`Cash collected (${C})`,money(c.cash),fmtN(c.revenue?c.cash/c.revenue*100:0)+'% of booked'),kpi(`Own ad spend (${C})`,money(c.ad_spend),'ROAS '+fmtN(c.roas,1)+'x',c.ad_spend&&c.roas<1?'bad':''),
  kpi(`Outstanding (${C})`,money(c.outstanding),'money still due',c.outstanding?'wr':''),kpi('Cost per lead (paid)',money(c.cpl),C),kpi('Cost per client (paid)',money(c.cac),C),
  kpi('Avg first response',fmtN(c.avg_resp,1)+' h',fmtN(c.ontime)+'% on time (target '+S.me.settings.sla_hours+' h)',c.ontime&&c.ontime<80?'wr':''),c.month_target!=null&&kpi('This month vs target',fmtN(c.month_target)+'%',`target ${C} ${money(S.me.settings.monthly_target)}`,c.month_target>=100?'ok':'wr'));
 const fn=d.funnel,f0=fn[0].n||1;
 const sr=[{c:'#4f46e5',l:'Revenue booked',k:'revenue'},{c:'#06b6d4',l:'Cash collected',k:'cash'},{c:'#f59e0b',l:'Own ad spend',k:'spend'}];
 return h('div',top,k,h('div.grid.g2',card('Action needed now',actions(d.action)),card('Sales funnel',barlist(fn.map((x,i)=>({n:x.label,v:x.n})),v=>`${fmtN(v)} · ${fmtN(v/f0*100)}%`))),
  h('div',{style:'height:14px'}),card('Month by month',legend(sr),chart(d.monthly,sr)),h('div',{style:'height:14px'}),
  h('div.grid.g2',card('Where clients come from',d.channels.length?tbl(['Channel','Leads','Qualified','Won',`Revenue (${C})`],d.channels.map(x=>({c:[x.name,x.leads,x.qualified,x.won,money(x.revenue)]})),{num:[1,2,3,4],rs:1}):empty('No leads in this period')),
   card('Services people ask for',barlist(d.services.slice().sort((a,b)=>b.leads-a.leads).slice(0,10).map(x=>({n:x.name,v:x.leads})),v=>fmtN(v)))),
  h('div',{style:'height:14px'}),
  d.paid.length?card('Own paid ads: spend → leads → clients → ROAS',tbl(['Platform',`Spend (${C})`,'Clicks','Leads',`Cost/lead`,'Won',`Revenue (${C})`,'ROAS'],d.paid.map(x=>({c:[x.platform,money(x.spend),fmtN(x.clicks),x.leads,money(x.cpl),x.won,money(x.revenue),h('b',{style:`color:var(--${x.spend&&x.roas<1?'bad':'ok'})`},fmtN(x.roas,1)+'x')]})),{num:[1,2,3,4,5,6,7],rs:1})):null,
  h('div',{style:'height:14px'}),h('div.grid.g2',card('How they contact us',barlist(d.contact.map(x=>({n:x.name,v:x.leads})))),card('Local vs international',barlist(d.market.map(x=>({n:x.name,v:x.leads})),v=>fmtN(v)))))}
async function pOps(){
 const d=await api('GET','/api/report/operations'),c=d.cards,C=cur();
 const team=d.team.filter(e=>e.status!=='Resigned'&&e.status!=='Terminated');
 return h('div',h('div.top',h('h1','Operations')),
  kpis(kpi('Active clients',c.active,`${c.onboarding} onboarding`,'ok'),kpi('At risk (red)',c.red,`${c.amber} amber`,c.red?'bad':''),kpi('Updates overdue',c.updates_due,`no update in ${S.me.settings.update_days}+ days`,c.updates_due?'wr':''),kpi('Open tasks',c.open_tasks),kpi('Overdue tasks',c.overdue_tasks,'',c.overdue_tasks?'bad':''),kpi('Projects in progress',c.in_progress),
   kpi('Active staff',c.staff),kpi('Avg allocation',fmtN(c.avg_alloc)+'%',`${c.overloaded} overloaded`,c.overloaded?'wr':''),kpi(`Client ad budget (${C}, month)`,money(c.ad_budget),'clients\' money'),kpi(`Client ad spend (${C}, month)`,money(c.ad_spend),fmtN(c.ad_budget?c.ad_spend/c.ad_budget*100:0)+'% of budget'),kpi('Agency-advanced, not reimbursed',money(c.advanced),C,c.advanced?'wr':'')),
  h('div.grid.g2',card('Action needed now',actions(d.action)),card('Clients by status',tbl(['Status','Clients',`Contract (${C})`,`Balance (${C})`],d.by_status.map(x=>({c:[chip(x.name),x.n,money(x.contract),money(x.contract-x.paid)]})),{num:[1,2,3],rs:1}),h('div',{style:'height:10px'}),h('h3','Client health (active + onboarding)'),barlist(d.health.map(x=>({n:x.name,v:x.n})),v=>v,x=>x.n&&x.n?({Green:'ok',Amber:'wr',Red:'bad'})[x.n]:'')),),
  h('div',{style:'height:14px'}),card('Team workload',team.length?tbl(['Employee','Role','Clients','Assignments','Allocated','Workload','Open tasks','Overdue'],team.map(e=>({go:'list/employee',c:[e.name,e.role||'–',e.clients_am,e.assigns,h('div',{style:'min-width:110px'},h('div.bar'+(e.alloc>100?'.bad':e.alloc>=S.me.settings.busy_alloc?'.wr':''),h('i',{style:`width:${Math.min(100,e.alloc)}%`})),h('span.sm.mut',fmtN(e.alloc)+'%')),chip(e.util),e.open_tasks,e.overdue]})),{num:[2,3,6,7],rs:1}):empty('Add your team on the Team page')),
  h('div',{style:'height:14px'}),h('div.grid.g2',card('Deals by project status',barlist(d.deals_by.map(x=>({n:x.name,v:x.n})))),card('Tasks by status',barlist(d.tasks_by.map(x=>({n:x.name,v:x.n}))))),
  h('div',{style:'height:14px'}),card('Client ads this month',d.ads.length?tbl(['Platform',`Budget (${C})`,`Spend (${C})`,'Used','Results'],d.ads.map(x=>({c:[x.platform,money(x.budget),money(x.spend),fmtN(x.budget?x.spend/x.budget*100:0)+'%',fmtN(x.results)]})),{num:[1,2,3,4],rs:1}):empty('No client ad lines this month')))}
async function pFin(q){
 const y=+q.year||new Date().getFullYear(),d=await api('GET','/api/report/finance?year='+y),T=d.totals,C=cur();
 const yr=h('select',{style:'width:auto','aria-label':'Year',onchange:e=>go('finance?year='+e.target.value)},[y-2,y-1,y,y+1].map(v=>h('option',{value:v,selected:v===y},v)));
 const sr=[{c:'#16a34a',l:'Cash collected',k:'cash'},{c:'#dc2626',l:'Costs',k:'costs'}];
 return h('div',h('div.top',h('h1','Finance'),yr),
  kpis(kpi(`Revenue booked (${C})`,money(T.revenue)),kpi(`Cash collected (${C})`,money(T.cash),'','ok'),kpi(`Total costs (${C})`,money(T.costs),'own ads + payroll + expenses'),kpi(`Net cash result (${C})`,money(T.net),fmtN(T.cash?T.net/T.cash*100:0)+'% of cash',T.net<0?'bad':'ok'),
   kpi(`Receivables (${C})`,money(d.receivable_total),'owed by clients',d.receivable_total?'wr':''),kpi(`Payroll pending (${C})`,money(d.payroll_pending),'',d.payroll_pending?'wr':''),kpi(`Agency-advanced ads (${C})`,money(d.advanced),'to reimburse',d.advanced?'wr':'')),
  card('Cash vs costs',legend(sr),chart(d.months,sr)),h('div',{style:'height:14px'}),
  card('Monthly result',tbl(['Month','Revenue','Cash','Own ads','Payroll','Expenses','Net result'],d.months.map(m=>({c:[isoMonthLabel(m.month),money(m.revenue),money(m.cash),money(m.own_ads),money(m.payroll),money(m.other),h('b',{style:`color:var(--${m.net<0?'bad':'ok'})`},money(m.net))]})),{num:[1,2,3,4,5,6],foot:['Year',money(T.revenue),money(T.cash),money(T.own_ads),money(T.payroll),money(T.other),money(T.net)]})),
  h('div',{style:'height:14px'}),h('div.grid.g2',card('Where the money goes',barlist(d.costs.filter(x=>x.amount).map(x=>({n:x.name,v:x.amount})))),card('Who owes you',d.receivables.length?tbl(['Deal','Client','Balance'],d.receivables.map(x=>({go:'list/deal',c:[x.code,x.client,money(x.balance)]})),{num:[2],rs:1}):empty('Nobody owes you money'))),
  h('p.mut.sm',`Net cash result is cash in minus costs. It is not accounting profit. Client ad budgets are the client's money and are not counted as your cost.`))}
async function pToday(){
 const d=await api('GET','/api/report/today');
 return h('div',h('div.top',h('h1','Today queue'),h('span.chip.n',d.rows.length)),
  d.rows.length?tbl(['Lead','Status','Phone','Service','Stage','Next follow-up','Age'],d.rows.map(r=>({c:[h('div',h('b',r.name),h('div.sm.mut',r.company||'')),chip(r.status),r.phone?h('a',{href:'https://wa.me/'+r.phone.replace(/\D/g,''),target:'_blank',rel:'noopener',onclick:e=>e.stopPropagation()},r.phone):'–',r.service||'–',r.stage||'New',fmtD(r.next_followup),r.age!=null?r.age+' d':'–'],click:async()=>{try{openForm('lead',await api('GET','/api/d/lead/'+r.code))}catch(e){fail(e)}}})),{rs:1}):empty('Inbox zero','Nobody needs a reply or follow-up right now.'))}
async function pC360(code){
 if(!code){const inp=h('input',{type:'search',placeholder:'Search clients…',oninput:draw});const box=h('div');
  function draw(){const q=inp.value.toLowerCase();const L=Object.entries(S.refs.client||{}).filter(([c,l])=>(c+l).toLowerCase().includes(q));box.replaceChildren(L.length?tbl(['Client','Code'],L.map(([c,l])=>({go:'c360/'+c,c:[l,c]})),{rs:1}):empty('No clients found'))}draw();
  return h('div',h('div.top',h('h1','Client 360')),h('div.tools',inp),box)}
 const d=await api('GET','/api/client360/'+code),c=d.client,C=cur(),E=can('client','e');
 const dealsAct=E&&can('deal','e');
 return h('div',h('div.top',h('h1',c.c_display),chip(c.status),chip(c.health),h('button.btn',{onclick:()=>window.print()},ic('print'),'Print / PDF'),
   E&&h('button.btn',{onclick:()=>openForm('client',c)},'Edit'),can('update','e')&&h('button.btn.p',{onclick:()=>openForm('update',null,{client_code:code})},ic('plus'),'Update')),
  h('p.mut.sm',[code,' · lead ',c.lead_code,' · ',c.c_channel||'–',' · ',c.c_country||'–',' · account manager ',lbl('employee',c.am)||'–',' · since ',fmtD(c.since)]),
  kpis(kpi(`Contract (${C})`,money(c.c_contract),c.c_deals+' deals'),kpi(`Paid (${C})`,money(c.c_paid),'','ok'),kpi(`Balance (${C})`,money(c.c_balance),'',c.c_balance>0?'wr':''),kpi(`Ad budget (${C}, month)`,money(c.c_budget_m),'spend '+money(c.c_spend_m)),
   kpi('Open tasks',c.c_open_tasks,c.c_overdue_tasks+' overdue',c.c_overdue_tasks?'bad':''),kpi('Last update',c.c_last_update?fmtD(c.c_last_update):'None',c.c_update_status||'',c.c_update_status==='OK'?'ok':'wr'),kpi('Team',c.c_team,'people assigned',c.c_team?'':'bad'),kpi(`Margin (${C})`,money(c.c_margin),'collected − direct costs')),
  h('div.grid.g2',
   card('Services & contract',d.deals.length?tbl(['Deal','Service','Total','Paid','Balance','Payment','Delivery'],d.deals.map(x=>({c:[x.code,x.service,money(x.c_total),money(x.c_paid),money(x.c_balance),chip(x.c_pay_status),chip(x.c_alert)]})),{num:[2,3,4],rs:1}):empty('No deals yet'),dealsAct&&h('button.btn.s',{style:'margin-top:10px',onclick:()=>openForm('deal',null,{client_code:code})},ic('plus'),'Add deal')),
   card('Team assigned',d.team.length?tbl(['Person','Role','Deal','Allocation','Status'],d.team.map(x=>({c:[x.c_emp_name,x.prole,x.deal_code,fmtN(x.alloc)+'%',chip(x.status)]})),{num:[3],rs:1}):empty('Nobody assigned'),can('assignment','e')&&d.deals.length?h('button.btn.s',{style:'margin-top:10px',onclick:()=>openForm('assignment',null,{deal_code:d.deals[0].code})},ic('plus'),'Assign person'):null)),
  h('div',{style:'height:14px'}),h('div.grid.g2',
   card('Tasks',d.tasks.length?tbl(['Task','Assignee','Due','Status','Flag'],d.tasks.map(x=>({c:[x.title,lbl('employee',x.assignee)||'–',fmtD(x.due),chip(x.status),chip(x.c_flag)]})),{rs:1}):empty('No tasks'),can('task','e')&&h('button.btn.s',{style:'margin-top:10px',onclick:()=>openForm('task',null,{client_code:code})},ic('plus'),'Add task')),
   card('Updates & reports',d.updates.length?h('div',d.updates.map(x=>h('div',{style:'padding:10px 0;border-bottom:1px solid var(--bd)'},h('div.row',h('b',x.utype||'Update'),chip(x.sentiment),h('span.sm.mut.right',fmtDT(x.at))),h('div',x.summary||''),x.results&&h('div.sm.mut','Results: '+x.results)))):empty('No updates logged'))),
  h('div',{style:'height:14px'}),h('div.grid.g2',
   card('Ad budget vs spend',d.ads.length?tbl(['Month','Platform','Budget','Spend','Used','Flag'],d.ads.map(x=>({c:[fmtD(x.month).slice(3),x.platform||'–',money(x.c_budget_base),money(x.c_spend_base),x.c_used!=null?fmtN(x.c_used)+'%':'–',chip(x.c_flag)]})),{num:[2,3,4],rs:1}):empty('No ad budget lines'),can('clientad','e')&&h('button.btn.s',{style:'margin-top:10px',onclick:()=>openForm('clientad',null,{client_code:code})},ic('plus'),'Add ad line')),
   card('Payments',d.payments.length?tbl(['Date','Deal',`Amount (${C})`,'Method'],d.payments.map(x=>({c:[fmtD(x.date),x.deal_code,money(x.amount),x.method||'–']})),{num:[2],rs:1}):empty('No payments yet'))))}

/* ============ company pages ============ */
const RES={dashboard:'Sales dashboard',operations:'Operations',finance:'Finance',client360:'Client 360',today:'Today queue'};
async function pAccess(q){
 const tab=q.tab||'logins',tabs=h('div.tabs',[['logins','Logins'],['matrix','Roles & access'],['audit','Activity log']].map(([k,l])=>h('button'+(tab===k?'.on':''),{onclick:()=>go('access?tab='+k)},l)));
 const head=h('div.top',h('h1','Logins & access'));
 if(tab==='matrix'){const roles=S.schema.roles.filter(r=>r.key!=='owner'),keys=Object.keys(S.schema.perm).filter(k=>!['users','settings','audit','billing'].includes(k));
  const c=(k,i)=>{const v=S.schema.perm[k][i];return v==='e'?h('span.chip.ok','Edit'):v==='v'?h('span.chip','View'):h('span.mut','—')};
  return h('div',head,tabs,tbl(['Area','Owner / CEO',...roles.map(r=>r.label)],keys.map(k=>({c:[(RES[k]||(S.schema.entities[k]||{}).label||k),h('span.chip.ok','Edit'),...roles.map((r,i)=>c(k,i))]})),{rs:1}),h('p.mut.sm','Owner always has full access, including Settings, Logins, Billing and the activity log. Salaries are visible only to Owner and Accounts.'))}
 if(tab==='audit'){const d=await api('GET','/api/audit');return h('div',head,tabs,d.rows.length?tbl(['When','Who','Action','Record','Fields'],d.rows.map(r=>({c:[fmtDT(r.at),r.user,r.action,`${(S.schema.entities[r.kind]||{}).label||r.kind} ${r.code}`,r.detail||'']})),{rs:1}):empty('No activity yet'))}
 const d=await api('GET','/api/team/users'),roles=S.schema.roles;
 const rows=d.users.map(u=>({c:[h('div',h('b',u.name),h('div.sm.mut',u.email)),h('select',{style:'min-width:150px',onclick:e=>e.stopPropagation(),onchange:async e=>{try{await api('PUT','/api/team/users/'+u.id,{role:e.target.value});toast('Role updated')}catch(x){fail(x);route()}}},roles.map(r=>h('option',{value:r.key,selected:r.key===u.role},r.label))),u.employee_code?lbl('employee',u.employee_code):'–',u.last_login?fmtDT(u.last_login):'Never',chip(u.active?'Active':'Disabled'),
   h('div.row',{style:'gap:6px'},h('button.btn.s',{onclick:async e=>{e.stopPropagation();const p=prompt('New password for '+u.name+' (min 8 characters):');if(!p)return;try{await api('PUT','/api/team/users/'+u.id,{password:p});toast('Password changed')}catch(x){fail(x)}}},'Reset password'),
    h('button.btn.s'+(u.active?'.d':''),{onclick:async e=>{e.stopPropagation();try{await api('PUT','/api/team/users/'+u.id,{active:!u.active});route()}catch(x){fail(x)}}},u.active?'Disable':'Enable'))]}));
 return h('div',h('div.top',h('h1','Logins & access'),h('button.btn.p',{onclick:newLogin},ic('plus'),'Add login')),tabs,h('p.mut.sm','Logins are people who sign in. Staff records (salary, workload) live on the Team page: link a login to a staff record.'),tbl(['Person','Role','Staff record','Last login','Status','Actions'],rows,{rs:1}))}
function newLogin(){
 const f={name:h('input',{placeholder:'Full name'}),email:h('input',{type:'email',placeholder:'name@company.com'}),role:h('select',S.schema.roles.filter(r=>r.key!=='owner').map(r=>h('option',{value:r.key},r.label))),pw:h('input',{type:'text',value:Math.random().toString(36).slice(2,6)+Math.random().toString(36).slice(2,6).toUpperCase()+'9',autocomplete:'off'}),emp:inputFor({type:'ref',ref:'employee'},'')};
 const row=(l,e,hint)=>h('div.fld',h('label.f',l),e,hint&&h('div.sm.mut',hint));
 const m=modal('Add a login',h('div',row('Name',f.name),row('Email',f.email),row('Role',f.role),row('Temporary password',f.pw,'Share it with them; they can change it after signing in.'),row('Staff record (optional)',f.emp)),
  [h('button.btn.p',{onclick:async()=>{try{await api('POST','/api/team/users',{name:f.name.value,email:f.email.value,role:f.role.value,password:f.pw.value,employee_code:f.emp.value});toast('Login created');m.close();route()}catch(e){fail(e)}}},'Create login'),h('button.btn',{onclick:()=>m.close()},'Cancel')])}
const SET_NUM=[['rate','Rate: 1 foreign currency = ? base currency'],['card_rate','Own-ads card rate (foreign → base)'],['default_charge','Default service charge %'],['qualified_score','Qualified lead score (min)'],['warm_score','Warm lead score (min)'],['sla_hours','First-response target (hours)'],['monthly_target','Monthly revenue target'],['update_days','Client update every (days)'],['budget_alert','Ad budget warning at %'],['busy_alloc','“Busy” workload from %'],['tz_offset','Time zone offset from UTC (hours)']];
const SET_LISTS=[['services','Services you sell'],['channels','Lead channels'],['paid_channels','Paid channels (subset of channels)'],['contact','Contact methods'],['lost','Lost reasons'],['paym','Payment methods'],['xcat','Expense categories'],['depts','Departments'],['erole','Job roles'],['utype','Update types']];
async function pSettings(){
 const s=S.me.settings,els={},mk=(k,l,v,t='text')=>{els[k]=h('input',{type:t,value:v,step:'any'});return h('div.fld',h('label.f',l),els[k])};
 const name=h('input',{value:S.me.org.name});const lists={};
 const gen=h('div.fg',mk('currency_base','Base currency (what you get paid in)',s.currency_base),mk('currency_foreign','Foreign currency (what you price in)',s.currency_foreign),mk('home_country','Home country (for Local / International)',s.home_country),SET_NUM.map(([k,l])=>mk(k,l,s[k],'number')));
 const ls=h('div.fg',SET_LISTS.map(([k,l])=>{lists[k]=h('textarea',{rows:6,value:s.lists[k].join('\n')});return h('div.fld',h('label.f',l+' (one per line)'),lists[k])}));
 return h('div',h('div.top',h('h1','Settings'),h('button.btn.p',{onclick:async e=>{const st={};for(const k of ['currency_base','currency_foreign','home_country'])st[k]=els[k].value;for(const [k] of SET_NUM)st[k]=els[k].value;st.lists={};for(const k in lists)st.lists[k]=lists[k].value.split('\n');
   try{await api('PUT','/api/org',{name:name.value,settings:st});S.me=await api('GET','/api/me');toast('Settings saved');route()}catch(x){fail(x)}}},'Save settings')),
  card('Business',h('div.fld',h('label.f','Business name'),name),gen,h('p.mut.sm','Changing currencies does not convert existing records. New deals freeze the rate and charge at the time they are created.')),h('div',{style:'height:14px'}),card('Your lists',h('p.mut.sm','These fill the dropdowns across the app. Remove an item only if no records use it.'),ls))}
async function pBilling(q){
 const d=await api('GET','/api/billing'),st=d.state,cp=d.plans.find(p=>p.key===d.plan_key);let yearly=false;const box=h('div');
 const pay=p=>{const months=h('select',[[1,'1 month'],[3,'3 months'],[6,'6 months'],[12,'12 months (best price)']].map(([v,l])=>h('option',{value:v},l))),method=h('select',['bKash','Nagad','Rocket','Bank Transfer','Other'].map(x=>h('option',x))),txn=h('input',{placeholder:'Transaction ID'}),note=h('input',{placeholder:'Note (optional)'});
  const amt=h('div',{style:'font-size:22px;font-weight:800;margin:8px 0'});const upd=()=>{const m=+months.value;amt.textContent=`${p.currency} ${fmtN(m===12&&p.price_yearly?p.price_yearly:p.price_monthly*m)}`};months.onchange=upd;upd();
  const m=modal('Pay for '+p.name,h('div',h('p',d.instructions),amt,h('div.fld',h('label.f','Period'),months),h('div.fld',h('label.f','Paid by'),method),h('div.fld',h('label.f','Transaction ID'),txn),h('div.fld',h('label.f','Note'),note)),
   [h('button.btn.p',{onclick:async()=>{try{await api('POST','/api/billing/request',{plan_key:p.key,months:+months.value,method:method.value,txn_id:txn.value,note:note.value});toast('Submitted. We will activate your plan after we confirm the payment.');m.close();route()}catch(e){fail(e)}}},'Submit payment'),h('button.btn',{onclick:()=>m.close()},'Cancel')])};
 const card_=async p=>{try{const r=await api('POST','/api/billing/checkout',{plan_key:p.key,interval:yearly?'yearly':'monthly'});location.href=r.url}catch(e){fail(e)}};
 function draw(){box.replaceChildren(h('div.plans',d.plans.map(p=>h('div.plan'+(p.key===d.plan_key&&st.active?'.cur':''),h('h2',p.name,p.key===d.plan_key&&st.active?h('span.chip.ok',{style:'margin-left:8px'},'Current'):null),h('div',h('span.pr',`${p.currency} ${fmtN(yearly&&p.price_yearly?p.price_yearly:p.price_monthly)}`),h('span.mut',yearly?' / year':' / month')),
   h('ul',p.features.map(f=>h('li',ic('tick'),f))),owner()&&h('button.btn.p',{onclick:()=>pay(p)},'Pay with bKash / Nagad / bank'),owner()&&d.stripe&&h('button.btn',{onclick:()=>card_(p)},'Pay by card')))))}
 draw();
 const tg=h('div.tabs',h('button.on',{onclick:e=>{yearly=false;tg.children[0].className='on';tg.children[1].className='';draw()}},'Monthly'),h('button',{onclick:e=>{yearly=true;tg.children[1].className='on';tg.children[0].className='';draw()}},'Yearly (save ~2 months)'));
 return h('div',h('div.top',h('h1','Billing')),
  card('Your subscription',h('div.kv',h('div','Plan'),h('div',cp?cp.name:'–'),h('div','Status'),h('div',chip(st.status)),h('div','Days left'),h('div',st.active?st.days_left:'0'),h('div','Logins used'),h('div',`${d.users} of ${cp?cp.max_users:'–'}`),h('div','Leads allowed'),h('div',cp?fmtN(cp.max_leads):'–'))),
  h('div',{style:'height:14px'}),!owner()&&h('p.mut','Only the owner can change the plan.'),tg,box,
  d.requests.length?h('div',h('div',{style:'height:14px'}),card('Payment history',tbl(['Date','Plan','Months','Amount','Method','Txn ID','Status'],d.requests.map(r=>({c:[fmtDT(r.created_at),r.plan_key,r.months,`${r.currency} ${fmtN(r.amount)}`,r.method,r.txn_id,chip(r.status)]})),{rs:1}))):null)}
async function pAdmin(q){
 const tab=q.tab||'overview',tabs=h('div.tabs',[['overview','Overview'],['orgs','Businesses'],['payments','Payments'],['plans','Plans']].map(([k,l])=>h('button'+(tab===k?'.on':''),{onclick:()=>go('admin?tab='+k)},l))),head=h('div.top',h('h1','Platform admin'));
 if(tab==='orgs'){const d=await api('GET','/api/admin/orgs'),pl=(await api('GET','/api/admin/plans')).plans;
  return h('div',head,tabs,tbl(['Business','Owner','Plan','Status','Days left','Users','Created','Actions'],d.orgs.map(o=>({c:[h('b',o.name),o.owner,h('select',{onchange:async e=>{try{await api('POST',`/api/admin/orgs/${o.id}/action`,{action:'plan',plan_key:e.target.value});toast('Plan changed')}catch(x){fail(x)}}},pl.map(p=>h('option',{value:p.key,selected:p.key===o.plan},p.name))),chip(o.state.status),o.state.days_left,o.users,o.created,
   h('div.row',{style:'gap:6px'},h('button.btn.s',{onclick:async()=>{const n=prompt('Extend by how many days?','14');if(!n)return;try{await api('POST',`/api/admin/orgs/${o.id}/action`,{action:'extend',days:+n});toast('Extended');route()}catch(x){fail(x)}}},'Extend'),h('button.btn.s',{onclick:async()=>{const p=prompt('New password for '+o.owner+' (min 8 characters):');if(!p)return;try{await api('POST','/api/admin/users/reset_password',{email:o.owner,password:p});toast('Owner password changed')}catch(x){fail(x)}}},'Reset owner pw'),h('button.btn.s'+(o.state.status==='suspended'?'':'.d'),{onclick:async()=>{try{await api('POST',`/api/admin/orgs/${o.id}/action`,{action:o.state.status==='suspended'?'unsuspend':'suspend'});route()}catch(x){fail(x)}}},o.state.status==='suspended'?'Unsuspend':'Suspend'))]})),{rs:1}))}
 if(tab==='payments'){const d=await api('GET','/api/admin/payments?status=all');
  return h('div',head,tabs,d.rows.length?tbl(['When','Business','Plan','Months','Amount','Method','Txn ID','Status','Action'],d.rows.map(r=>({c:[fmtDT(r.created_at),r.org,r.plan_key,r.months,`${r.currency} ${fmtN(r.amount)}`,r.method,h('b',r.txn_id),chip(r.status),r.status==='pending'?h('div.row',{style:'gap:6px'},h('button.btn.s.p',{onclick:async()=>{try{await api('POST',`/api/admin/payments/${r.id}/decide`,{approve:true});toast('Approved and activated');route()}catch(x){fail(x)}}},'Approve'),h('button.btn.s.d',{onclick:async()=>{try{await api('POST',`/api/admin/payments/${r.id}/decide`,{approve:false});route()}catch(x){fail(x)}}},'Reject')):'']})),{rs:1}):empty('No payments yet'))}
 if(tab==='plans'){const d=await api('GET','/api/admin/plans');
  return h('div',head,tabs,h('p.mut.sm','Edit prices and limits. Changes apply to everyone immediately. Prices are placeholders until you set yours.'),h('div.grid.g3',d.plans.map(p=>{const e={};const f=(k,l,t='text')=>{e[k]=h('input',{type:t,value:p[k]});return h('div.fld',h('label.f',l),e[k])};
   const feat=h('textarea',{rows:5,value:p.features.join('\n')});
   return card(p.name,f('name','Name'),f('price_monthly','Price / month','number'),f('price_yearly','Price / year','number'),f('currency','Currency'),f('max_users','Max logins','number'),f('max_leads','Max leads','number'),f('stripe_price_monthly','Stripe price ID (monthly)'),f('stripe_price_yearly','Stripe price ID (yearly)'),h('div.fld',h('label.f','Features (one per line)'),feat),
    h('button.btn.p',{onclick:async()=>{const b={features:feat.value.split('\n').filter(Boolean)};for(const k in e)b[k]=e[k].value;try{await api('PUT','/api/admin/plans/'+p.key,b);toast('Plan saved')}catch(x){fail(x)}}},'Save'))})))}
 const o=await api('GET','/api/admin/overview'),C='BDT';
 return h('div',head,tabs,kpis(kpi('Businesses',o.orgs),kpi('Active (paying)',o.active,'','ok'),kpi('On trial',o.trialing),kpi('Expired',o.expired,'',o.expired?'wr':''),kpi('Suspended',o.suspended),kpi('Pending payments',o.pending,'',o.pending?'bad':''),kpi('Monthly recurring (est.)',fmtN(o.mrr),C),kpi('Total users',o.users)),
  o.pending?h('div.banner',`${o.pending} payment(s) waiting for approval`,h('button.btn.s',{onclick:()=>go('admin?tab=payments')},'Review')):null)}

/* ============ auth ============ */
function authShell(title,sub,form){return h('div.auth',h('div.hero',h('div.row',h('div.logo',{style:'width:44px;height:44px;font-size:18px'},'R1'),h('b',{style:'font-size:22px'},'RITS One')),h('h1','Run your whole business from one place.'),h('ul',['Leads, follow-ups and qualification','Clients, deals, tasks and team assignments','Client reports, ad budgets and payments','Finance, payroll and live dashboards','Works on phone, tablet and desktop'].map(x=>h('li',ic('tick'),x)))),h('div.formside',h('div.formbox',h('h2',title),h('p.mut',{style:'margin:0 0 18px'},sub),form)))}
const fld=(l,el)=>h('div.fld',h('label.f',l),el);
function pLogin(){
 const em=h('input',{type:'email',autocomplete:'username',required:true,autofocus:true}),pw=h('input',{type:'password',autocomplete:'current-password',required:true}),btn=h('button.btn.p',{type:'submit'},'Sign in');
 const form=h('form',{onsubmit:async e=>{e.preventDefault();btn.disabled=true;try{await api('POST','/api/auth/login',{email:em.value,password:pw.value});await boot();go('')}catch(x){fail(x);btn.disabled=false}}},fld('Email',em),fld('Password',pw),btn,h('p.tc.sm',h('a',{href:'#/forgot'},'Forgot password?')),h('p.tc.sm.mut','New here? ',h('a',{href:'#/signup'},'Start your free trial')));
 return authShell('Welcome back','Sign in to your workspace.',form)}
function pSignup(){
 const f={org:h('input',{required:true,placeholder:'e.g. Rafirit Station'}),name:h('input',{required:true,autocomplete:'name'}),em:h('input',{type:'email',required:true,autocomplete:'username'}),pw:h('input',{type:'password',minlength:8,required:true,autocomplete:'new-password'}),tpl:h('select',h('option',{value:'agency'},'Digital / IT agency (ready-made services)'),h('option',{value:'general'},'Other business (start simple)'))},btn=h('button.btn.p',{type:'submit'},'Create my workspace');
 const form=h('form',{onsubmit:async e=>{e.preventDefault();btn.disabled=true;try{await api('POST','/api/auth/signup',{org_name:f.org.value,name:f.name.value,email:f.em.value,password:f.pw.value,template:f.tpl.value});await boot();go('')}catch(x){fail(x);btn.disabled=false}}},fld('Business name',f.org),fld('Your name',f.name),fld('Work email',f.em),fld('Password (8+ characters)',f.pw),fld('Business type',f.tpl),btn,h('p.tc.sm.mut','Already have an account? ',h('a',{href:'#/login'},'Sign in')));
 return authShell('Start your free trial','No card needed. Set up in minutes.',form)}
function pForgot(){
 const em=h('input',{type:'email',required:true});
 return authShell('Reset password','We will email you a reset link.',h('form',{onsubmit:async e=>{e.preventDefault();try{await api('POST','/api/auth/forgot',{email:em.value});toast('If that email exists, a reset link is on its way.')}catch(x){fail(x)}}},fld('Email',em),h('button.btn.p',{type:'submit'},'Send reset link'),h('p.tc.sm',h('a',{href:'#/login'},'Back to sign in'))))}
function pReset(q){
 const pw=h('input',{type:'password',minlength:8,required:true,autocomplete:'new-password'});
 return authShell('Choose a new password','At least 8 characters.',h('form',{onsubmit:async e=>{e.preventDefault();try{await api('POST','/api/auth/reset',{token:q.token,password:pw.value});toast('Password changed. Please sign in.');go('login')}catch(x){fail(x)}}},fld('New password',pw),h('button.btn.p',{type:'submit'},'Save password')))}

/* ============ shell & router ============ */
const NAV=[['Overview',[['','Dashboard','home','dashboard'],['ops','Operations','chart','operations'],['finance','Finance','wallet','finance'],['today','Today queue','inbox','today']]],
['Sales',[['list/lead','Leads','target','lead'],['list/followup','Follow-ups','message','followup']]],
['Clients & delivery',[['list/client','Clients','briefcase','client'],['c360','Client 360','eye','client360'],['list/deal','Deals','file','deal'],['list/assignment','Assignments','users','assignment'],['list/task','Tasks','check','task'],['list/update','Updates & reports','message','update'],['list/clientad','Client ads','megaphone','clientad']]],
['Money',[['list/payment','Payments','wallet','payment'],['list/ownad','Own ad spend','megaphone','ownad'],['list/expense','Expenses','file','expense'],['list/payroll','Payroll','card','payroll']]],
['Company',[['list/employee','Team','users','employee'],['access','Logins & access','shield','users'],['settings','Settings','sliders','settings'],['billing','Billing','card','billing']]]];
const allowed=r=>r==='billing'?owner():can(r);
const parse=()=>{const [p,qs]=(location.hash.slice(2)||'').split('?');return{segs:p.split('/').filter(Boolean),q:Object.fromEntries(new URLSearchParams(qs||''))}};
const homeRoute=()=>{for(const [,items] of NAV)for(const [p,,,r] of items)if(allowed(r))return p;return 'billing'};
function theme(){document.documentElement.dataset.theme=S.dark?'dark':'light';const m=document.querySelector('meta[name=theme-color]');if(m)m.content=S.dark?'#0a0f1f':'#4f46e5'}
function installHelp(){if(S.install){S.install.prompt();return}modal('Install RITS One as an app',h('div',h('p','Add RITS One to your home screen so it opens like a normal app, full screen.'),h('p',h('b','iPhone / iPad (Safari): '),'tap Share, then “Add to Home Screen”.'),h('p',h('b','Android (Chrome): '),'tap the ⋮ menu, then “Install app” / “Add to Home screen”.'),h('p',h('b','Computer (Chrome / Edge): '),'click the install icon at the right of the address bar.')))}
function changePw(){const o=h('input',{type:'password',autocomplete:'current-password'}),n=h('input',{type:'password',minlength:8,autocomplete:'new-password'});const m=modal('Change password',h('div',fld('Current password',o),fld('New password (8+ characters)',n)),[h('button.btn.p',{onclick:async()=>{try{await api('POST','/api/auth/password',{old:o.value,new:n.value});toast('Password changed');m.close()}catch(e){fail(e)}}},'Save'),h('button.btn',{onclick:()=>m.close()},'Cancel')])}
async function logout(){try{await api('POST','/api/auth/logout')}catch(_){}S.me=null;S.booted=false;location.hash='#/login'}
function shell(){
 const u=S.me.user,sa=u.superadmin&&!S.me.org;let side;
 const link=(p,l,i)=>h('a',{href:'#/'+p,'data-p':p,onclick:()=>side.classList.remove('open')},ic(i),l);
 const nav=h('nav.nav',{'aria-label':'Main'},sa?[h('h4','Platform'),link('admin','Admin','shield')]:NAV.map(([g,items])=>{const L=items.filter(i=>allowed(i[3]));return L.length?[h('h4',g),L.map(i=>link(i[0],i[1],i[2]))]:null}));
 side=h('aside.side',h('div.brand',h('div.logo','R1'),h('div',h('div','RITS One'),h('div.sm.mut',{style:'font-weight:500'},sa?'Platform admin':S.me.org.name))),nav,
  h('div.sidefoot',h('div.av',u.name.slice(0,1).toUpperCase()),h('div.grow',{style:'min-width:0'},h('div',{style:'font-weight:600;overflow:hidden;text-overflow:ellipsis'},u.name),h('div.sm.mut',(S.schema.roles.find(r=>r.key===u.role)||{}).label||u.role)),
   h('button.btn.g.ic',{title:'Dark / light','aria-label':'Toggle theme',onclick:()=>{S.dark=!S.dark;localStorage.theme=S.dark?'dark':'light';theme()}},ic('moon')),
   h('button.btn.g.ic',{title:'Install app','aria-label':'Install app',onclick:installHelp},ic('download')),h('button.btn.g.ic',{title:'Change password','aria-label':'Change password',onclick:changePw},ic('shield')),h('button.btn.g.ic',{title:'Sign out','aria-label':'Sign out',onclick:logout},ic('logout'))));
 const tabs=sa?[]:[['','Home','home','dashboard'],['today','Today','inbox','today'],['list/lead','Leads','target','lead'],['list/task','Tasks','check','task'],['list/client','Clients','briefcase','client']].filter(i=>allowed(i[3])).slice(0,4);
 const tb=h('nav.tabbar',{'aria-label':'Quick'},tabs.map(([p,l,i])=>h('a',{href:'#/'+p,'data-p':p},ic(i),l)),h('button',{onclick:()=>{side.classList.toggle('open');let s=$('.scrim');if(side.classList.contains('open')&&!s){s=h('div.scrim',{onclick:()=>{side.classList.remove('open');s.remove()}});document.body.append(s)}else if(s)s.remove()}},ic('more'),'More'));
 $('#root').replaceChildren(h('div.app',side,h('main.main',{id:'main'},h('div#banner'),h('div#view')),tb));
}
function banner(){
 const b=$('#banner');if(!b||!S.me.subscription)return;const s=S.me.subscription;b.replaceChildren();
 const act=owner()?h('button.btn.s.p',{onclick:()=>go('billing')},'Choose a plan'):null;
 if(s.status==='suspended')b.append(h('div.banner.bad','This workspace is suspended. Contact support.'));
 else if(!s.active)b.append(h('div.banner.bad','Your subscription has expired. You can view your data but cannot make changes.',act));
 else if(s.status==='trialing')b.append(h('div.banner',`Free trial: ${s.days_left} day${s.days_left===1?'':'s'} left.`,act));
 else if(s.days_left<=5)b.append(h('div.banner',`Your plan renews in ${s.days_left} day(s).`,owner()?h('button.btn.s.p',{onclick:()=>go('billing')},'Renew'):null))}
let rid=0;
async function route(){
 const my=++rid,{segs,q}=parse(),r0=segs[0]||'',auth=['login','signup','forgot','reset'];
 if(!S.booted){await boot()}
 if(!S.me){if(!auth.includes(r0)){location.hash='#/login';return}
  $('#root').replaceChildren(r0==='signup'?pSignup():r0==='forgot'?pForgot():r0==='reset'?pReset(q):pLogin());return}
 if(auth.includes(r0)){go('');return}
 const sa=S.me.user.superadmin&&!S.me.org;
 if(!$('#view')||S.shellFor!==S.me.user.id){shell();S.shellFor=S.me.user.id}
 if(sa&&r0!=='admin'){go('admin');return}
 if(!sa&&r0===''&&!allowed('dashboard')){go(homeRoute());return}
 document.querySelectorAll('[data-p]').forEach(a=>{const p=a.dataset.p;a.classList.toggle('on',p===''?!r0:(r0+'/'+(segs[1]||'')).startsWith(p)&&(p!=='list/'||true)&&(segs.join('/')===p||segs.join('/').startsWith(p+'/')||r0===p))});
 banner();const view=$('#view');view.replaceChildren(skeleton());
 let res=r0==='list'?segs[1]:{'':'dashboard',ops:'operations',finance:'finance',today:'today',c360:'client360',access:'users',settings:'settings',billing:'billing',admin:'admin'}[r0];
 try{
  if(!sa&&!allowed(res)&&r0!=='billing'){view.replaceChildren(h('div.empty',h('h3','No access'),h('p','Ask the owner to change your role if you need this.')));return}
  if(r0==='list'&&!S.schema.entities[segs[1]]){view.replaceChildren(empty('Page not found'));return}
  const node=await ({'':()=>pDash(q),ops:pOps,finance:()=>pFin(q),today:pToday,c360:()=>pC360(segs[1]),list:()=>pList(segs[1],q),access:()=>pAccess(q),settings:pSettings,billing:()=>pBilling(q),admin:()=>pAdmin(q)}[r0]||(()=>empty('Page not found')))();
  if(my===rid){view.replaceChildren(node);window.scrollTo(0,0)}
 }catch(e){if(my===rid){view.replaceChildren(h('div.empty',h('h3',e.status===402?'Subscription needed':'Could not load'),h('p',e.message),owner()&&e.status===402?h('button.btn.p',{onclick:()=>go('billing')},'Open billing'):h('button.btn',{onclick:route},'Try again')))}}
}
async function boot(){
 try{S.me=await api('GET','/api/me')}catch(_){S.me=null}
 if(!S.schema)try{S.schema=await api('GET','/api/schema')}catch(_){}
 if(S.me&&S.me.org)try{await refreshRefs()}catch(_){}
 S.booted=true;S.shellFor=null}
window.addEventListener('hashchange',route);
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();S.install=e});
theme();
if('serviceWorker'in navigator&&(location.protocol==='https:'||location.hostname==='localhost'))navigator.serviceWorker.register('/sw.js').catch(()=>{});
window.__rits={route,S};
route();
})();
