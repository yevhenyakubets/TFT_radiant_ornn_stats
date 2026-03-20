import { Routes, Route, Outlet } from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";
import HomePage from "./pages/HomePage";
import ChampionPage from "./pages/ChampionPage";
import ChampionsListPage from "./pages/ChampionListPage";
import ItemPage from "./pages/ItemPage";
import ItemListPage from "./pages/ItemListPage";
import "./styles/App.css"

function PageLayout() {
  return (
    <>
      <Header />
      <Outlet />
      <Footer />
    </>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<><HomePage /><Footer /></>} />

      <Route element={<PageLayout />}>
        <Route path="/champions" element={<ChampionsListPage />} />
        <Route path="/champions/:championId" element={<ChampionPage />} />
        <Route path="/artifacts/:itemId" element={<ItemPage />} />
        <Route path="/radiant-items/:itemId" element={<ItemPage />} />
        <Route path="/radiant-items" element={<ItemListPage />} />
        <Route path="/artifacts" element={<ItemListPage />} />
      </Route>

      <Route path="*" element={<><HomePage /><Footer /></>} />
    </Routes>
  );
}

export default App;