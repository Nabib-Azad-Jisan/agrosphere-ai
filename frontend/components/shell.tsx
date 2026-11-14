"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "motion/react";
import {
  Sprout,
  LayoutDashboard,
  ScanLine,
  BrainCircuit,
  CloudSun,
  Map,
  Radio,
  ChartNoAxesCombined,
  Bell,
  Settings,
  Menu,
  X,
  ArrowUpRight,
  Sun,
  Moon,
  Languages,
  ChevronDown,
} from "lucide-react";
import { useApp } from "./providers";
import { api, type Plot } from "@/lib/api";
const links = [
  ["dashboard", "Overview", "সারসংক্ষেপ", LayoutDashboard],
  ["rootsense", "RootSense", "রুটসেন্স", ScanLine],
  ["aquamind", "AquaMind", "অ্যাকুয়ামাইন্ড", BrainCircuit],
  ["weather", "Weather center", "আবহাওয়া", CloudSun],
  ["farms", "Farms & plots", "খামার ও জমি", Map],
  ["devices", "Sensor center", "সেন্সর কেন্দ্র", Radio],
  ["analytics", "Analytics & reports", "বিশ্লেষণ", ChartNoAxesCombined],
  ["notifications", "Notifications", "বিজ্ঞপ্তি", Bell],
  ["settings", "Settings", "সেটিংস", Settings],
] as const;
export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const { t, language, theme, plotId, update } = useApp();
  const [open, setOpen] = useState(false);
  const plots = useQuery({
    queryKey: ["plots"],
    queryFn: () => api<Plot[]>("/plots"),
  });
  return (
    <div className="app-shell">
      <aside className={`sidebar ${open ? "is-open" : ""}`}>
        <Link href="/" className="brand">
          <span className="brand-mark">
            <Sprout size={25} />
          </span>
          <span>
            AgroSphere<span className="brand-ai"> AI</span>
            <small>BY ZYNTRIX</small>
          </span>
        </Link>
        <button
          className="mobile-close icon-button"
          onClick={() => setOpen(false)}
          aria-label="Close navigation"
        >
          <X />
        </button>
        <div className="workspace-label">
          {t("YOUR WORKSPACE", "আপনার কর্মক্ষেত্র")}
        </div>
        <nav>
          {links.map(([slug, en, bn, Icon]) => (
            <Link
              key={slug}
              href={`/${slug}`}
              onClick={() => setOpen(false)}
              className={`nav-link ${path === `/${slug}` ? "active" : ""}`}
            >
              <Icon size={19} />
              {t(en, bn)}
              {slug === "aquamind" && <span className="tiny-tag">AI</span>}
            </Link>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="growth-art">
            <Sprout size={30} />
            <span>
              {t("Better insight.", "আরও ভালো তথ্য।")}
              <br />
              {t("Thoughtful growth.", "যত্নশীল চাষ।")}
            </span>
          </div>
          <p>{t("Intelligence Beyond Boundaries", "সীমানার বাইরে বুদ্ধিমত্তা")}</p>
          <Link href="/" className="back-link">
            {t("Explore AgroSphere", "AgroSphere দেখুন")}
            <ArrowUpRight size={15} />
          </Link>
        </div>
      </aside>
      {open && (
        <button
          className="scrim"
          aria-label="Close navigation"
          onClick={() => setOpen(false)}
        />
      )}
      <div className="main-column">
        <header className="topbar">
          <div className="topbar-start">
            <button
              className="icon-button mobile-menu"
              onClick={() => setOpen(true)}
              aria-label="Open navigation"
            >
              <Menu />
            </button>
            <span className="breadcrumb">
              {t("Workspace", "কর্মক্ষেত্র")}
              <span>/</span>
              <strong>
                {t(
                  links.find((x) => `/${x[0]}` === path)?.[1] || "Overview",
                  links.find((x) => `/${x[0]}` === path)?.[2] || "সারসংক্ষেপ",
                )}
              </strong>
            </span>
          </div>
          <div className="topbar-actions">
            <div className="plot-select">
              <Sprout size={16} />
              <select
                aria-label="Selected plot"
                value={plotId}
                onChange={(e) => update({ plotId: e.target.value })}
              >
                {plots.data?.length ? (
                  plots.data.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))
                ) : (
                  <option value={plotId}>Select plot</option>
                )}
              </select>
              <ChevronDown size={13} />
            </div>
            <button
              className="icon-button"
              aria-label="Switch language"
              onClick={() =>
                update({ language: language === "en" ? "bn" : "en" })
              }
            >
              <Languages size={19} />
              <span className="language-tag">
                {language === "en" ? "EN" : "বাং"}
              </span>
            </button>
            <button
              className="icon-button"
              aria-label="Toggle theme"
              onClick={() =>
                update({ theme: theme === "light" ? "dark" : "light" })
              }
            >
              {theme === "light" ? <Moon size={19} /> : <Sun size={19} />}
            </button>
            <Link className="avatar" href="/settings" aria-label="Settings">
              ZF
            </Link>
          </div>
        </header>
        <motion.main
          key={path}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.22 }}
          className="page-content"
        >
          {children}
        </motion.main>
        <footer className="app-footer">
          <span>© ZYNTRIX · AgroSphere AI</span>
          <span>
            {t(
              "Decision support. Always verify field conditions.",
              "সিদ্ধান্তে সহায়তা। মাঠের অবস্থা যাচাই করুন।",
            )}
          </span>
        </footer>
      </div>
    </div>
  );
}
