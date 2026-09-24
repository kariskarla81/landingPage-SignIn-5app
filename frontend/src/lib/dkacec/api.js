import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { API } from "@/lib/api";

export { uploadImage } from "@/lib/kht/api";
export { fmtFull, fmtCountdown, remainingSeconds, defaultSampleId } from "@/lib/htcbt/api";

export const DKACEC = `${API}/dkacec`;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  if (!res.ok) {
    let d;
    try { d = await res.json(); } catch { /* ignore */ }
    throw new Error(d?.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

async function del(url) {
  const res = await fetch(url, { method: "DELETE" });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const useDkacecMethods = () =>
  useQuery({ queryKey: ["dkacec", "methods"], queryFn: () => getJSON(`${DKACEC}/methods`) });

export const useDkacecActive = () =>
  useQuery({ queryKey: ["dkacec", "active"], queryFn: () => getJSON(`${DKACEC}/active`), refetchInterval: 30000 });

export const useDkacecRuns = () =>
  useQuery({ queryKey: ["dkacec", "runs"], queryFn: () => getJSON(`${DKACEC}/runs`) });

export async function ocrLabelWithPolling(image_path, onTick) {
  const job = await postJSON(`${DKACEC}/ocr/start`, { image_path });
  const started = Date.now();
  const deadline = started + 4 * 60 * 1000;
  while (Date.now() < deadline) {
    await sleep(2000);
    onTick?.(Math.round((Date.now() - started) / 1000));
    let st = null;
    try { st = await getJSON(`${DKACEC}/ocr/jobs/${job.id}`); } catch { /* transient */ }
    if (!st) continue;
    if (st.status === "done") return st.result;
    if (st.status === "error") throw new Error(st.error || "OCR gagal membaca label.");
  }
  throw new Error("OCR memakan waktu terlalu lama. Coba foto yang lebih jelas.");
}

const invalidate = (qc) => qc.invalidateQueries({ queryKey: ["dkacec"] });

export function useDkacecSubmitBatch() {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (payload) => postJSON(`${DKACEC}/submit-batch`, payload), onSuccess: () => invalidate(qc) });
}

export function useDkacecComplete() {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (id) => postJSON(`${DKACEC}/runs/${id}/complete`), onSuccess: () => invalidate(qc) });
}

export function useDkacecStop() {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (id) => postJSON(`${DKACEC}/runs/${id}/stop`), onSuccess: () => invalidate(qc) });
}

export function useDkacecDeleteRun() {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (id) => del(`${DKACEC}/runs/${id}`), onSuccess: () => invalidate(qc) });
}

export function useDkacecRemoveSample() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, code }) => del(`${DKACEC}/runs/${id}/samples/${encodeURIComponent(code)}`),
    onSuccess: () => invalidate(qc),
  });
}
