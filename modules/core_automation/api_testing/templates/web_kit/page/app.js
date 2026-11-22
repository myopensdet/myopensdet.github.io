// Template from myOpenSDET: https://myopensdet.github.io/
// The JavaScript in the browser. It calls the API in the background (AJAX, with fetch)
// and puts the answer on the page, without loading a new page.

function money(price) {
  return "£" + price.toFixed(2);
}

async function loadProducts() {
  const response = await fetch("/api/products");
  const products = await response.json();
  const list = document.querySelector("#products");
  const select = document.querySelector("#product");
  for (const product of products) {
    const item = document.createElement("li");
    const stock = product.stock > 0 ? "" : " (sold out)";
    item.textContent = product.title + " " + money(product.price) + stock;
    list.append(item);
    select.append(new Option(product.title, product.id));
  }
  document.querySelector("#status").textContent = products.length + " products";
}

async function addToCart(event) {
  event.preventDefault();
  const response = await fetch("/api/cart", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      product_id: Number(document.querySelector("#product").value),
      quantity: Number(document.querySelector("#quantity").value),
    }),
  });
  const answer = await response.json();
  document.querySelector("#message").textContent = response.ok
    ? "Added. Cart total: " + money(answer.total)
    : "Sorry: " + answer.error;
}

document.querySelector("#cart-form").addEventListener("submit", addToCart);
loadProducts();
