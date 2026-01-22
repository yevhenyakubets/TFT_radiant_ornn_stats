document.getElementById("load").addEventListener("click", async () => {
  const name = document.getElementById("champion").value;
  const res = await fetch(`http://127.0.0.1:8000/champion/${name}`);
  const data = await res.json();
  document.getElementById("output").textContent =
    JSON.stringify(data, null, 2);
});
