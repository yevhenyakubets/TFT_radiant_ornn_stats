import { Routes, Route, Outlet } from "react-router-dom";

import Header from "./components/Header";

import HomePage from "./pages/HomePage";
import ChampionPage from "./pages/ChampionPage";
import ChampionsListPage from "./pages/ChampionsListPage";
import ArtifactListPage from "./pages/ArtifactListPage";
import RadiantListPage from "./pages/RadiantListPage";
import ItemPage from "./pages/ItemPage";

function PageLayout() {
  return (
    <>
      <Header />
      <Outlet /> {/* This is where the specific page content will render */}
    </>
  );
}

function App() {
  return (
    <Routes>
      {/* Home page stays separate (No Header) */}
      <Route path="/" element={<HomePage />} />

      {/* Wrap everything else in the PageLayout */}
      <Route element={<PageLayout />}>
        <Route path="/champions" element={<ChampionsListPage />} />
        <Route path="/champions/:championId" element={<ChampionPage />} />
        <Route path="/artifacts" element={<ArtifactListPage />} />
        <Route path="/radiant-items" element={<RadiantListPage />} />
        <Route 
          path="/artifacts/:itemId" 
          element={<ItemPage key={window.location.pathname} />} 
        />
        <Route 
          path="/radiant-items/:itemId" 
          element={<ItemPage key={window.location.pathname} />} 
        />
        </Route>

      <Route path="*" element={<HomePage />} />
    </Routes>
  );
}

export default App;
