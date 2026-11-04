import { NextRequest, NextResponse } from "next/server";

type RouteContext = { params: Promise<{ path: string[] }> };

export async function GET(request: NextRequest, context: RouteContext) {
  const base = process.env.INTERNAL_API_BASE_URL;
  if (!base) return NextResponse.json(
    { detail: "Backend URL is not configured. Dashboard is in preview mode." }, { status: 503 }
  );
  const { path } = await context.params;
  const isProbe = path.length === 1 && ["health", "ready"].includes(path[0]);
  const upstreamPath = isProbe ? `/${path[0]}` : `/api/v1/${path.map(encodeURIComponent).join("/")}`;
  const target = new URL(upstreamPath, base);
  request.nextUrl.searchParams.forEach((value, key) => target.searchParams.set(key, value));
  const headers = new Headers();
  if (process.env.BACKEND_API_TOKEN) headers.set("Authorization", `Bearer ${process.env.BACKEND_API_TOKEN}`);
  try {
    const response = await fetch(target, { headers, cache: "no-store" });
    return new NextResponse(await response.text(), {
      status: response.status,
      headers: { "Content-Type": response.headers.get("Content-Type") ?? "application/json" },
    });
  } catch {
    return NextResponse.json({ detail: "Backend service is unreachable." }, { status: 503 });
  }
}
