
const SUPABASE_URL = "YOUR_PROJECT_URL";
const SUPABASE_KEY = "YOUR_PUBLISHABLE_KEY";

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
