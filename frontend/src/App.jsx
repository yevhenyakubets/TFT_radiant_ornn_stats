import { Routes, Route } from "react-router-dom";
import ChampionPage from "./pages/ChampionPage";
import ChampionsListPage from "./pages/ChampionsListPage";
import ArtifactListPage from "./pages/ArtifactListPage";
import ArtifactPage from "./pages/ArtifactPage";

function App() {
  return (
    <Routes>
      <Route path="/champions" element={<ChampionsListPage />} />
      <Route path="/champions/:championName" element={<ChampionPage />} />
      <Route path="/artifacts" element={<ArtifactListPage />} />
      <Route path="/artifacts/:artifactName" element={<ArtifactPage />} />
    </Routes>
  );
}

export default App;
