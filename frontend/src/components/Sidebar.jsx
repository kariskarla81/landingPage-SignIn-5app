import React from "react";
import { NavLink } from "react-router-dom";
import { FlaskConical, Beaker, Gauge, Hexagon, Circle } from "lucide-react";
import { MODULE_LIST } from "@/config/modules";

const ICONS = {
  khtt: FlaskConical,
  "copper-strip": Beaker,
  "rating-dka": Gauge,
};

export const Sidebar = () => {
  return (
    <aside
      data-testid="app-sidebar"
      className="fixed left-0 top-0 z-30 hidden h-screen w-72 flex-col border-r border-zinc-800 bg-zinc-900 lg:flex"
    >
      <NavLink
        to="/"
        data-testid="sidebar-brand"
        className="flex items-center gap-3 border-b border-zinc-800 px-6 py-6 transition-colors hover:bg-zinc-800/40"
      >
        <div className="relative flex h-10 w-10 items-center justify-center rounded-md bg-amber-500">
          <Hexagon className="h-6 w-6 text-zinc-950" strokeWidth={2.5} />
        </div>
        <div className="leading-tight">
          <div className="font-heading text-lg font-bold tracking-tight text-zinc-50">
            Elastech
          </div>
          <div className="text-[10px] font-medium uppercase tracking-[0.25em] text-amber-500">
            Production
          </div>
        </div>
      </NavLink>

      <div className="px-4 py-6">
        <div className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-zinc-500">
          Laboratory Tools
        </div>
        <nav className="flex flex-col gap-1">
          {MODULE_LIST.map((m) => {
            const Icon = ICONS[m.slug] || Circle;
            return (
              <NavLink
                key={m.slug}
                to={`/${m.slug}`}
                data-testid={`nav-${m.slug}`}
                className={({ isActive }) =>
                  `group relative flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors duration-200 ${
                    isActive
                      ? "bg-zinc-800/70 text-zinc-50"
                      : "text-zinc-400 hover:bg-zinc-800/40 hover:text-zinc-100"
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <span
                      className={`absolute left-0 top-1/2 h-6 w-[3px] -translate-y-1/2 rounded-r bg-amber-500 transition-opacity duration-200 ${
                        isActive ? "opacity-100" : "opacity-0"
                      }`}
                    />
                    <Icon
                      className={`h-4 w-4 ${
                        isActive ? "text-amber-500" : "text-zinc-500 group-hover:text-zinc-300"
                      }`}
                    />
                    <span className="font-medium">{m.title}</span>
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      <div className="mt-auto border-t border-zinc-800 px-6 py-4">
        <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
          v1.0 · Lab Suite
        </div>
        <div className="mt-1 text-xs text-zinc-500">
          © {new Date().getFullYear()} Elastech Production
        </div>
      </div>
    </aside>
  );
};
