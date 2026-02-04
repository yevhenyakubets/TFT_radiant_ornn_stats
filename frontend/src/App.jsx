import { Routes, Route } from "react-router-dom";
import ChampionPage from "./pages/ChampionPage";
import ChampionsListPage from "./pages/ChampionsListPage";
import ArtifactListPage from "./pages/ArtifactListPage";
import ArtifactPage from "./pages/ArtifactPage";
import RadiantListPage from "./pages/RadiantListPage";
import RadiantPage from "./pages/RadiantPage";

function App() {
  return (
    <Routes>
      <Route path="/champions" element={<ChampionsListPage />} />
      <Route path="/champions/:championId" element={<ChampionPage />} />
      <Route path="/artifacts" element={<ArtifactListPage />} />
      <Route path="/artifacts/:artifactId" element={<ArtifactPage />} />
      <Route path="/radiant-items" element={<RadiantListPage />} />
      <Route path="/radiant-items/:radiantId" element={<RadiantPage />} />
    </Routes>
  );
}

export default App;
