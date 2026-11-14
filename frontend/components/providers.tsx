"use client";
import { createContext, useContext, useState, useEffect } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MotionConfig } from "motion/react";
type Preferences = {
  language: "en" | "bn";
  theme: "light" | "dark";
  plotId: string;
  notifications: boolean;
};
type Context = Preferences & {
  update: (p: Partial<Preferences>) => void;
  t: (en: string, bn: string) => string;
};
const AppContext = createContext<Context | null>(null);
export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("Missing provider");
  return ctx;
}
export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { retry: 1, refetchInterval: 15000, staleTime: 5000 },
        },
      }),
  );
  const [prefs, setPrefs] = useState<Preferences>({
    language: "en",
    theme: "light",
    plotId: "tomato_plot_001",
    notifications: true,
  });
  useEffect(() => {
    const id = requestAnimationFrame(() => {
      try {
        const saved = localStorage.getItem("agrosphere-preferences");
        if (saved) setPrefs((p) => ({ ...p, ...JSON.parse(saved) }));
      } catch {
        /* invalid local preferences reset to defaults */
      }
    });
    return () => cancelAnimationFrame(id);
  }, []);
  useEffect(() => {
    document.documentElement.dataset.theme = prefs.theme;
    document.documentElement.lang = prefs.language;
  }, [prefs.theme, prefs.language]);
  const update = (p: Partial<Preferences>) =>
    setPrefs((old) => {
      const next = { ...old, ...p };
      localStorage.setItem("agrosphere-preferences", JSON.stringify(next));
      return next;
    });
  return (
    <QueryClientProvider client={client}>
      <AppContext.Provider
        value={{
          ...prefs,
          update,
          t: (en, bn) => (prefs.language === "bn" ? bn : en),
        }}
      >
        <MotionConfig reducedMotion="user">{children}</MotionConfig>
      </AppContext.Provider>
    </QueryClientProvider>
  );
}
