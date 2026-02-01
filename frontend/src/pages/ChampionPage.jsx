import { useEffect, useState } from "react";

function ChampionPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/champions/Ornn")
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>{data.champion}</h1>

      <h2>Artifacts</h2>
      <table border="1" cellPadding="6">
        <thead>
          <tr>
            <th>Item</th>
            <th>Count</th>
            <th>Avg placement</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data.artifact).map(([item, info]) => (
            <tr key={item}>
              <td>{item}</td>
              <td>{info.count}</td>
              <td>{info.average_placement}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Radiant</h2>
      <table border="1" cellPadding="6">
        <thead>
          <tr>
            <th>Item</th>
            <th>Count</th>
            <th>Avg placement</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data.radiant).map(([item, info]) => (
            <tr key={item}>
              <td>{item}</td>
              <td>{info.count}</td>
              <td>{info.average_placement}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ChampionPage;
