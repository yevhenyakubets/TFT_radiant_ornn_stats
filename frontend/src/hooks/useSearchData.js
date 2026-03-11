import { useContext } from "react";
import { SearchDataContext } from "../context/SearchDataContext.jsx";

export function useSearchData() {
  return useContext(SearchDataContext);
}