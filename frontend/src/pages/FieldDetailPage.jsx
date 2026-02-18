import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Droplets, Sprout, MapPin } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  LineChart, Line, AreaChart, Area,
} from 'recharts';
import PageHeader from '../components/PageHeader';
import { getField } from '../services/api';
import toast, { Toaster } from 'react-hot-toast';

const MONTHS_ORDER = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

export default function FieldDetailPage() {
  const { id } = useParams();
  const [field, setField] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getField(id)
      .then((res) => setField(res.data))
      .catch(() => toast.error('Erreur lors du chargement'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="w-8 h-8 border-4 border-palm-200 border-t-palm-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!field) {
    return <p className="text-stone-500">Parcelle non trouvée</p>;
  }

  // Préparer les données de rendement (annuel)
  const yieldData = (field.year_field_data || []).map((d) => ({
    year: d.year,
    yield: d.yield_tffb_ha,
    deposition: d.atmospheric_deposition,
  }));

  // Préparer les données pluviométrie (pour la dernière année dispo)
  const years = [...new Set((field.rainfall_data || []).map((r) => r.year))].sort();
  const lastYear = years[years.length - 1];
  const rainfallByMonth = MONTHS_ORDER.map((month) => {
    const entries = (field.rainfall_data || []).filter(
      (r) => r.month === month && r.year === lastYear
    );
    return {
      month: month.substring(0, 3),
      rainfall: entries.length > 0 ? entries[0].rainfall_mm : 0,
    };
  });

  // Préparer les données fertilisation (agrégées par année)
  const fertByYear = {};
  (field.fertilization_data || []).forEach((f) => {
    if (!fertByYear[f.year]) fertByYear[f.year] = { year: f.year, mineral: 0, organic: 0 };
    if (f.fertilization_type === 'Mineral') {
      fertByYear[f.year].mineral += f.quantity;
    } else {
      fertByYear[f.year].organic += f.quantity;
    }
  });
  const fertData = Object.values(fertByYear).sort((a, b) => a.year - b.year);

  return (
    <div>
      <Toaster position="top-right" />

      <Link
        to="/fields"
        className="inline-flex items-center gap-1.5 text-sm text-stone-500 hover:text-stone-700 mb-4 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Retour aux parcelles
      </Link>

      <PageHeader
        title={field.field_name}
        subtitle={`${field.localisation} · ${field.year_planting}–${field.end_field} (${field.end_field - field.year_planting} ans)`}
      />

      {/* Caractéristiques sol */}
      <div className="card p-6 mb-6">
        <h2 className="font-display text-lg text-stone-800 mb-4 flex items-center gap-2">
          <MapPin className="w-5 h-5 text-soil-500" />
          Caractéristiques du sol
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[
            { label: 'Texture', value: field.texture },
            { label: 'C organique', value: field.organic_carbon ? `${field.organic_carbon}%` : '—' },
            { label: 'pH', value: field.ph },
            { label: 'CEC', value: field.cec ? `${field.cec} cmol/kg` : '—' },
            { label: 'Pente', value: field.slope ? `${field.slope}%` : '—' },
            { label: 'Terrasses', value: field.terraces },
            { label: 'Eau initiale sol', value: field.initial_soil_water ? `${field.initial_soil_water} mm` : '—' },
            { label: 'Précédent', value: field.previous_palm || '—' },
          ].map(({ label, value }) => (
            <div key={label}>
              <p className="text-xs text-stone-400 uppercase tracking-wider">{label}</p>
              <p className="text-sm font-medium text-stone-800 mt-0.5">{value || '—'}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Graphique rendement */}
        <div className="card p-6">
          <h2 className="font-display text-lg text-stone-800 mb-4 flex items-center gap-2">
            <Sprout className="w-5 h-5 text-palm-500" />
            Rendement (tFFB/ha/an)
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={yieldData}>
              <defs>
                <linearGradient id="yieldGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3d8b41" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3d8b41" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis dataKey="year" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="yield"
                stroke="#3d8b41"
                strokeWidth={2}
                fill="url(#yieldGrad)"
                name="Rendement"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Graphique pluviométrie */}
        <div className="card p-6">
          <h2 className="font-display text-lg text-stone-800 mb-4 flex items-center gap-2">
            <Droplets className="w-5 h-5 text-sky-500" />
            Pluviométrie {lastYear} (mm/mois)
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={rainfallByMonth}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="rainfall" fill="#34adff" radius={[4, 4, 0, 0]} name="Pluie (mm)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Graphique fertilisation */}
        <div className="card p-6 lg:col-span-2">
          <h2 className="font-display text-lg text-stone-800 mb-4">
            Fertilisation par année
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={fertData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis dataKey="year" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="mineral" fill="#3d8b41" radius={[4, 4, 0, 0]} name="Minéral (kg/ha)" />
              <Bar dataKey="organic" fill="#be8f54" radius={[4, 4, 0, 0]} name="Organique (tFM/ha)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
