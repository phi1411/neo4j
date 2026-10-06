'use strict';
window.escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
window.wrapLabel = (value, width) => {
  const lines = []; let line='';
  for (const word of value.split(' ')) { if (line && line.length+word.length+1>width) {lines.push(line);line='';} line += (line?' ':'')+word; }
  if (line) lines.push(line); return lines.join('\n');
};
const $ = id => document.getElementById(id), esc=window.escapeHTML;
function state(id,message,error=false) { const element=$(id); element.textContent=message; element.classList.toggle('error',error); }
function connection(message,bad=false) { $('connection').textContent=message; $('connection').className=`connection ${bad?'bad':'ok'}`; }
// Không cache/fallback. Mỗi thao tác đọc response API thật và lược bỏ chẩn đoán nội bộ.
window.api = async (url, options={}) => {
  const controller=new AbortController(), timer=setTimeout(()=>controller.abort(),20000);
  try {
    const response=await fetch(url,{cache:'no-store',...options,signal:controller.signal});
    let body; try {body=await response.json();} catch {throw new Error('Phản hồi máy chủ không hợp lệ. Hãy tải lại trang.');}
    if (!response.ok || !body.success) {
      if (response.status===503) connection('Neo4j chưa kết nối',true);
      throw new Error(body.error?.message || `Không thực hiện được yêu cầu (HTTP ${response.status}).`);
    }
    return body.data;
  } catch(error) {
    if (error.name==='AbortError') throw new Error('Máy chủ phản hồi quá lâu. Kiểm tra Flask và Neo4j rồi thử lại.');
    if (error instanceof TypeError) {connection('Không liên lạc được Flask',true);throw new Error('Không liên lạc được máy chủ Flask. Kiểm tra server đang chạy rồi tải lại trang.');}
    throw error;
  } finally {clearTimeout(timer);}
};
async function health() {
  $('connection').textContent='Đang kiểm tra Neo4j…';
  try {await api('/api/health');connection('Neo4j đang kết nối · Kiểm tra lại ↻');}
  catch(error) {connection(error.message,true);}
}
function shapeOptions(select,shapes,selected='HV') {
  select.replaceChildren(...shapes.map(s=>new Option(`${s.name} · ${s.id}`,s.id)));
  if (shapes.some(s=>s.id===selected)) select.value=selected;
  select.disabled=!shapes.length;
}
function shapeChips(shapes,ancestors=false) {
  return shapes.length ? shapes.map(s=>`<a class="chip" data-shape="${esc(s.id)}" href="/shapes/${encodeURIComponent(s.id)}">${esc(s.name)}${ancestors?`<small>${esc(s.distance)} cạnh IS_A</small>`:''}</a>`).join('') : '<p class="muted">Không có quan hệ phân loại ở mục này.</p>';
}
async function dashboard() {
  const graph=new KnowledgeGraph('taxonomy');
  graph.load('/api/graph/taxonomy',true);
  try {
    const stats=await api('/api/stats');
    const fields=[['Shape · Loại hình',stats.node_counts.Shape],['Property · Tính chất',stats.node_counts.Property],['Condition · Dấu hiệu',stats.node_counts.Condition],['Tổng node',stats.total_nodes],['Tổng relationship',stats.total_relationships]];
    $('stats').innerHTML=fields.map(([name,value],i)=>`<article class="stat ${i>2?'accent':''}"><strong>${esc(value)}</strong><span>${esc(name)}</span></article>`).join('');
    state('stats-state','');
  } catch(error) { $('stats').replaceChildren(); state('stats-state',error.message,true); }
}
async function shapesPage() {
  let version=0;
  async function load(query='') {
    const current=++version;
    $('shape-list').replaceChildren(); state('shapes-state',query?'Đang tìm…':'Đang tải các loại hình…');
    try {
      const data=await api(query?`/api/search?${new URLSearchParams({q:query})}`:'/api/shapes');
      if (current!==version) return;
      const shapes=query?data.results:data;
      $('shape-list').innerHTML=shapes.map(s=>`<article class="shape-card" data-shape="${esc(s.id)}"><span class="badge">${esc(s.id)} · Shape</span><h2>${esc(s.name)}</h2><p>${esc(s.definition)}</p><a href="/shapes/${encodeURIComponent(s.id)}">Xem chi tiết →</a></article>`).join('');
      state('shapes-state',shapes.length?`${shapes.length} loại hình${query?' phù hợp với “'+query+'”':''}.`:`Không tìm thấy loại hình với từ khóa “${query}”.`);
    } catch(error) { if(current===version) state('shapes-state',error.message,true); }
  }
  $('search-form').addEventListener('submit',event=>{event.preventDefault();load($('search-input').value.trim());});
  $('search-reset').addEventListener('click',()=>{$('search-input').value='';load();});
  await load();
}
async function detailPage() {
  const id=document.body.dataset.shapeId;
  try {
    const data=await api(`/api/shapes/${encodeURIComponent(id)}`), shape=data.shape;
    $('shape-name').textContent=shape.name; document.title=`${shape.name} · Tứ giác & Neo4j`;
    $('shape-code').textContent=`${shape.id} · SHAPE`; $('shape-definition').textContent=shape.definition;
    $('parents').innerHTML=shapeChips(data.direct_parents); $('ancestors').innerHTML=shapeChips(data.ancestors,true);
    $('property-summary').textContent=`${data.effective_properties.length} tính chất · ${data.direct_properties.length} trực tiếp`;
    // diagonal_angle thuộc nhóm Đường chéo, vẫn giữ ghi chú giao thoa với góc.
    const groups=[['side','Cạnh'],['angle','Góc'],['diagonal','Đường chéo'],['structure','Cấu trúc']];
    $('properties').innerHTML=groups.map(([key,title])=>{
      const properties=data.effective_properties.filter(p=>(p.category==='diagonal_angle'?'diagonal':p.category)===key);
      if(!properties.length) return '';
      return `<section class="property-group"><h3>${title} <span class="badge">${properties.length}</span></h3>${properties.map(p=>`<article class="property-item" data-property="${esc(p.id)}"><div><h4>${esc(p.name)}</h4><p>${esc(p.description)}</p><p>Nguồn khai báo: ${p.declared_at.map(s=>`<a href="/shapes/${encodeURIComponent(s.id)}">${esc(s.name)}</a>`).join(', ')}</p>${p.category==='diagonal_angle'?'<p>Liên quan đường chéo và góc.</p>':''}</div><span class="badge">${p.direct&&p.inherited?'Trực tiếp & kế thừa':p.direct?'Trực tiếp':'Kế thừa'}</span><details><summary>Xem đường tới nguồn khai báo</summary><ul class="path-list">${p.inheritance_paths.map(path=>`<li>${path.shape_names.map(esc).join(' → ')} → ${esc(p.name)}</li>`).join('')}</ul></details></article>`).join('')}</section>`;
    }).join('');
    $('conditions').innerHTML=data.conditions.length?data.conditions.map((condition,index)=>`${index?'<div class="or-divider">HOẶC · OR</div>':''}<article class="condition-card" data-condition="${esc(condition.condition_id)}"><span class="badge">${esc(condition.condition_id)}</span><h3>${esc(condition.name)}</h3><div class="condition-expression"><span class="condition-term">${esc(condition.required_shape.name)}</span>${condition.required_properties.map(p=>`<span class="logic">VÀ · AND</span><span class="condition-term">${esc(p.name)}</span>`).join('')}<span class="logic">⇒</span><strong>${esc(shape.name)}</strong></div><p>${esc(condition.explanation || condition.statement)}</p></article>`).join(''):'<p class="state">Đây là khái niệm gốc, chưa có quy tắc nhận biết riêng trong dataset.</p>';
    $('detail-content').hidden=false; state('detail-state','');
    const graph=new KnowledgeGraph('detail-graph');
    const load=()=>graph.load(`/api/graph/neighborhood/${encodeURIComponent(shape.id)}?depth=${encodeURIComponent($('detail-depth').value)}`);
    $('detail-graph-form').addEventListener('submit',event=>{event.preventDefault();load();});
    await load();
  } catch(error) { $('detail-content').hidden=true; state('detail-state',error.message,true); }
}
async function graphPage() {
  const graph=new KnowledgeGraph('explorer');
  const load=()=>graph.load(`/api/graph/neighborhood/${encodeURIComponent($('graph-shape').value)}?depth=${encodeURIComponent($('graph-depth').value)}`);
  $('graph-form').addEventListener('submit',event=>{event.preventDefault();load();});
  $('graph-taxonomy').addEventListener('click',()=>graph.load('/api/graph/taxonomy',true));
  try {
    shapeOptions($('graph-shape'),await api('/api/shapes'));
    $('graph-load').disabled=$('graph-shape').disabled;
    if (!$('graph-shape').disabled) await load(); else graph.clear('Chưa có loại hình nào trong database.');
  } catch(error) {graph.clear(error.message,true);}
}
function renderValue(value) {
  if(value===null || value===undefined) return '—';
  if(Array.isArray(value)) {
    if (value.length && value.every(v=>v && typeof v==='object' && v.label)) return `<details><summary>${value.length} node</summary>${value.map(v=>esc(v.label)).join('<br>')}</details>`;
    if (value.length && value.every(v=>v && typeof v==='object' && v.from)) return `<details><summary>${value.length} relationship</summary>${value.map(v=>`${esc(v.from)} → ${esc(v.type)} → ${esc(v.to)}`).join('<br>')}</details>`;
    return value.map(v=>esc(typeof v==='object'?JSON.stringify(v):v)).join(' → ');
  }
  if(typeof value==='object') {
    if(value.nodes && value.edges) return esc(value.nodes.map(n=>n.label).join(' → '));
    if(value.label) return esc(value.label);
    return `<details><summary>Xem nội dung</summary><pre>${esc(JSON.stringify(value,null,2))}</pre></details>`;
  }
  return esc(value);
}
// Chú giải cách đọc cột, không chứa bản sao kết quả database.
const QUERY_EXPLANATIONS={
  Q01:'Một dòng chứa tập node và relationship của project. Mở các ô để xem danh sách hoặc khám phá graph bên dưới.',
  Q02:'Mỗi dòng là một Property hiệu lực. declared_at liệt kê loại hình khai báo; DISTINCT gộp tính chất gặp qua nhiều đường IS_A.',
  Q03:'Chỉ các hình nối từ hình được chọn bằng đúng một cạnh IS_A. Không bao gồm tổ tiên xa hơn hoặc ngữ cảnh của Condition.',
  Q04:'Mỗi tổ tiên xuất hiện một lần dù có nhiều đường IS_A tới đó. Không bao gồm chính hình được chọn.',
  Q05:'Duyệt ngược IS_A để tìm các trường hợp đặc biệt. Hình bình hành gốc không được tính là trường hợp đặc biệt của chính nó.',
  Q06:'Kiểm tra tính chất bốn cạnh bằng nhau ở chính hình hoặc tổ tiên; mỗi dòng là một loại hình thỏa mãn.',
  Q07:'Kiểm tra tính chất bốn góc vuông qua IS_A và HAS_PROPERTY, bao gồm tính chất kế thừa.',
  Q08:'Các hình ở nhánh khác nhau vẫn có thể chia sẻ cùng một Property; kết quả không khẳng định quan hệ IS_A giữa chúng.',
  Q09:'node_ids theo thứ tự duyệt từ Tứ giác tới hình được chọn; edge_count là số cạnh. Mũi tên trên graph vẫn theo chiều IS_A từ hình đặc biệt tới hình tổng quát.',
  Q10:'Mỗi dòng là một Property có trong cả hai tập tính chất hiệu lực của hình vuông và hình chữ nhật.',
  Q11:'Mỗi dòng là một Property có trong cả hai tập tính chất hiệu lực của hình vuông và hình thoi.',
  Q12:'Hai tính chất đường chéo phải đồng thời có hiệu lực cho cùng một loại hình: vuông góc VÀ chia đôi nhau.',
  Q13:'Các cột phân loại cạnh vào và ra của từng Shape. direct_property_count chỉ đếm khai báo trực tiếp, không cộng tính chất kế thừa.',
  Q14:'Tập node đạt được bằng traversal không hướng trong bán kính đã chọn, kèm mọi cạnh giữa chúng. Đây là graph lân cận, không phải danh sách tổ tiên IS_A.',
  Q15:'Mỗi dòng là một đường từ hình vuông qua IS_A tới lớp khai báo, rồi HAS_PROPERTY tới tính chất chia đôi đường chéo. Graph gộp node/cạnh chung; bảng vẫn giữ các đường riêng.',
};
async function queriesPage() {
  let catalog, shapes, selected, version=0;
  const graph=new KnowledgeGraph('query-graph');
  const sources=JSON.parse($('query-sources').textContent);
  const clear=()=>{ $('query-table').replaceChildren(); $('query-result-count').hidden=true; $('query-graph-wrap').hidden=true; graph.clear(''); };
  function selectQuery() {
    ++version; selected=catalog.find(q=>q.id===$('query-select').value); clear();
    $('query-code').textContent=selected.id; $('query-title').textContent=selected.title;
    $('query-description').textContent=selected.description; $('cypher').textContent=sources[selected.id];
    $('query-explanation').textContent=QUERY_EXPLANATIONS[selected.id];
    $('query-parameters').replaceChildren();
    for (const [key,schema] of Object.entries(selected.parameter_schema)) {
      const label=document.createElement('label'), select=document.createElement('select');
      label.textContent=key==='shape_id'?'Loại hình':'Độ sâu'; select.name=key; select.id=`param-${key}`;
      if(key==='shape_id') shapeOptions(select,shapes,schema.default);
      else {select.replaceChildren(...schema.enum.map(v=>new Option(String(v),String(v))));select.value=String(schema.default);}
      label.append(select); $('query-parameters').append(label);
    }
    $('query-run').disabled=false; state('query-result-state','Chọn tham số và bấm “Chạy truy vấn”.');
  }
  $('query-select').addEventListener('change',selectQuery);
  $('query-parameters').addEventListener('change',()=>{++version;clear();$('query-run').disabled=false;state('query-result-state','Tham số đã đổi. Bấm “Chạy truy vấn” để lấy kết quả mới.');});
  $('query-form').addEventListener('submit',async event=>{
    event.preventDefault(); const current=++version, queryId=selected.id;
    clear(); $('query-run').disabled=true; state('query-result-state','Đang chạy truy vấn trên Neo4j…');
    const params=Object.fromEntries(new FormData(event.currentTarget));
    if(params.depth) params.depth=Number(params.depth);
    try {
      const data=await api(`/api/queries/${queryId}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(params)});
      if(current!==version) return;
      $('cypher').textContent=data.cypher;
      $('query-result-count').textContent=`${data.rows.length} dòng`; $('query-result-count').hidden=false;
      state('query-result-state',data.rows.length?'Truy vấn thành công. Kết quả đọc trực tiếp từ Neo4j.':'Truy vấn thành công nhưng không có dòng kết quả.');
      if(data.rows.length) {
        const columns=Object.keys(data.rows[0]);
        $('query-table').innerHTML=`<table><caption class="muted">${esc(queryId)} · ${esc(data.title)}</caption><thead><tr>${columns.map(c=>`<th scope="col">${esc(c)}</th>`).join('')}</tr></thead><tbody>${data.rows.map(row=>`<tr>${columns.map(c=>`<td>${renderValue(row[c])}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
      }
      if(data.graph.nodes.length) { $('query-graph-wrap').hidden=false; graph.render(data.graph,queryId==='Q09'); }
    } catch(error) {if(current===version) {clear();state('query-result-state',error.message,true);}}
    finally {if(current===version) $('query-run').disabled=false;}
  });
  try {
    [catalog,shapes]=await Promise.all([api('/api/queries'),api('/api/shapes')]);
    $('query-select').replaceChildren(...catalog.map(q=>new Option(`${q.id} · ${q.title}`,q.id)));
    $('query-workspace').hidden=false;state('queries-state','');selectQuery();
  } catch(error) {state('queries-state',error.message,true);}
}
document.addEventListener('DOMContentLoaded',()=>{
  $('connection').addEventListener('click',health);health();
  const pages={dashboard,shapes:shapesPage,detail:detailPage,graph:graphPage,queries:queriesPage};
  pages[document.body.dataset.page]?.();
});
