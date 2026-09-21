import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { Layout } from "@/components/Layout";
import Landing from "@/pages/Landing";
import ModulePage from "@/pages/ModulePage";
import KhtLayout from "@/pages/kht/KhtLayout";
import KhtDashboard from "@/pages/kht/Dashboard";
import KhtNewTest from "@/pages/kht/NewTest";
import KhtHistory from "@/pages/kht/History";
import KhtTrend from "@/pages/kht/Trend";
import KhtResult from "@/pages/kht/Result";
import KhtColorScale from "@/pages/kht/ColorScale";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Landing />} />
          <Route path="/khtt" element={<KhtLayout />}>
            <Route index element={<KhtDashboard />} />
            <Route path="new" element={<KhtNewTest />} />
            <Route path="history" element={<KhtHistory />} />
            <Route path="trend" element={<KhtTrend />} />
          </Route>
          <Route path="/khtt/result/:id" element={<KhtResult />} />
          <Route path="/khtt/color-scale" element={<KhtColorScale />} />
          <Route path="/:module" element={<ModulePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
      <Toaster position="top-right" theme="dark" richColors />
    </BrowserRouter>
  );
}

export default App;
