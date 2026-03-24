import { useState } from "react";

export function useSortConfig(defaultKey = 'average_placement') {
  const [sortConfig, setSortConfig] = useState({ key: defaultKey, direction: 'asc' });

  const requestSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return <span className="sort-arrow-placeholder"></span>;
    return sortConfig.direction === 'asc' ? ' ▲' : ' ▼';
  };

  return { sortConfig, requestSort, getSortIcon };
}