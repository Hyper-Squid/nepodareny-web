import { getStore } from "@netlify/blobs";

const DEFAULT_STOCK = { 0: 5, 1: 3, 2: 4, 3: 6, 4: 2 };

export default async (req) => {
  const store = getStore("shop");
  let stock = await store.get("stock", { type: "json" });

  if (!stock) {
    stock = DEFAULT_STOCK;
    await store.setJSON("stock", stock);
  }

  if (req.method === "POST") {
    const { items } = await req.json(); // e.g. { "0": 2, "4": 1 }

    for (const [id, qty] of Object.entries(items)) {
      if (!(id in stock) || !Number.isInteger(qty) || qty < 1 || stock[id] < qty) {
        return Response.json({ error: "Nedostatok na sklade", stock }, { status: 409 });
      }
    }
    for (const [id, qty] of Object.entries(items)) stock[id] -= qty;
    await store.setJSON("stock", stock);
  }

  return Response.json(stock);
};

export const config = { path: "/api/stock" };
