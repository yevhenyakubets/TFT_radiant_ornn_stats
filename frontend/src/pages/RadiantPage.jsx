import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function RadiantPage() {
  const { radiantId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/radiant-items/${radiantId}`)
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      });
  }, [radiantId]);

  if (loading) return <div>Loading...</div>;
  if (data.error) return <div>{data.error}</div>;

  return (
    <div style={{ padding: "20px" }}>
      <h1>{data.name}</h1>

      <h2>Champions</h2>
      <table border="1" cellPadding="6">
        <thead>
          <tr>
            <th>Champion</th>
            <th>Frequency</th>
            <th>Avg placement</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data.champions).map(([champion, info]) => (
            <tr key={champion}>
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

export default RadiantPage;
