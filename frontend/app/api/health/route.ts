import { NextResponse } from "next/server";

export async function GET() {
  const base = process.env.INTERNAL_API_BASE_URL ?? "http://127.0.0.1:8000";
  try {
    const response = await fetch(`${base}/health`, { cache: "no-store" });
    if (!response.ok) {
      return NextResponse.json({ status: "unavailable" }, { status: 503 });
    }
    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json({ status: "unavailable" }, { status: 503 });
  }
}
