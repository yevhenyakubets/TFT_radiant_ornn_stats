import { createContext, useState, useEffect } from "react";
import { apiClient } from '../api';

// eslint-disable-next-line react-refresh/only-export-components
export const SearchDataContext = createContext([]);

export function SearchDataProvider({ children }) {
  const [searchPool, setSearchPool] = useState([]);

useEffect(() => {
  const fetchData = async () => {
    try {
      const [champsData, artifacts, radiants] = await Promise.all([
        apiClient.get("/champions"),
        apiClient.get("/artifacts"),
        apiClient.get("/radiant-items")
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