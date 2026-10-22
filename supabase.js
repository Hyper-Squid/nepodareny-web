// 1. Správna inicializácia Supabase klienta
const SUPABASE_URL = "https://qaondcjyzvipjvaejzqi.supabase.co"; // Odstránené /rest/v1/, Supabase si to pridá samo
const SUPABASE_KEY = "sb_publishable_WdryToMPqpsjK6Qcpi1I5g_-keCM_1c";

const supabase = Supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// 2. Funkcia na načítanie produktov z databázy hneď pri otvorení/refresnutí stránky
async function loadProductsFromDatabase() {
  const { data: products, error } = await supabase
    .from('products')
    .select('*');

  if (error) {
    console.error("Chyba pri načítaní produktov:", error.message);
    return;
  }

  // Uisti sa, že v index.html máš element s id="products-list"
  const productContainer = document.getElementById('products-list');
  if (!productContainer) {
    console.error("V HTML chýba element s id='products-list'!");
    return;
  }

  productContainer.innerHTML = ''; 

  products.forEach(product => {
    productContainer.innerHTML += `
      <div class="product" style="border: 1px solid #ccc; padding: 10px; margin: 10px 0;">
        <h3>${product.name}</h3>
        <p>Cena: ${product.price} €</p>
        <p>Na sklade: <span id="stock-${product.id}">${product.stock}</span></p>
        <button onclick="buyProduct('${product.id}', ${product.stock})">Kúpiť</button>
      </div>
    `;
  });
}

// 3. Nová funkcia, ktorá odpočíta kus z databázy po kliknutí na "Kúpiť"
async function buyProduct(productId, currentStock) {
  if (currentStock <= 0) {
    alert("Tento produkt je už vypredaný!");
    return;
  }

  // Odpočítame 1 kus priamo v Supabase tabuľke
  const { error } = await supabase
    .from('products')
    .update({ stock: currentStock - 1 })
    .eq('id', productId);

  if (error) {
    alert("Nákup zlyhal! Skontroluj RLS nastavenia v Supabase.");
    console.error(error.message);
  } else {
    alert("Produkt úspešne kúpený!");
    // Po úspešnom nákupe znovu načítame databázu, aby sa číslo na obrazovke zmenilo
    loadProductsFromDatabase();
  }
}

// Spustenie načítania hneď po tom, čo prehliadač spracuje HTML struktúru
document.addEventListener('DOMContentLoaded', loadProductsFromDatabase);

