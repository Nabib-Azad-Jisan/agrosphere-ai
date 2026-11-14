import { test, expect } from "@playwright/test";

test("all management and reporting pages render without browser errors", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  for (const section of [
    "weather",
    "farms",
    "analytics",
    "notifications",
    "settings",
  ]) {
    await page.goto(`/${section}`);
    await expect(page.locator("main h1")).toBeVisible();
  }
  await page.goto("/devices");
  await page.getByLabel("Device ID", { exact: true }).fill("invalid id!");
  await page.getByLabel("Display name", { exact: true }).fill("Test station");
  await page
    .getByRole("combobox", { name: "Assigned plot", exact: true })
    .selectOption("tomato_plot_001");
  await page.getByRole("button", { name: "Provision device" }).click();
  await expect(
    page.getByText("id: Use letters, numbers, underscores or hyphens"),
  ).toBeVisible();
  expect(errors).toEqual([]);
});
test("landing, navigation, simulation, observations and forecast", async ({
  page,
  isMobile,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", {
      name: "Good growing starts with understanding.",
    }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Explore the live demo" }).click();
  await expect(
    page.getByRole("heading", { name: "Your farm, in focus." }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Open sensor center" }).click();
  await expect(
    page.getByRole("heading", { name: "A living demo, clearly labeled." }),
  ).toBeVisible();
  await page.getByLabel("Simulation speed").selectOption("15");
  const startedAt = Date.now();
  await page
    .getByRole("button", { name: "Start simulation", exact: true })
    .click();
  await expect(page.getByText("Running", { exact: true })).toBeVisible();
  await expect
    .poll(
      async () => {
        const r = await page.request.get(
          "/api/v1/plots/tomato_plot_001/status",
        );
        const reading = (await r.json()).reading;
        return (
          reading?.provenance === "synthetic" &&
          new Date(reading.timestamp).getTime() >= startedAt
        );
      },
      { timeout: 30000 },
    )
    .toBe(true);
  await page.getByRole("button", { name: "Pause", exact: true }).click();
  if (isMobile)
    await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("link", { name: "RootSense", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Listen to your soil." }),
  ).toBeVisible();
  await expect(
    page.getByText("Simulation", { exact: true }).first(),
  ).toBeVisible();
  if (isMobile)
    await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("link", { name: /AquaMind/ }).click();
  await expect(
    page.getByText("Not field validated", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Toggle theme" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.getByRole("button", { name: "Switch language" }).click();
  await expect(page.locator("html")).toHaveAttribute("lang", "bn");
  await expect(page.locator("body")).toHaveJSProperty(
    "scrollWidth",
    await page.locator("body").evaluate((el) => el.clientWidth),
  );
});
