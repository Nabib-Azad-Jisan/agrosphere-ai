"use client";
import Link from "next/link";
import { motion } from "motion/react";
import {
  ArrowUpRight,
  Sprout,
  ScanLine,
  BrainCircuit,
  Radio,
  ArrowRight,
  Check,
  Droplets,
  Leaf,
  CloudSun,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useApp } from "@/components/providers";
export default function Landing() {
  const { t, language, update } = useApp();
  return (
    <div className="landing">
      <nav className="landing-nav">
        <Link href="/" className="brand">
          <span className="brand-mark">
            <Sprout size={26} />
          </span>
          <span>
            AgroSphere <span className="brand-ai">AI</span>
            <small>BY ZYNTRIX</small>
          </span>
        </Link>
        <div className="landing-links">
          <a href="#intelligence">{t("The intelligence", "প্রযুক্তি")}</a>
          <a href="#how-it-works">{t("How it works", "কীভাবে কাজ করে")}</a>
          <button
            className="language-button"
            onClick={() =>
              update({ language: language === "en" ? "bn" : "en" })
            }
          >
            {language === "en" ? "বাংলা" : "English"}
          </button>
          <Button asChild>
            <Link href="/dashboard">
              {t("Open workspace", "ড্যাশবোর্ড খুলুন")}
              <ArrowUpRight size={16} />
            </Link>
          </Button>
        </div>
      </nav>
      <main>
        <section className="landing-hero">
          <motion.div
            className="hero-copy"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="landing-kicker">
              <span className="live-dot" />
              {t("ROOTED IN DATA. GROWN WITH CARE.", "তথ্যে ভিত্তি। যত্নে বৃদ্ধি।")}
            </span>
            <h1>
              {t("Good growing", "ভালো চাষ")}
              <br />
              {t("starts with", "শুরু হয়")}
              <br />
              <em>{t("understanding.", "বোঝাপড়া থেকে।")}</em>
            </h1>
            <p>
              {t(
                "Meet the intelligence beneath your next harvest. Connect soil, weather, and a little foresight to make more thoughtful irrigation decisions.",
                "মাটি, আবহাওয়া ও আগাম তথ্য একসাথে বুঝুন। সেচের জন্য আরও ভালো সিদ্ধান্ত নিন।",
              )}
            </p>
            <div className="hero-actions">
              <Button asChild>
                <Link href="/dashboard">
                  {t("Explore the live demo", "সিমুলেশন ডেমো দেখুন")}
                  <ArrowUpRight size={18} />
                </Link>
              </Button>
              <a href="#how-it-works" className="quiet-link">
                {t("See how it works", "কীভাবে কাজ করে")}
                <ArrowRight size={17} />
              </a>
            </div>
            <div className="hero-trust">
              <span>
                <Check size={14} /> {t("Hardware optional", "হার্ডওয়্যার ছাড়াই")}
              </span>
              <span>
                <Check size={14} /> {t("Transparent forecasts", "স্বচ্ছ পূর্বাভাস")}
              </span>
              <span>
                <Check size={14} /> {t("Bangladesh first", "বাংলাদেশের জন্য")}
              </span>
            </div>
          </motion.div>
          <motion.div
            className="hero-visual"
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <div className="orbital orbital-one" />
            <div className="orbital orbital-two" />
            <div className="hero-plant">
              <div className="plant-stem" />
              <div className="plant-leaf leaf-one" />
              <div className="plant-leaf leaf-two" />
              <div className="plant-leaf leaf-three" />
              <div className="plant-leaf leaf-four" />
              <div className="soil-layer soil-one" />
              <div className="soil-layer soil-two" />
              <div className="soil-layer soil-three" />
              <div className="root-line root-one" />
              <div className="root-line root-two" />
              <div className="root-line root-three" />
            </div>
            <div className="float-card moisture-float">
              <span className="float-icon">
                <Droplets size={21} />
              </span>
              <div>
                <small>ROOTSENSE</small>
                <strong>{t("Know your root zone", "মাটির অবস্থা জানুন")}</strong>
                <span>
                  {t("Source-aware soil monitoring", "তথ্যের উৎসসহ পর্যবেক্ষণ")}
                </span>
              </div>
              <span className="signal-dot" />
            </div>
            <div className="float-card forecast-float">
              <span className="float-icon purple">
                <BrainCircuit size={21} />
              </span>
              <div>
                <small>AQUAMIND</small>
                <strong>
                  {t("A clearer next 24 hours", "আগামী ২৪ ঘণ্টার তথ্য")}
                </strong>
                <span>
                  {t("Explainable baseline outlooks", "কারণসহ বেসলাইন পূর্বাভাস")}
                </span>
              </div>
            </div>
            <span className="visual-label">
              <Radio size={13} /> SOFTWARE-FIRST · HARDWARE-READY
            </span>
          </motion.div>
        </section>
        <section className="landing-values">
          <span>{t("Built for the whole picture.", "পুরো তথ্য একসাথে।")}</span>
          <div>
            <Droplets size={19} />
            Soil awareness
          </div>
          <div>
            <CloudSun size={20} />
            Weather context
          </div>
          <div>
            <BrainCircuit size={20} />
            Thoughtful foresight
          </div>
          <div>
            <Leaf size={19} />
            Farmer first
          </div>
        </section>
        <section id="intelligence" className="landing-section">
          <span className="eyebrow">TWO MODULES. ONE CLEARER PICTURE.</span>
          <h2>
            {t("Understand today.", "আজকের অবস্থা বুঝুন।")}
            <br />
            <em>{t("Prepare for tomorrow.", "আগামীর জন্য প্রস্তুত হন।")}</em>
          </h2>
          <div className="feature-grid">
            <div className="feature-card">
              <span className="feature-number">01 / OBSERVE</span>
              <ScanLine size={35} />
              <h3>RootSense</h3>
              <p>
                {t(
                  "Follow moisture trends, understand data quality, and know when a sensor needs attention. Every observation keeps its source.",
                  "আর্দ্রতার পরিবর্তন, তথ্যের গুণমান ও সেন্সরের অবস্থা জানুন। প্রতিটি পাঠের উৎস সংরক্ষিত থাকে।",
                )}
              </p>
              <Link href="/rootsense">
                Explore monitoring <ArrowUpRight size={17} />
              </Link>
            </div>
            <div className="feature-card feature-dark">
              <span className="feature-number">02 / ANTICIPATE</span>
              <BrainCircuit size={35} />
              <h3>AquaMind</h3>
              <p>
                {t(
                  "Bring soil and forecast weather together for transparent 24-hour estimates and practical, understandable advisories.",
                  "মাটি ও আবহাওয়ার পূর্বাভাস একত্রে ব্যবহার করে ২৪ ঘণ্টার অনুমান ও সহজ পরামর্শ পান।",
                )}
              </p>
              <Link href="/aquamind">
                Explore intelligence <ArrowUpRight size={17} />
              </Link>
            </div>
          </div>
        </section>
        <section id="how-it-works" className="landing-section how-section">
          <div>
            <span className="eyebrow">A CONNECTED WAY TO GROW</span>
            <h2>
              {t("From observation", "পর্যবেক্ষণ থেকে")}
              <br />
              <em>{t("to understanding.", "বোঝাপড়া।")}</em>
            </h2>
            <p className="muted">
              Start with a clearly labeled simulation. Later, provision and
              calibrate an ESP32 station through the same API.
            </p>
          </div>
          <div className="steps">
            {[
              [
                "01",
                "Connect a source",
                "Simulated, historical, or calibrated hardware. One ingestion contract.",
              ],
              [
                "02",
                "See the whole picture",
                "Soil observations meet weather context and transparent baselines.",
              ],
              [
                "03",
                "Make a thoughtful decision",
                "Understand the evidence, inspect the root zone, and record what you find.",
              ],
            ].map(([n, title, desc]) => (
              <div key={n}>
                <span>{n}</span>
                <div>
                  <h3>{title}</h3>
                  <p>{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
        <section className="landing-cta">
          <Sprout size={37} />
          <h2>
            {t("Your next harvest starts", "পরের ফসলের শুরু")}
            <br />
            {t("with a better question.", "আরও ভালো তথ্য দিয়ে।")}
          </h2>
          <p>{t("What is your soil telling you?", "আপনার মাটি কী বলছে?")}</p>
          <Button asChild>
            <Link href="/dashboard">
              Open AgroSphere AI
              <ArrowUpRight size={18} />
            </Link>
          </Button>
          <small>Software-first demo · No field validation claimed</small>
        </section>
      </main>
      <footer className="landing-footer">
        <span>ZYNTRIX · Intelligence Beyond Boundaries</span>
        <span>AgroSphere AI · Bangladesh</span>
      </footer>
    </div>
  );
}
