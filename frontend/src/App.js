import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { Layout } from "@/components/Layout";
import Landing from "@/pages/Landing";
import ModulePage from "@/pages/ModulePage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Landing />} />
          <Route path="/:module" element={<ModulePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
      <Toaster position="top-right" theme="dark" richColors />
    </BrowserRouter>
  );
}

export default App;
