document.getElementById("load").addEventListener("click", async () => {
  const res = await fetch("http://127.0.0.1:8000/champion/Ahri");
  const data = await res.json();
  document.getElementById("output").textContent =
    JSON.stringify(data, null, 2);
});