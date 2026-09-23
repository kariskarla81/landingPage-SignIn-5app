import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Camera, ImageIcon, Loader2, ScanLine, Play } from "lucide-react";
import { toast } from "sonner";
import {
  uploadImage, ocrLabelWithPolling, useHtcbtSubmit, useHtcbtMethods, defaultSampleId,
} from "@/lib/htcbt/api";
import { CameraCapture } from "@/components/kht/capture";

const Field = ({ label, value, onChange, placeholder, numeric, testId }) => (
  <label className="flex flex-1 flex-col gap-1">
    <span className="font-mono text-[11px] text-zinc-300">{label}</span>
    <input
      data-testid={testId}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      inputMode={numeric ? "decimal" : "text"}
      className="h-11 rounded-md border border-zinc-700 bg-zinc-900 px-3 font-mono text-sm font-medium text-zinc-50 outline-none transition-colors placeholder:text-zinc-500 focus:border-amber-500"
    />
  </label>
);

export default function HtcbtNewSample() {
  const navigate = useNavigate();
  const galleryRef = useRef(null);
  const { data: methodsData } = useHtcbtMethods();
  const methods = methodsData?.methods || [];
  const submit = useHtcbtSubmit();

  const [imageUri, setImageUri] = useState(null);
  const [showCamera, setShowCamera] = useState(false);
  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState("");
  const [rawText, setRawText] = useState("");
  const [scanned, setScanned] = useState(false);
  const [imagePath, setImagePath] = useState(null);
  const [f, setF] = useState({ sampleId: "", operator: "", methodCode: "", temperature: "", duration: "" });
  const set = (k) => (v) => setF((s) => ({ ...s, [k]: v }));

  function onGalleryPick(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (file) { setImageUri(URL.createObjectURL(file)); setScanned(false); }
  }

  function applyMethod(code) {
    const m = methods.find((x) => x.code === code);
    setF((s) => ({
      ...s,
      methodCode: code,
      temperature: m ? String(m.temperature_c) : s.temperature,
      duration: m ? String(m.duration_hours) : s.duration,
    }));
  }

  async function runOcr() {
    if (!imageUri) { toast.error("Ambil atau unggah foto label dulu."); return; }
    setBusy(true);
    let step = "Upload foto";
    try {
      setStage("Uploading label\u2026");
      const path = await uploadImage(imageUri);
      step = "OCR AI Vision";
      setStage("Membaca tulisan tangan (AI Vision)\u2026");
      const r = await ocrLabelWithPolling(path, (sec) => setStage(`Membaca tulisan tangan\u2026 ${sec}s`));
      setImagePath(path);
      setRawText(r.raw_text || "");
      setF((s) => ({
        ...s,
        sampleId: r.sample_code || s.sampleId || defaultSampleId(),
        methodCode: r.method_code || s.methodCode,
        temperature: r.temperature_c != null ? String(r.temperature_c) : s.temperature,
        duration: r.duration_hours != null ? String(r.duration_hours) : s.duration,
      }));
      setScanned(true);
      toast.success("Label terbaca. Periksa data lalu mulai timer.");
    } catch (e) {
      toast.error(`${step} gagal: ${String(e?.message || "OCR gagal").slice(0, 120)}`);
    } finally {
      setBusy(false);
      setStage("");
    }
  }

  async function startTimer() {
    if (!f.sampleId.trim()) { toast.error("Kode sampel wajib diisi."); return; }
    if (!f.methodCode && !f.duration) { toast.error("Pilih metode atau isi durasi (jam)."); return; }
    setBusy(true);
    try {
      const res = await submit.mutateAsync({
        sample_code: f.sampleId.trim(),
        temperature_c: f.temperature ? Number(f.temperature) : null,
        duration_hours: f.duration ? Number(f.duration) : null,
        method_code: f.methodCode || null,
        operator: f.operator,
        image_path: imagePath,
        ocr_raw: rawText,
      });
      toast.success(res.created ? "Smart Timer dimulai!" : "Sampel ditambahkan ke batch aktif.");
      navigate("/htcbt");
    } catch (e) {
      toast.error(String(e?.message || "Gagal memulai timer").slice(0, 140));
    } finally {
      setBusy(false);
    }
  }

  const pickBtn = (icon, label, onClick, testId) => (
    <button type="button" onClick={onClick} data-testid={testId} className="flex min-w-[120px] flex-col items-center gap-2 rounded-md border border-zinc-700 bg-zinc-800 px-6 py-4 hover:border-amber-500/50">
      {icon}<span className="font-mono text-xs font-bold tracking-widest text-zinc-50">{label}</span>
    </button>
  );

  return (
    <div className="flex flex-col gap-3 pb-28 animate-fade-up" data-testid="htcbt-new-sample">
      <input ref={galleryRef} type="file" accept="image/*" className="hidden" onChange={onGalleryPick} data-testid="htcbt-gallery-input" />

      {imageUri ? (
        <div className="overflow-hidden rounded-xl border border-amber-500" data-testid="htcbt-image-preview-wrap">
          <img src={imageUri} alt="label sampel" className="h-56 w-full bg-zinc-800 object-cover" data-testid="htcbt-image-preview" />
          <div className="flex gap-2 bg-zinc-900 p-2">
            <button type="button" onClick={() => setShowCamera(true)} data-testid="htcbt-retake-camera" className="flex flex-1 items-center justify-center gap-2 rounded border border-zinc-700 bg-zinc-800 py-2 font-mono text-xs text-zinc-50 hover:bg-zinc-700"><Camera className="h-4 w-4" />Retake</button>
            <button type="button" onClick={() => galleryRef.current?.click()} data-testid="htcbt-change-gallery" className="flex flex-1 items-center justify-center gap-2 rounded border border-zinc-700 bg-zinc-800 py-2 font-mono text-xs text-zinc-50 hover:bg-zinc-700"><ImageIcon className="h-4 w-4" />Change</button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-4 rounded-xl border border-dashed border-zinc-600 bg-zinc-900 p-6" data-testid="htcbt-pick-box">
          <p className="text-center font-mono text-xs text-zinc-300">Ambil atau unggah foto label tulisan tangan sampel</p>
          <div className="flex gap-3">
            {pickBtn(<Camera className="h-6 w-6 text-amber-400" />, "CAMERA", () => setShowCamera(true), "htcbt-pick-camera")}
            {pickBtn(<ImageIcon className="h-6 w-6 text-amber-400" />, "GALLERY", () => galleryRef.current?.click(), "htcbt-pick-gallery")}
          </div>
        </div>
      )}

      {imageUri && !scanned && (
        <button
          type="button"
          onClick={runOcr}
          disabled={busy}
          data-testid="htcbt-run-ocr"
          className="flex h-12 items-center justify-center gap-2 rounded-md bg-amber-500 font-mono text-sm font-bold tracking-widest text-zinc-950 hover:bg-amber-400 disabled:opacity-50"
        >
          {busy ? <><Loader2 className="h-5 w-5 animate-spin" /><span data-testid="htcbt-ocr-stage">{stage || "MEMPROSES\u2026"}</span></> : <><ScanLine className="h-5 w-5" /> BACA LABEL (OCR)</>}
        </button>
      )}

      <div className="mt-1 font-mono text-[11px] tracking-[0.15em] text-amber-500">DATA SAMPEL {scanned ? "(hasil OCR \u2014 dapat diedit)" : ""}</div>
      <Field label="Kode Sampel" value={f.sampleId} onChange={set("sampleId")} placeholder="cth: HTCBT-001" testId="htcbt-input-sample-id" />
      <Field label="Operator" value={f.operator} onChange={set("operator")} placeholder="Nama analis (opsional)" testId="htcbt-input-operator" />

      <div className="mt-1 font-mono text-[11px] tracking-[0.15em] text-amber-500">METODE UJI</div>
      <div className="grid grid-cols-2 gap-2" data-testid="htcbt-method-picker">
        {methods.map((m) => (
          <button
            key={m.code}
            type="button"
            data-testid={`htcbt-method-${m.code}`}
            onClick={() => applyMethod(m.code)}
            className={`rounded-lg border p-3 text-left transition-colors ${f.methodCode === m.code ? "border-amber-500 bg-amber-500/10" : "border-zinc-700 bg-zinc-900 hover:border-amber-500/40"}`}
          >
            <div className="font-mono text-[12px] font-bold text-zinc-50">{m.duration_hours} jam</div>
            <div className="font-mono text-[11px] text-zinc-400">@ {m.temperature_c}\u00b0C</div>
          </button>
        ))}
      </div>
      <div className="flex gap-3">
        <Field label="Temp (\u00b0C)" value={f.temperature} onChange={set("temperature")} numeric testId="htcbt-input-temp" placeholder="135" />
        <Field label="Durasi (jam)" value={f.duration} onChange={set("duration")} numeric testId="htcbt-input-duration" placeholder="168" />
      </div>

      {rawText && (
        <div className="rounded-md border border-zinc-800 bg-zinc-950 p-3" data-testid="htcbt-raw-text">
          <div className="font-mono text-[10px] tracking-widest text-zinc-500">TEKS TERBACA</div>
          <p className="mt-1 whitespace-pre-wrap font-mono text-[11px] leading-4 text-zinc-400">{rawText}</p>
        </div>
      )}

      <div className="fixed bottom-0 left-0 right-0 z-20 border-t border-zinc-700 bg-zinc-900 px-4 py-3 lg:left-72">
        <div className="mx-auto max-w-3xl">
          <button
            onClick={startTimer}
            disabled={busy || submit.isPending}
            data-testid="htcbt-start-timer"
            className={`flex h-14 w-full items-center justify-center gap-2 rounded-md bg-amber-500 font-mono text-sm font-bold tracking-widest text-zinc-950 hover:bg-amber-400 ${busy || submit.isPending ? "opacity-50" : ""}`}
          >
            {submit.isPending ? <Loader2 className="h-5 w-5 animate-spin" /> : <Play className="h-5 w-5" />} MULAI / TAMBAH TIMER
          </button>
        </div>
      </div>

      <CameraCapture open={showCamera} onClose={() => setShowCamera(false)} onCapture={(uri) => { setShowCamera(false); setImageUri(uri); setScanned(false); }} />
    </div>
  );
}
