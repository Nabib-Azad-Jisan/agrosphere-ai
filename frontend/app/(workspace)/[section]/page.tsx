import { WorkspacePage } from "@/components/workspace-page";
import { notFound } from "next/navigation";
export function generateStaticParams() {
  return [
    "dashboard",
    "rootsense",
    "aquamind",
    "weather",
    "farms",
    "devices",
    "analytics",
    "notifications",
    "settings",
  ].map((section) => ({ section }));
}
export default async function Page({
  params,
}: {
  params: Promise<{ section: string }>;
}) {
  const { section } = await params;
  if (
    ![
      "dashboard",
      "rootsense",
      "aquamind",
      "weather",
      "farms",
      "devices",
      "analytics",
      "notifications",
      "settings",
    ].includes(section)
  )
    notFound();
  return <WorkspacePage section={section} />;
}
