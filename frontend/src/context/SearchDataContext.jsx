import { createContext, useState, useEffect } from "react";

// eslint-disable-next-line react-refresh/only-export-components
export const SearchDataContext = createContext([]);

export function SearchDataProvider({ children }) {
  const [searchPool, setSearchPool] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [champsData, artifacts, radiants] = await Promise.all([
          fetch("http://127.0.0.1:8000/champions").then(res => res.json()),
          fetch("http://127.0.0.1:8000/artifacts").then(res => res.json()),
          fetch("http://127.0.0.1:8000/radiant-items").then(res => res.json())
        ]);

        const combined = [
          ...(champsData.champions || []).map((champ) => ({
            id: champ.id,
            name: champ.name.trim(),
            type: 'champion',
            route: `/champions/${champ.id}`,
            icon: `/assets/champ_logos/${champ.id}.png`
          })),
          ...Object.entries(artifacts).map(([id, info]) => ({
            id,
            name: info.name,
            type: 'artifact',
            route: `/artifacts/${id}`,
            icon: `/assets/artifacts/${id}.png`
          })),
          ...Object.entries(radiants).map(([id, info]) => ({
            id,
            name: info.name,
            type: 'radiant',
            route: `/radiant-items/${id}`,
            icon: `/assets/radiant_items/${id}.png`
          }))
        ];

        setSearchPool(combined);
      } catch (e) {
        console.error("Search data fetch failed", e);
      }
    };
    fetchData();
  }, []);

  return (
    <SearchDataContext.Provider value={searchPool}>
      {children}
    </SearchDataContext.Provider>
  );
}