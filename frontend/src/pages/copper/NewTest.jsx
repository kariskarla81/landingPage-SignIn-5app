import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Camera, ImageIcon, Loader2, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { defaultSampleId, uploadImage, useAnalyzeCopper } from "@/lib/copper/api";
import { CameraCapture } from "@/components/kht/capture";
import { AmberBtn } from "@/components/copper/ui";

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

export default function CopperNewTest() {
  const navigate = useNavigate();
  const galleryRef = useRef(null);
  const [stage, setStage] = useState("");
  const analyze = useAnalyzeCopper((sec) => setStage(`Running AI Vision analysis… ${sec}s`));
  const [imageUri, setImageUri] = useState(null);
  const [showCamera, setShowCamera] = useState(false);
  const [busy, setBusy] = useState(false);
  const [f, setF] = useState({ sampleId: defaultSampleId(), product: "Diesel Fuel B30", batch: "", operator: "", temperature: "100", duration: "3", remark: "" });
  const set = (k) => (v) => setF((s) => ({ ...s, [k]: v }));

  function onGalleryPick(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (file) setImageUri(URL.createObjectURL(file));
  }

  async function runAnalysis() {
    if (!imageUri) { toast.error("Ambil atau unggah foto copper strip dulu."); return; }
    setBusy(true);
    let step = "Upload foto";
    try {
      setStage("Uploading image…");
      const path = await uploadImage(imageUri);
      step = "Analisa AI";
      setStage("Running AI Vision analysis…");
      const result = await analyze.mutateAsync({
        image_path: path, sample_id: f.sampleId, product: f.product, batch: f.batch, operator: f.operator,
        temperature_c: Number(f.temperature) || 100, duration_hours: Number(f.duration) || 3, remark: f.remark,
      });
      toast.success(`Analisa selesai — kelas ${String(result.classification).toUpperCase()}`);
      setImageUri(null);
      set("sampleId")(defaultSampleId());
      navigate(`/copper-strip/result/${result.id}`);
    } catch (e) {
      toast.error(`${step} gagal: ${String(e?.message || "AI analysis failed.").slice(0, 110)}`);
    } finally {
      setBusy(false);
      setStage("");
    }
  }

  const pickBtn = (icon, label, onClick, testId) => (
    <button type="button" onClick={onClick} data-testid={testId} className="flex min-w-[120px] flex-col items-center gap-2 rounded-md border border-zinc-700 bg-zinc-800 px-6 py-4 hover:border-amber-500/50">
      {icon}<span className="font-mono text-xs font-bold tracking-widest text-zinc-50">{label}</span>
    </button>
  );

  return (
    <div className="flex flex-col gap-3 pb-24 animate-fade-up" data-testid="copper-new-test">
      <input ref={galleryRef} type="file" accept="image/*" className="hidden" onChange={onGalleryPick} data-testid="copper-gallery-input" />

      {imageUri ? (
        <div className="overflow-hidden rounded-xl border border-amber-500" data-testid="copper-image-preview-wrap">
          <img src={imageUri} alt="copper strip" className="h-64 w-full bg-zinc-800 object-cover" data-testid="copper-image-preview" />
          <div className="flex gap-2 bg-zinc-900 p-2">
            <button type="button" onClick={() => setShowCamera(true)} data-testid="copper-retake-camera" className="flex flex-1 items-center justify-center gap-2 rounded border border-zinc-700 bg-zinc-800 py-2 font-mono text-xs text-zinc-50 hover:bg-zinc-700"><Camera className="h-4 w-4" />Retake</button>
            <button type="button" onClick={() => galleryRef.current?.click()} data-testid="copper-change-gallery" className="flex flex-1 items-center justify-center gap-2 rounded border border-zinc-700 bg-zinc-800 py-2 font-mono text-xs text-zinc-50 hover:bg-zinc-700"><ImageIcon className="h-4 w-4" />Change</button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-4 rounded-xl border border-dashed border-zinc-600 bg-zinc-900 p-6" data-testid="copper-pick-box">
          <p className="font-mono text-xs text-zinc-300">Ambil atau unggah foto copper strip</p>
          <div className="flex gap-3">
            {pickBtn(<Camera className="h-6 w-6 text-amber-400" />, "CAMERA", () => setShowCamera(true), "copper-pick-camera")}
            {pickBtn(<ImageIcon className="h-6 w-6 text-amber-400" />, "GALLERY", () => galleryRef.current?.click(), "copper-pick-gallery")}
          </div>
        </div>
      )}

      <div className="mt-2 font-mono text-[11px] tracking-[0.15em] text-amber-500">SAMPLE INFORMATION</div>
      <Field label="Sample ID" value={f.sampleId} onChange={set("sampleId")} testId="copper-input-sample-id" />
      <Field label="Product / Fuel" value={f.product} onChange={set("product")} testId="copper-input-product" />
      <Field label="Batch / Lot No." value={f.batch} onChange={set("batch")} placeholder="LOT-…" testId="copper-input-batch" />
      <Field label="Operator" value={f.operator} onChange={set("operator")} placeholder="Nama" testId="copper-input-operator" />
      <div className="mt-2 font-mono text-[11px] tracking-[0.15em] text-amber-500">TEST CONDITION</div>
      <div className="flex gap-3">
        <Field label="Temp (°C)" value={f.temperature} onChange={set("temperature")} numeric testId="copper-input-temp" />
        <Field label="Duration (h)" value={f.duration} onChange={set("duration")} numeric testId="copper-input-duration" />
      </div>
      <Field label="Remark" value={f.remark} onChange={set("remark")} placeholder="Opsional" testId="copper-input-remark" />

      <div className="fixed bottom-0 left-0 right-0 z-20 border-t border-zinc-700 bg-zinc-900 px-4 py-3 lg:left-72">
        <div className="mx-auto max-w-3xl">
          <AmberBtn onClick={runAnalysis} disabled={busy} data-testid="copper-run-analysis" className={`h-14 w-full text-sm ${!imageUri || busy ? "opacity-50" : ""}`}>
            {busy ? <><Loader2 className="h-5 w-5 animate-spin" /><span data-testid="copper-analysis-stage">{stage || "PROCESSING…"}</span></> : <><Sparkles className="h-5 w-5" />RUN AI VISION ANALYSIS</>}
          </AmberBtn>
        </div>
      </div>

      <CameraCapture open={showCamera} onClose={() => setShowCamera(false)} onCapture={(uri) => { setShowCamera(false); setImageUri(uri); }} />
    </div>
  );
}
