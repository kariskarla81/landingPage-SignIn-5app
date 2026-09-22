import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider } from "@/context/AuthContext";
import RequireAuth from "@/components/RequireAuth";
import Login from "@/pages/Login";
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
import DkaLayout from "@/pages/dka/DkaLayout";
import DkaDashboard from "@/pages/dka/Dashboard";
import DkaNewTest from "@/pages/dka/NewTest";
import DkaHistory from "@/pages/dka/History";
import DkaTrend from "@/pages/dka/Trend";
import DkaResult from "@/pages/dka/Result";
import DkaScale from "@/pages/dka/Scale";
import CopperLayout from "@/pages/copper/CopperLayout";
import CopperDashboard from "@/pages/copper/Dashboard";
import CopperNewTest from "@/pages/copper/NewTest";
import CopperHistory from "@/pages/copper/History";
import CopperTrend from "@/pages/copper/Trend";
import CopperResult from "@/pages/copper/Result";
import CopperScale from "@/pages/copper/Scale";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          {/* Public landing page — no authentication required */}
          <Route path="/" element={<Landing />} />
          <Route element={<RequireAuth />}>
            <Route element={<Layout />}>
              <Route path="/khtt" element={<KhtLayout />}>
                <Route index element={<KhtDashboard />} />
                <Route path="new" element={<KhtNewTest />} />
                <Route path="history" element={<KhtHistory />} />
                <Route path="trend" element={<KhtTrend />} />
              </Route>
              <Route path="/khtt/result/:id" element={<KhtResult />} />
              <Route path="/khtt/color-scale" element={<KhtColorScale />} />
              <Route path="/rating-dka" element={<DkaLayout />}>
                <Route index element={<DkaDashboard />} />
                <Route path="new" element={<DkaNewTest />} />
                <Route path="history" element={<DkaHistory />} />
                <Route path="trend" element={<DkaTrend />} />
              </Route>
              <Route path="/rating-dka/result/:id" element={<DkaResult />} />
              <Route path="/rating-dka/scale" element={<DkaScale />} />
              <Route path="/copper-strip" element={<CopperLayout />}>
                <Route index element={<CopperDashboard />} />
                <Route path="new" element={<CopperNewTest />} />
                <Route path="history" element={<CopperHistory />} />
                <Route path="trend" element={<CopperTrend />} />
              </Route>
              <Route path="/copper-strip/result/:id" element={<CopperResult />} />
              <Route path="/copper-strip/scale" element={<CopperScale />} />
              <Route path="/:module" element={<ModulePage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Route>
        </Routes>
        <Toaster position="top-right" theme="dark" richColors />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
