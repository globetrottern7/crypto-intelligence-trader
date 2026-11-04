import { NextRequest, NextResponse } from "next/server";

import {
  createDashboardSession,
  credentialsConfigured,
  isDashboardSessionValid,
  SESSION_COOKIE,
  SESSION_TTL_SECONDS,
  verifyDashboardPassword,
} from "@/lib/session";

export async function GET(request: NextRequest) {
  if (!isDashboardSessionValid(request.cookies.get(SESSION_COOKIE)?.value)) {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }
  return NextResponse.json({ authenticated: true });
}

export async function POST(request: NextRequest) {
  if (!credentialsConfigured()) {
    return NextResponse.json({ detail: "Dashboard credentials are not configured." }, { status: 503 });
  }
  let body: { password?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid request." }, { status: 400 });
  }
  if (typeof body.password !== "string" || !verifyDashboardPassword(body.password)) {
    return NextResponse.json({ detail: "Incorrect password." }, { status: 401 });
  }
  const response = NextResponse.json({ authenticated: true });
  response.cookies.set(SESSION_COOKIE, createDashboardSession(), {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/",
    maxAge: SESSION_TTL_SECONDS,
  });
  return response;
}

export async function DELETE() {
  const response = NextResponse.json({ authenticated: false });
  response.cookies.set(SESSION_COOKIE, "", { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "strict", path: "/", maxAge: 0 });
  return response;
}
