import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function ChampionPage() {
  const { championId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/champions/${championId}`)
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      });
  }, [championId]);

  if (loading) return <div>Loading...</div>;
  if (data.error) return <div>{data.error}</div>;

  return (
    <div style={{ padding: "20px" }}>
      <h1>{data.name}</h1>

      <h2>Artifacts</h2>
      <table border="1" cellPadding="6">
        <thead>
          <tr>
            <th>Item</th>
            <th>Frequency</th>
            <th>Avg placement</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data.artifacts).map(([item, info]) => (
            <tr key={item}>
              <td>{info.name}</td>
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
            <th>Frequency</th>
            <th>Avg placement</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data.radiants).map(([item, info]) => (
            <tr key={item}>
              <td>{info.name}</td>
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
