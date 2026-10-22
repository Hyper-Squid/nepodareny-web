
const SUPABASE_URL = "https://qaondcjyzvipjvaejzqi.supabase.co/rest/v1/";
const SUPABASE_KEY = "sb_publishable_WdryToMPqpsjK6Qcpi1I5g_-keCM_1c";

const db = window.supabase.createClient(
https://qaondcjyzvipjvaejzqi.supabase.co/rest/v1/,
sb_publishable_WdryToMPqpsjK6Qcpi1I5g_-keCM_1c
);

async function loadProducts() {
  const { data, error } = await db
    .from("products")
    .select("*");

  if (error) {
    console.error(error.message);
    return [];
  }

  console.log("Products:", data);
  return data;
}

loadProducts();


<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script src="supabase.js"></script>

// 1. Run this function immediately when the website opens/refreshes
async function loadProductsFromDatabase() {
  // Fetching the fresh inventory status from Supabase
  const { data: products, error } = await supabase
    .from('products')
    .select('*');

  if (error) {
    console.error("Error loading products:", error);
    return;
  }

  // 2. Clear your old HTML list and render the updated items dynamically
  const productContainer = document.getElementById('products-list');
  productContainer.innerHTML = ''; 

  products.forEach(product => {
    productContainer.innerHTML += `
      <div class="product">
        <h3>${product.name}</h3>
        <p>In Stock: ${product.stock}</p>
        <button onclick="buyProduct('${product.id}', ${product.stock})">Buy</button>
      </div>
    `;
  });
}

// Call the function as soon as the DOM content is loaded
document.addEventListener('DOMContentLoaded', loadProductsFromDatabase);

