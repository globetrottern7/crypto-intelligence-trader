import { NextResponse } from "next/server";

export async function GET() {
  try {
    const base = process.env.INTERNAL_API_BASE_URL;
    if (!base) return NextResponse.json({ status: "preview" }, { status: 503 });
    const response = await fetch(new URL("/health", base), { cache: "no-store" });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch {
    return NextResponse.json({ status: "unavailable" }, { status: 503 });
  }
}
