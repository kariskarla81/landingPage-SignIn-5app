import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  FlaskConical,
  Beaker,
  Gauge,
  ArrowRight,
  Cloud,
  Cpu,
  Globe,
  Smartphone,
  ShieldCheck,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { MODULE_LIST } from "@/config/modules";

const ICONS = { khtt: FlaskConical, "copper-strip": Beaker, "rating-dka": Gauge };

const SERVICES = [
  { icon: Cloud, label: "SaaS" },
  { icon: Cpu, label: "IoT" },
  { icon: Globe, label: "Web App" },
  { icon: Smartphone, label: "Mobile App" },
];

const fade = {
  hidden: { opacity: 0, y: 20 },
  show: (i) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, delay: i * 0.08, ease: "easeOut" },
  }),
};

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div data-testid="landing-page" className="relative">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-zinc-800">
        <div
          className="absolute inset-0 opacity-[0.18]"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1695668548342-c0c1ad479aee?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600')",
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        />
        <div className="absolute inset-0 bg-zinc-950/80" />
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage:
              "linear-gradient(#71717a 1px, transparent 1px), linear-gradient(90deg, #71717a 1px, transparent 1px)",
            backgroundSize: "48px 48px",
          }}
        />

        <div className="relative mx-auto max-w-7xl px-6 py-24 lg:px-10 lg:py-32">
          <motion.div
            initial="hidden"
            animate="show"
            variants={fade}
            custom={0}
            className="inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/70 px-4 py-1.5 text-xs font-medium tracking-wide text-zinc-400"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
            Petroleum Laboratory Technology
          </motion.div>

          <motion.h1
            initial="hidden"
            animate="show"
            variants={fade}
            custom={1}
            className="font-heading mt-6 max-w-3xl text-5xl font-bold leading-[1.05] tracking-tight text-zinc-50"
          >
            Elastech <span className="text-amber-500">Production</span>
          </motion.h1>

          <motion.p
            initial="hidden"
            animate="show"
            variants={fade}
            custom={2}
            className="mt-5 max-w-xl text-base leading-relaxed text-zinc-400"
          >
            Perusahaan teknologi yang membangun solusi digital end-to-end —
            dari platform SaaS hingga perangkat IoT — serta menghadirkan suite
            perangkat lunak pengujian laboratorium minyak bumi yang presisi dan
            cerdas.
          </motion.p>

          <motion.div
            initial="hidden"
            animate="show"
            variants={fade}
            custom={3}
            className="mt-8 flex flex-wrap gap-3"
          >
            {SERVICES.map((s) => (
              <div
                key={s.label}
                className="flex items-center gap-2 rounded-md border border-zinc-800 bg-zinc-900/60 px-4 py-2 text-sm font-medium text-zinc-300"
              >
                <s.icon className="h-4 w-4 text-amber-500" />
                {s.label}
              </div>
            ))}
          </motion.div>

          <motion.div
            initial="hidden"
            animate="show"
            variants={fade}
            custom={4}
            className="mt-10"
          >
            <Button
              data-testid="hero-explore-btn"
              onClick={() => navigate("/khtt")}
              className="rounded-md bg-amber-500 font-medium text-zinc-950 hover:bg-amber-400"
            >
              Buka Lab Suite
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Modules */}
      <section className="mx-auto max-w-7xl px-6 py-16 lg:px-10">
        <div className="mb-8 flex items-end justify-between">
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-amber-500">
              Laboratory Modules
            </div>
            <h2 className="font-heading mt-2 text-2xl font-bold tracking-tight text-zinc-50 lg:text-3xl">
              Tools Pengujian Minyak Bumi
            </h2>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {MODULE_LIST.map((m, i) => {
            const Icon = ICONS[m.slug];
            return (
              <motion.button
                key={m.slug}
                initial="hidden"
                whileInView="show"
                viewport={{ once: true }}
                variants={fade}
                custom={i}
                data-testid={`module-card-${m.slug}`}
                onClick={() => navigate(`/${m.slug}`)}
                className="group flex flex-col rounded-lg border border-zinc-800 bg-zinc-900/40 p-6 text-left transition-colors duration-200 hover:border-amber-500/40 hover:bg-zinc-900/70"
              >
                <div className="flex h-11 w-11 items-center justify-center rounded-md border border-zinc-800 bg-zinc-950 text-amber-500 transition-colors duration-200 group-hover:border-amber-500/40">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="font-heading mt-5 text-lg font-semibold tracking-tight text-zinc-50">
                  {m.title}
                </h3>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-zinc-400">
                  {m.description}
                </p>
                <div className="mt-5 flex items-center gap-2 text-sm font-medium text-amber-500">
                  Mulai Pengujian
                  <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
                </div>
              </motion.button>
            );
          })}
        </div>

        {/* Feature strip */}
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            { icon: Activity, title: "Input & Rating", desc: "Form data sampel dan penilaian rating sesuai standar uji." },
            { icon: Cpu, title: "Analisa AI", desc: "Interpretasi hasil otomatis oleh AI ahli laboratorium." },
            { icon: ShieldCheck, title: "Export PDF", desc: "Laporan pengujian profesional siap cetak & arsip." },
          ].map((f, i) => (
            <div
              key={i}
              className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-6"
            >
              <f.icon className="h-5 w-5 text-zinc-500" />
              <div className="font-heading mt-4 text-base font-semibold text-zinc-100">
                {f.title}
              </div>
              <p className="mt-1.5 text-sm text-zinc-400">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
