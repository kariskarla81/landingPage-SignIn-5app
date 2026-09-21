import { fileUrl, imageToDataUri, isClear, statusLabel } from "@/lib/kht/api";
import { fmtDate, fmtDateTime, paramRows } from "@/lib/kht/format";

const esc = (s) =>
  String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const statusColor = (status) => (isClear(status) ? "#15803D" : "#C1220E");

const commonStyles = () => `
    @page { margin: 0; size: A4; }
    * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    body { font-family: -apple-system, Helvetica, Arial, sans-serif; color: #0A1420; margin: 0; padding: 0; }
    .page { padding: 40px 32px; page-break-after: always; }
    .page:last-child { page-break-after: auto; }
    h1 { color: #0A1420; margin: 0; font-size: 22px; }
    h2 { color: #0A1420; margin: 0; font-size: 16px; }
    .sub { color: #00898a; font-size: 11px; letter-spacing: 1.2px; font-weight: 700; }
    .rating { font-size: 56px; font-weight: 800; line-height: 1; }
    .badge { display: inline-block; padding: 4px 12px; border-radius: 4px; color: #fff; font-weight: bold; font-size: 12px; }
    .card { border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px; margin-top: 12px; }
    .card b { font-size: 12px; letter-spacing: 0.5px; color: #0A1420; }
    .card p { margin: 6px 0 0; font-size: 12px; color: #374151; line-height: 1.5; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    td, th { padding: 7px 4px; border-bottom: 1px solid #e5e7eb; font-size: 12px; text-align: left; }
    th { font-size: 10px; color: #64748b; letter-spacing: 0.5px; text-transform: uppercase; border-bottom: 1px solid #cbd5e1; }
    td.num { text-align: right; font-weight: bold; }
    .imgwrap { text-align: center; margin-top: 10px; }
    .imgwrap img { max-width: 100%; max-height: 260px; border-radius: 8px; object-fit: contain; }
    .caption { color: #64748b; font-size: 10px; margin-top: 4px; }
    .meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 16px; margin-top: 6px; }
    .meta-grid div { font-size: 11px; color: #374151; padding: 4px 0; border-bottom: 1px solid #eef2f7; }
    .meta-grid span { color: #64748b; margin-right: 6px; }
`;

const coverStyles = () => `
    .cover { padding: 44px 36px; page-break-after: always; }
    .cover-hero { background: linear-gradient(135deg,#0A1420 0%, #112033 60%, #0E3342 100%); color: #fff; padding: 28px; border-radius: 12px; }
    .cover-hero .brand { color: #00D2D3; font-size: 12px; letter-spacing: 2px; font-weight: 700; }
    .cover-hero h1 { color: #fff; font-size: 26px; margin-top: 6px; }
    .cover-hero .caption { color: #CBD5E1; font-size: 12px; margin-top: 4px; }
    .stat-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 18px; }
    .stat-cell { background: #F1F5F9; border-radius: 8px; padding: 10px; text-align: center; }
    .stat-cell .k { font-size: 9px; color: #64748b; letter-spacing: 1px; text-transform: uppercase; }
    .stat-cell .v { font-size: 22px; font-weight: 800; color: #0A1420; margin-top: 4px; }
    .summary { margin-top: 22px; }
    .summary h2 { font-size: 14px; letter-spacing: 1px; color: #00898a; text-transform: uppercase; margin-bottom: 6px; }
    .toc { width: 100%; border-collapse: collapse; }
    .toc th { background: #0A1420; color: #fff; font-size: 10px; letter-spacing: 0.5px; padding: 8px 6px; text-align: left; text-transform: uppercase; }
    .toc td { padding: 8px 6px; border-bottom: 1px solid #e5e7eb; font-size: 11px; color: #0A1420; }
    .toc .rate { font-weight: 800; }
    .foot { color: #64748b; font-size: 10px; text-align: center; margin-top: 22px; }
`;

function renderSamplePage(test, imgSrc, index, total) {
  const rows = paramRows(test.parameters)
    .map((r) => `<tr><td>${esc(r.label)}</td><td class="num">${esc(r.value)}</td></tr>`)
    .join("");
  const scolor = statusColor(test.status);
  return `
    <div class="page">
      <div style="display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1px solid #e5e7eb;padding-bottom:8px">
        <div>
          <div class="sub">KHT AI VISION · SAMPLE ${index}/${total}</div>
          <h1>${esc(test.meta.sample_id || "—")}</h1>
        </div>
        <div style="text-align:right">
          <div style="font-size:10px;color:#64748b">${esc(fmtDateTime(test.created_at))}</div>
          <div style="margin-top:4px"><span class="badge" style="background:${scolor}">${esc(statusLabel(test.status))}</span></div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:18px;margin-top:14px">
        <div>
          <span class="rating" style="color:${scolor}">${test.rating.toFixed(1)}</span>
          <span style="font-size:16px;color:#64748b"> /10</span>
        </div>
        <div style="flex:1">
          <div style="font-size:12px;color:#0A1420;font-weight:700">${esc(test.performance || "—")}</div>
          <div style="font-size:11px;color:#64748b;margin-top:2px">Confidence ${test.confidence.toFixed(1)}% · ${esc(test.deposit_level_label || "—")}</div>
        </div>
      </div>
      <div class="imgwrap">
        <img src="${esc(imgSrc)}" alt="sample"/>
        <div class="caption">Original sample photo — ${esc(test.meta.sample_id || "—")}</div>
      </div>
      <div class="card"><b>Deskripsi Kondisi</b><p>${esc(test.ai_summary || "—")}</p></div>
      <div class="card"><b>Rekomendasi</b><p>${esc(test.recommendation || "—")}</p></div>
      <div class="card"><b>Parameter Analysis</b><table>${rows}</table></div>
      <div class="card">
        <b>Test Information</b>
        <div class="meta-grid">
          <div><span>Product / Oil</span>${esc(test.meta.oil_type || "—")}</div>
          <div><span>Batch / Lot</span>${esc(test.meta.batch || "—")}</div>
          <div><span>Operator</span>${esc(test.meta.operator || "—")}</div>
          <div><span>Condition</span>${test.meta.temperature_c}&deg;C · ${test.meta.duration_hours}h</div>
          <div><span>Air / Oil Flow</span>${test.meta.air_flow} / ${test.meta.oil_flow} mL/min</div>
          <div><span>AI Model</span>${esc(test.ai_model)}</div>
        </div>
      </div>
    </div>`;
}

function renderCoverPage(tests) {
  const total = tests.length;
  const passed = tests.filter((t) => isClear(t.status)).length;
  const avg = total ? (tests.reduce((s, t) => s + t.rating, 0) / total).toFixed(1) : "0.0";
  const rows = tests
    .map((t, i) => {
      const c = statusColor(t.status);
      return `<tr><td>#${i + 1}</td><td>${esc(t.meta.sample_id || "—")}</td><td>${esc(t.meta.oil_type || "—")}</td><td>${esc(fmtDate(t.created_at))}</td><td class="rate" style="color:${c}">${t.rating.toFixed(1)}</td><td><span class="badge" style="background:${c}">${esc(statusLabel(t.status))}</span></td></tr>`;
    })
    .join("");
  return `
    <div class="cover">
      <div class="cover-hero">
        <div class="brand">KHT AI VISION · KOMATSU HOT TUBE TESTER</div>
        <h1>Combined Test Report</h1>
        <div class="caption">${total} sampel · Dihasilkan ${esc(fmtDateTime(new Date().toISOString()))}</div>
      </div>
      <div class="stat-row">
        <div class="stat-cell"><div class="k">Total Sampel</div><div class="v">${total}</div></div>
        <div class="stat-cell"><div class="k">Clear</div><div class="v" style="color:#15803D">${passed}</div></div>
        <div class="stat-cell"><div class="k">Tarnish</div><div class="v" style="color:#C1220E">${total - passed}</div></div>
        <div class="stat-cell"><div class="k">Rata-rata Rating</div><div class="v">${avg}</div></div>
      </div>
      <div class="summary">
        <h2>Ringkasan Sampel</h2>
        <table class="toc">
          <thead><tr><th>#</th><th>Sample ID</th><th>Oil / Product</th><th>Tanggal</th><th>Rating</th><th>Status</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      <div class="foot">Halaman rinci setiap sampel tersedia setelah lembar cover ini.</div>
    </div>`;
}

async function embedImage(test) {
  const url = fileUrl(test.image_path);
  return (await imageToDataUri(url)) || url;
}

export async function buildSingleReportHtml(test) {
  const imgSrc = await embedImage(test);
  const rows = paramRows(test.parameters)
    .map((r) => `<tr><td>${r.label}</td><td style="text-align:right;font-weight:bold">${r.value}</td></tr>`)
    .join("");
  const scolor = statusColor(test.status);
  return `
    <html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>KHT Report ${esc(test.meta.sample_id)}</title>
    <style>
      @page{margin:0;size:A4}
      *{-webkit-print-color-adjust:exact;print-color-adjust:exact}
      body{font-family:-apple-system,Helvetica,Arial;margin:0;padding:40px 32px;color:#0A1420}
      h1{color:#0A1420;margin:0} .sub{color:#00898a;font-size:12px;letter-spacing:1px}
      .rating{font-size:64px;font-weight:800;color:${scolor}}
      table{width:100%;border-collapse:collapse;margin-top:12px}
      td{padding:8px 4px;border-bottom:1px solid #e5e7eb;font-size:13px}
      .badge{display:inline-block;padding:4px 12px;border-radius:4px;color:#fff;font-weight:bold;background:${scolor}}
      .card{border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin-top:16px}
      img{width:100%;border-radius:8px;margin-top:12px}
    </style></head><body>
      <div class="sub">KHT AI VISION · KOMATSU HOT TUBE TESTER</div>
      <h1>Test Report — ${esc(test.meta.sample_id)}</h1>
      <div style="margin-top:12px">
        <span class="rating">${test.rating.toFixed(1)}</span>
        <span style="font-size:20px;color:#64748b">/10</span>
        &nbsp;&nbsp;<span class="badge">${statusLabel(test.status)}</span>
        <div style="color:#64748b;font-size:13px">${esc(test.performance)} · Confidence ${test.confidence.toFixed(1)}% · ${esc(test.deposit_level_label)}</div>
      </div>
      <img src="${esc(imgSrc)}" />
      <div style="color:#64748b;font-size:11px;margin-top:4px">Original sample photo — ${esc(test.meta.sample_id)}</div>
      <div class="card"><b>Deskripsi Kondisi</b><p style="font-size:13px;color:#374151">${esc(test.ai_summary || "-")}</p></div>
      <div class="card"><b>Rekomendasi</b><p style="font-size:13px;color:#374151">${esc(test.recommendation || "-")}</p></div>
      <div class="card"><b>Parameter Analysis</b><table>${rows}</table></div>
      <div class="card"><b>Test Information</b><table>
        <tr><td>Product / Oil</td><td style="text-align:right">${esc(test.meta.oil_type || "-")}</td></tr>
        <tr><td>Batch / Lot</td><td style="text-align:right">${esc(test.meta.batch || "-")}</td></tr>
        <tr><td>Operator</td><td style="text-align:right">${esc(test.meta.operator || "-")}</td></tr>
        <tr><td>Condition</td><td style="text-align:right">${test.meta.temperature_c}&deg;C / ${test.meta.duration_hours}h</td></tr>
        <tr><td>Air / Oil Flow</td><td style="text-align:right">${test.meta.air_flow} / ${test.meta.oil_flow} mL/min</td></tr>
        <tr><td>Analyzed</td><td style="text-align:right">${fmtDateTime(test.created_at)}</td></tr>
        <tr><td>AI Model</td><td style="text-align:right">${esc(test.ai_model)}</td></tr>
      </table></div>
    </body></html>`;
}

export async function buildCombinedReportHtml(tests) {
  const imgs = await Promise.all(tests.map(embedImage));
  const total = tests.length;
  const pages = tests.map((t, i) => renderSamplePage(t, imgs[i], i + 1, total)).join("\n");
  return `<!DOCTYPE html><html><head><meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>KHT Combined Report</title>
    <style>${commonStyles()}${coverStyles()}</style>
  </head><body>${renderCoverPage(tests)}${pages}</body></html>`;
}

export function printHtmlOnWeb(html) {
  const iframe = document.createElement("iframe");
  iframe.setAttribute("data-testid", "pdf-print-frame");
  Object.assign(iframe.style, { position: "fixed", right: "0", bottom: "0", width: "0", height: "0", border: "0" });
  document.body.appendChild(iframe);
  const cw = iframe.contentWindow;
  const doc = cw?.document;
  if (!cw || !doc) {
    iframe.remove();
    return;
  }
  doc.open();
  doc.write(html);
  doc.close();
  setTimeout(() => {
    try {
      cw.focus();
      cw.print();
    } catch {
      // ignore print errors
    }
    setTimeout(() => iframe.remove(), 1000);
  }, 400);
}
