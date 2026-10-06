'use strict';
// Chỉ chuyển định dạng JSON API sang vis-network; không tái tạo quan hệ trong client.
window.KnowledgeGraph = class {
  constructor(id) {
    this.root = document.getElementById(id);
    this.canvas = this.root.querySelector('.network');
    this.status = this.root.querySelector('.graph-status');
    this.selection = this.root.querySelector('.graph-selection');
    this.picker = this.root.querySelector('.node-picker');
    this.fit = this.root.querySelector('.graph-fit');
    this.fit.addEventListener('click', () => this.network?.fit({animation:false}));
    this.picker.addEventListener('change', () => {
      if (this.picker.value) {
        this.network.selectNodes([this.picker.value]);
        this.showNode(this.picker.value);
      }
    });
    this.version = 0;
  }
  clear(message='Đang tải graph…', error=false) {
    this.network?.destroy(); this.network = null;
    this.canvas.style.visibility = 'visible';
    this.root.dataset.nodes = ''; this.root.dataset.edges = '';
    this.root.removeAttribute('data-ready');
    this.status.textContent = message;
    this.status.classList.toggle('error', error);
    this.selection.replaceChildren();
    this.picker.replaceChildren(new Option('Chọn node…', ''));
    this.picker.disabled = true; this.fit.disabled = true;
  }
  async load(url, taxonomy=false) {
    const version = ++this.version;
    this.clear();
    try {
      const graph = await window.api(url);
      if (version === this.version) this.render(graph, taxonomy);
    } catch (error) {
      if (version === this.version) this.clear(error.message, true);
    }
  }
  render(graph, taxonomy=false) {
    this.clear('');
    if (!graph.nodes.length) { this.clear('Không có node trong kết quả.'); return; }
    if (!window.vis?.Network) throw new Error('Không tải được thư viện graph. Kiểm tra các file trong app/static/vendor.');
    this.nodes = new Map(graph.nodes.map(n => [n.id, n]));
    this.edges = new Map(graph.edges.map(e => [e.id, e]));
    // Tooltip dùng textContent, tránh HTML từ dữ liệu được hiểu thành mã.
    const tooltip = text => { const element=document.createElement('div'); element.textContent=text; return element; };
    const nodes = graph.nodes.map(n => ({id:n.id, label:n.type==='Condition'?`Dấu hiệu\n${n.entity_id}`:window.wrapLabel(n.label,24), group:n.type,
      title:tooltip(`${n.type} · ${n.entity_id}\n${n.properties.definition || n.properties.description || n.properties.statement || n.label}`)}));
    const edges = graph.edges.map(e => ({...e, title:tooltip(`${this.nodes.get(e.from).label} → ${e.type} → ${this.nodes.get(e.to).label}`)}));
    this.canvas.style.visibility = 'hidden';
    this.network = new vis.Network(this.canvas, {nodes,edges}, {
      layout: taxonomy ? {hierarchical:{enabled:true,direction:'DU',sortMethod:'directed',levelSeparation:110,nodeSpacing:210,treeSpacing:240}} : {improvedLayout:true},
      physics: taxonomy ? false : {solver:'barnesHut',barnesHut:{gravitationalConstant:-7500,springLength:190,springConstant:0.025,avoidOverlap:0.5},stabilization:{iterations:180,fit:true}},
      nodes:{borderWidth:1.5,font:{face:'Segoe UI',size:16,color:'#20343e'},margin:14},
      groups:{Shape:{shape:'box',color:{background:'#d9eaf5',border:'#366384'}},Property:{shape:'ellipse',color:{background:'#def0e5',border:'#397252'}},Condition:{shape:'diamond',color:{background:'#fff0d1',border:'#976323'},margin:20}},
      edges:{arrows:{to:{enabled:true,scaleFactor:.65}},color:{color:'#889ba5',highlight:'#174e58'},font:{face:'Segoe UI',size:11,color:'#40545f',strokeWidth:3,strokeColor:'#fafcfd'},smooth:taxonomy?{enabled:true,type:'cubicBezier',forceDirection:'vertical',roundness:.4}:{enabled:true,type:'continuous'},width:1.3},
      interaction:{hover:true,tooltipDelay:200,keyboard:{enabled:true,bindToWindow:false},zoomView:true,dragView:true},
    });
    const ready = () => {
      this.network?.fit({animation:false});
      this.canvas.style.visibility='visible'; this.root.dataset.ready='true';
      this.fit.disabled=false;
      this.status.textContent=`${graph.nodes.length} node · ${graph.edges.length} relationship · ${taxonomy?'Phân loại IS_A':'Lân cận / kết quả traversal'}`;
    };
    // Bố cục ổn định trước khi hiển thị, rồi tắt physics để graph đứng yên.
    if (taxonomy) this.network.once('afterDrawing', ready);
    else this.network.once('stabilizationIterationsDone', () => {this.network?.setOptions({physics:false}); ready();});
    this.network.on('resize', () => {
      const active = this.network;
      // Căn sau khi canvas cập nhật kích thước, tránh dùng transform của khung cũ.
      requestAnimationFrame(() => {if (active === this.network) active?.fit({animation:false});});
    });
    this.network.on('click', selected => {
      if (selected.nodes.length) this.showNode(selected.nodes[0]);
      else if (selected.edges.length) this.showEdge(selected.edges[0]);
    });
    for (const n of graph.nodes) this.picker.add(new Option(`${n.label} · ${n.type}`, n.id));
    this.picker.disabled = false;
    this.root.dataset.nodes = graph.nodes.length; this.root.dataset.edges = graph.edges.length;
    this.status.textContent = 'Đang sắp xếp bố cục graph…';
    this.selection.innerHTML = '<p class="muted">Bấm một node hoặc cạnh để xem nội dung.</p>';
    this.network.fit({animation:false});
  }
  showNode(id) {
    const n = this.nodes.get(id); if (!n) return;
    this.picker.value = id;
    const e = window.escapeHTML, p = n.properties;
    this.selection.innerHTML = `<span class="badge">${e(n.type)}</span><h3>${e(n.label)}</h3><code>${e(n.entity_id)}</code><p>${e(p.definition || p.description || p.statement || '')}</p>${p.explanation?`<p>${e(p.explanation)}</p>`:''}${p.logic?`<p>Logic: <strong>${e(p.logic)}</strong></p>`:''}${p.notation?`<p>${e(p.notation)}</p>`:''}${n.type==='Shape'?`<a href="/shapes/${encodeURIComponent(n.entity_id)}">Xem chi tiết loại hình →</a>`:''}`;
  }
  showEdge(id) {
    const edge = this.edges.get(id); if (!edge) return;
    this.picker.value = '';
    const meaning = {IS_A:'Là trường hợp đặc biệt của loại hình đích.',HAS_PROPERTY:'Khai báo tính chất trực tiếp của loại hình.',HAS_CONDITION:'Một dấu hiệu đủ để nhận biết loại hình nguồn.',REQUIRES_SHAPE:'Ngữ cảnh hình ban đầu của quy tắc.',REQUIRES_PROPERTY:'Giả thiết bổ sung cần thỏa mãn trong quy tắc.'};
    const e = window.escapeHTML;
    this.selection.innerHTML = `<span class="badge">Relationship</span><h3>${e(edge.type)}</h3><p>${e(this.nodes.get(edge.from).label)} → ${e(this.nodes.get(edge.to).label)}</p><p>${e(meaning[edge.type] || '')}</p>`;
  }
};
