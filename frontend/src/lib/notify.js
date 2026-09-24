// Shared timer-finished notifications: browser notification + audible alarm.

let _audioCtx = null;

function getAudioCtx() {
  if (typeof window === "undefined") return null;
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return null;
  if (!_audioCtx) _audioCtx = new AC();
  return _audioCtx;
}

// Ask for browser notification permission (safe to call repeatedly).
export function requestNotifyPermission() {
  try {
    if (typeof Notification === "undefined") return;
    if (Notification.permission === "default") {
      Notification.requestPermission().catch(() => {});
    }
  } catch {
    /* ignore */
  }
}

// Show a browser (OS) notification if the user granted permission.
export function showBrowserNotification(title, body) {
  try {
    if (typeof Notification === "undefined") return;
    if (Notification.permission !== "granted") return;
    const n = new Notification(title, {
      body,
      tag: "lab-timer-done",
      requireInteraction: true,
    });
    n.onclick = () => {
      try {
        window.focus();
        n.close();
      } catch {
        /* ignore */
      }
    };
  } catch {
    /* ignore */
  }
}

// Play a repeating alarm beep sequence using the Web Audio API.
export function playAlarm({ beeps = 4, freq = 880, gap = 0.45 } = {}) {
  try {
    const ctx = getAudioCtx();
    if (!ctx) return;
    if (ctx.state === "suspended") ctx.resume().catch(() => {});
    const start = ctx.currentTime + 0.02;
    for (let i = 0; i < beeps; i += 1) {
      const t0 = start + i * gap;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "square";
      // alternate two tones for an "alarm" feel
      osc.frequency.setValueAtTime(i % 2 === 0 ? freq : freq * 0.75, t0);
      gain.gain.setValueAtTime(0.0001, t0);
      gain.gain.exponentialRampToValueAtTime(0.25, t0 + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.3);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(t0);
      osc.stop(t0 + 0.32);
    }
  } catch {
    /* ignore */
  }
}

// Fire everything at once when a countdown reaches zero.
export function notifyTimerDone(title, body) {
  playAlarm();
  showBrowserNotification(title, body);
}

// Resume the AudioContext on a user gesture so the alarm can play later.
export function unlockAudio() {
  const ctx = getAudioCtx();
  if (ctx && ctx.state === "suspended") ctx.resume().catch(() => {});
}
