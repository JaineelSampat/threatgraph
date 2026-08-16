import { Route, Routes } from "react-router-dom";
import { Nav } from "./components/Nav";
import { Dashboard } from "./pages/Dashboard";
import { EntityDetail } from "./pages/EntityDetail";
import { Explorer } from "./pages/Explorer";
import { Investigate } from "./pages/Investigate";

export function App() {
  return (
    <div className="min-h-screen bg-bg">
      <Nav />
      <main>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/explorer" element={<Explorer />} />
          <Route path="/entity/:id" element={<EntityDetail />} />
          <Route path="/investigate" element={<Investigate />} />
        </Routes>
      </main>
    </div>
  );
}
