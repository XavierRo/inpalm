import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import './index.css';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ImportPage from './pages/ImportPage';
import FieldsPage from './pages/FieldsPage';
import FieldDetailPage from './pages/FieldDetailPage';
import ParametersPage from './pages/ParametersPage';
import SimulationsPage from './pages/SimulationsPage';
import ResultsPage from './pages/ResultsPage';
import Mockup from './pages/Mockup';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/mockup" element={<Mockup />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="import" element={<ImportPage />} />
          <Route path="fields" element={<FieldsPage />} />
          <Route path="fields/:id" element={<FieldDetailPage />} />
          <Route path="parameters" element={<ParametersPage />} />
          <Route path="simulations" element={<SimulationsPage />} />
          <Route path="results/:simulationId?" element={<ResultsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
