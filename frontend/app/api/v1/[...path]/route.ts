import { NextRequest, NextResponse } from "next/server";
import { sameOrigin } from "@/lib/security";
// Server-only local demo gateway. ADMIN_TOKEN is never serialized to the browser.
// Deployments require user authentication here before exposing this gateway beyond loopback.
async function proxy(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  const origin = request.headers.get("origin");
  if (
    !["GET", "HEAD"].includes(request.method) &&
    !sameOrigin(origin, request.headers.get("host"))
  )
    return NextResponse.json(
      { error: { message: "Cross-origin action rejected" } },
      { status: 403 },
    );
  const headers = new Headers({
    "Content-Type": request.headers.get("content-type") || "application/json",
  });
  if (process.env.ADMIN_TOKEN)
    headers.set("Authorization", `Bearer ${process.env.ADMIN_TOKEN}`);
  const deviceToken = request.headers.get("x-device-token");
  if (deviceToken) headers.set("X-Device-Token", deviceToken);
  try {
    const response = await fetch(
      `${process.env.BACKEND_URL || "http://127.0.0.1:8000"}/api/v1/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`,
      {
        method: request.method,
        headers,
        body: ["GET", "HEAD"].includes(request.method)
          ? undefined
          : await request.text(),
        signal: AbortSignal.timeout(45000),
        cache: "no-store",
      },
    );
    return new NextResponse(response.body, {
      status: response.status,
      headers: {
        "Content-Type":
          response.headers.get("content-type") || "application/json",
        ...(response.headers.get("content-disposition")
          ? {
              "Content-Disposition": response.headers.get(
                "content-disposition",
              )!,
            }
          : {}),
      },
    });
  } catch {
    return NextResponse.json(
      {
        error: {
          code: "backend_unavailable",
          message: "Backend unavailable. Start the API and database.",
        },
      },
      { status: 503 },
    );
  }
}
export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
