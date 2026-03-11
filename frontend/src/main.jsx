import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./styles/index.css"
import { SearchDataProvider } from "./context/SearchDataContext.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <SearchDataProvider>
      <App />
    </SearchDataProvider>
  </BrowserRouter>
);
