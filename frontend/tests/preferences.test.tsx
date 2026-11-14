import React from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from "@testing-library/react";
import { afterEach, expect, it } from "vitest";
import { Providers, useApp } from "@/components/providers";
import { api, moisture } from "@/lib/api";
import { sameOrigin } from "@/lib/security";

it("compares browser origins against the incoming host rather than Next.js internal hostname", () => {
  expect(sameOrigin("http://127.0.0.1:3000", "127.0.0.1:3000")).toBe(true);
  expect(sameOrigin("https://attacker.example", "127.0.0.1:3000")).toBe(false);
  expect(sameOrigin("invalid origin", "127.0.0.1:3000")).toBe(false);
});
afterEach(() => {
  cleanup();
  localStorage.clear();
});
function Preferences() {
  const { language, theme, update, t } = useApp();
  return (
    <>
      <p>{t("Your farm", "আপনার খামার")}</p>
      <button
        onClick={() => update({ language: language === "en" ? "bn" : "en" })}
      >
        Language
      </button>
      <button
        onClick={() => update({ theme: theme === "light" ? "dark" : "light" })}
      >
        Theme
      </button>
    </>
  );
}
it("switches Bengali copy and persists dark appearance", async () => {
  render(
    <Providers>
      <Preferences />
    </Providers>,
  );
  expect(screen.getByText("Your farm")).toBeInTheDocument();
  fireEvent.click(screen.getByText("Language"));
  expect(screen.getByText("আপনার খামার")).toBeInTheDocument();
  fireEvent.click(screen.getByText("Theme"));
  await waitFor(() =>
    expect(document.documentElement.dataset.theme).toBe("dark"),
  );
  expect(
    JSON.parse(localStorage.getItem("agrosphere-preferences")!).language,
  ).toBe("bn");
});
it("does not present missing VWC as a measurement", () => {
  expect(moisture(null)).toBe("—");
  expect(moisture(0.25)).toBe("25.0%");
});
it("exposes useful backend errors", async () => {
  const original = global.fetch;
  global.fetch = async () =>
    new Response(
      JSON.stringify({ error: { message: "Backend unavailable" } }),
      { status: 503 },
    );
  await expect(api("/health")).rejects.toThrow("Backend unavailable");
  global.fetch = original;
});
