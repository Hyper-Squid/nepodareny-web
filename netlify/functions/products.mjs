import { getStore } from "@netlify/blobs";
import { timingSafeEqual } from "node:crypto";

const DEFAULTS = [
  { nazov: "Jablko", cena: 0.5, druh: "Ovocie", sklad: 5 },
  { nazov: "Banán", cena: 0.45, druh: "Ovocie", sklad: 3 },
  { nazov: "Mrkva", cena: 0.3, druh: "Zelenina", sklad: 4 },
  { nazov: "Zemiak", cena: 0.25, druh: "Zelenina", sklad: 6 },
  { nazov: "Mlieko", cena: 1.2, druh: "Mliečne", sklad: 2 },
];

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });

function isAdmin(req) {
  const expected = Netlify.env.get("ADMIN_PASSWORD");
  if (!expected) return false;
  const given = (req.headers.get("authorization") || "").replace("Bearer ", "");
  const a = Buffer.from(given);
  const b = Buffer.from(expected);
  return a.length === b.length && timingSafeEqual(a, b);
}

function clean(list) {
  if (!Array.isArray(list) || list.length > 500) return null;
  const out = [];
  for (const p of list) {
    const nazov = String(p.nazov ?? "").trim().slice(0, 80);
    const druh = String(p.druh ?? "").trim().slice(0, 40);
    const cena = Number(p.cena);
    const sklad = Math.floor(Number(p.sklad));
    if (!nazov || !isFinite(cena) || cena < 0 || !isFinite(sklad) || sklad < 0) return null;
    out.push({ id: out.length, nazov, druh, cena: Math.round(cena * 100) / 100, sklad });
  }
  return out;
}

export default async (req) => {
  const store = getStore("shop");

  if (req.method === "GET") {
    const saved = await store.get("products", { type: "json" });
    const list = saved ?? DEFAULTS.map((p, i) => ({ ...p, id: i }));
    return json(list);
  }

  if (req.method === "PUT") {
    if (!isAdmin(req)) return json({ error: "Nesprávne heslo" }, 401);
    let body;
    try { body = await req.json(); } catch { return json({ error: "Zlé dáta" }, 400); }
    const list = clean(body);
    if (!list) return json({ error: "Neplatné produkty" }, 400);
    await store.setJSON("products", list);
    return json(list);
  }

  if (req.method === "POST") {
    // login check
    return isAdmin(req) ? json({ ok: true }) : json({ error: "Nesprávne heslo" }, 401);
  }

  return json({ error: "Method not allowed" }, 405);
};

export const config = { path: "/api/products" };
