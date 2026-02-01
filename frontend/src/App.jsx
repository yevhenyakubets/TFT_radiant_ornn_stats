import { Routes, Route } from "react-router-dom";
import ChampionPage from "./pages/ChampionPage";

function App() {
  return (
    <Routes>
      <Route path="/champions/:championName" element={<ChampionPage />} />
    </Routes>
  );
}

export default App;
