
import { getStore } from "@netlify/blobs";

const DEFAULTS = [
    { id: 0, nazov: "Jablko", cena: 0.50, druh: "Ovocie", sklad: 5 },
    { id: 1, nazov: "Banán", cena: 0.45, druh: "Ovocie", sklad: 3 },
    { id: 2, nazov: "Mrkva", cena: 0.30, druh: "Zelenina", sklad: 4 },
    { id: 3, nazov: "Zemiak", cena: 0.25, druh: "Zelenina", sklad: 6 },
    { id: 4, nazov: "Mlieko", cena: 1.20, druh: "Mliečne", sklad: 2 }
];

function json(data, status = 200) {
    return new Response(JSON.stringify(data), {
        status,
        headers: {
            "Content-Type": "application/json",
            "Cache-Control": "no-store"
        }
    });
}

export default async function handler(request) {
    const store = getStore("shop");
    let products = await store.get("products", { type: "json" });

    if (!products) {
        products = DEFAULTS;
    }

    if (request.method === "GET") {
        const stock = {};
        products.forEach(p => stock[p.id] = p.sklad);
        return json(stock);
    }

    if (request.method !== "POST") {
        return json({ error: "Nepodporovaná metóda." }, 405);
    }

    let body;

    try {
        body = await request.json();
    } catch {
        return json({ error: "Neplatné údaje." }, 400);
    }

    if (!body.items || typeof body.items !== "object" ||
        Array.isArray(body.items)) {
        return json({ error: "Neplatný košík." }, 400);
    }

    for (const [id, quantity] of Object.entries(body.items)) {
        if (!/^\d+$/.test(id) ||
            !Number.isInteger(quantity) || quantity < 1) {
            return json({ error: "Neplatný produkt alebo počet." }, 400);
        }

        const product = products.find(p => p.id === Number(id));

        if (!product || product.sklad < quantity) {
            return json({ error: "Produkt už nie je na sklade." }, 409);
        }
    }

    for (const [id, quantity] of Object.entries(body.items)) {
        const product = products.find(p => p.id === Number(id));
        product.sklad -= quantity;
    }

    await store.setJSON("products", products);

    return json({ success: true });
}

export const config = { path: "/api/stock" };

