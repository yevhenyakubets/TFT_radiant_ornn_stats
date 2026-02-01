import { Routes, Route } from "react-router-dom";
import ChampionPage from "./pages/ChampionPage";
import ChampionsListPage from "./pages/ChampionsListPage";

function App() {
  return (
    <Routes>
      <Route path="/champions" element={<ChampionsListPage />} />
      <Route path="/champions/:championName" element={<ChampionPage />} />
    </Routes>
  );
}

export default App;
