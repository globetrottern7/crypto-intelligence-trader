import { createHmac, timingSafeEqual } from "node:crypto";

export const SESSION_COOKIE = "dashboard_session";
export const SESSION_TTL_SECONDS = 12 * 60 * 60;

function safeEqual(left: string, right: string): boolean {
  const a = Buffer.from(left);
  const b = Buffer.from(right);
  return a.length === b.length && timingSafeEqual(a, b);
}

export function credentialsConfigured(): boolean {
  return Boolean(process.env.DASHBOARD_PASSWORD && process.env.SESSION_SECRET);
}

export function verifyDashboardPassword(candidate: string): boolean {
  const expected = process.env.DASHBOARD_PASSWORD ?? "";
  return credentialsConfigured() && safeEqual(candidate, expected);
}

export function createDashboardSession(): string {
  const expiry = String(Date.now() + SESSION_TTL_SECONDS * 1000);
  const signature = createHmac("sha256", process.env.SESSION_SECRET ?? "")
    .update(`dashboard-session:${expiry}`)
    .digest("hex");
  return `${expiry}.${signature}`;
}

export function isDashboardSessionValid(value?: string): boolean {
  if (process.env.NODE_ENV !== "production") return true;
  if (!credentialsConfigured() || !value) return false;
  const [expiry, signature, extra] = value.split(".");
  if (!expiry || !signature || extra !== undefined || !/^\d+$/.test(expiry)) return false;
  if (Number(expiry) <= Date.now()) return false;
  const expected = createHmac("sha256", process.env.SESSION_SECRET ?? "")
    .update(`dashboard-session:${expiry}`)
    .digest("hex");
  return safeEqual(signature, expected);
}
