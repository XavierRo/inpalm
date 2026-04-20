import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, TrendingUp, TrendingDown, Scale, ChevronDown, ChevronRight } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  PieChart, Pie, Cell,
} from 'recharts';
import PageHeader from '../components/PageHeader';
import { getSimulationResults } from '../services/api';
import toast, { Toaster } from 'react-hot-toast';

const INPUT_COLORS = {
  n_initial_soil: '#1a3b1e',
  n_fixation: '#3d8b41',
  n_residues: '#87c48a',
  n_synthetic_fertilizer: '#5ba85f',
  n_organic_fertilizer: '#b8ddb9',
  n_atmospheric_deposition: '#dceedd',
};

const OUTPUT_COLORS = {
  n_volatilization: '#9a6234',
  n_leaching: '#34adff',
  n_palm_uptake: '#be8f54',
  n_n2o_emission: '#e74c3c',
  n_nox_emission: '#e67e22',
  n_n2_emission: '#f39c12',
  n_runoff: '#084171',
};

const INPUT_LABELS = {
  n_initial_soil: 'Sol initial',
  n_fixation: 'Fixation légumineuses',
  n_residues: 'Résidus',
  n_synthetic_fertilizer: 'Fert. synthétique',
  n_organic_fertilizer: 'Fert. organique',
  n_atmospheric_deposition: 'Dépôt atm.',
};

const OUTPUT_LABELS = {
  n_volatilization: 'Volatilisation NH₃',
  n_leaching: 'Lessivage NO₃⁻',
  n_palm_uptake: 'Captation palmier',
  n_n2o_emission: 'N₂O',
  n_nox_emission: 'NOx',
  n_n2_emission: 'N₂',
  n_runoff: 'Ruissellement',
};

const FLUX_LABELS = { ...INPUT_LABELS, ...OUTPUT_LABELS };

// Formatage d'une valeur intermédiaire
function formatVal(v) {
  if (v === null || v === undefined) return '—';
  if (typeof v === 'boolean') return v ? 'oui' : 'non';
  if (typeof v === 'number') return Math.round(v * 1000) / 1000;
  if (typeof v === 'object') return JSON.stringify(v);
  return String(v);
}

// Panneau de détail d'une année (intermediate_results)
function YearDetail({ intermediates, yr }) {
  if (!intermediates || Object.keys(intermediates).length === 0) {
    return <p className="text-xs text-stone-400 italic">Aucun détail intermédiaire disponible.</p>;
  }

  // On réorganise : entrées puis sorties
  const fluxOrder = [
    'n_initial_soil', 'n_fixation', 'n_residues',
    'n_synthetic_fertilizer', 'n_organic_fertilizer', 'n_atmospheric_deposition',
    'n_volatilization', 'n_leaching', 'n_palm_uptake',
    'n_n2o_emission', 'n_nox_emission', 'n_n2_emission', 'n_runoff',
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
      {fluxOrder.map((fluxKey) => {
        const data = intermediates[fluxKey];
        const value = yr[fluxKey];
        const isInput = fluxKey in INPUT_LABELS;
        if (!data) return null;

        // Aplatir les détails (ignorer les tableaux de détails pour la lisibilité)
        const entries = Object.entries(data).filter(
          ([k, v]) => k !== 'details' && typeof v !== 'object'
        );
        const details = data.details;

        return (
          <div key={fluxKey} className="bg-stone-50 rounded-lg p-3 border border-stone-200">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-semibold text-stone-700">
                {FLUX_LABELS[fluxKey] || fluxKey}
              </p>
              <span className={`text-xs font-mono font-bold ${isInput ? 'text-palm-600' : 'text-soil-600'}`}>
                {isInput ? '+' : '-'}{Math.round((value || 0) * 10) / 10} kg N/ha
              </span>
            </div>

            {entries.length > 0 && (
              <table className="w-full text-xs">
                <tbody>
                  {entries.map(([k, v]) => (
                    <tr key={k} className="border-t border-stone-200 first:border-0">
                      <td className="py-0.5 text-stone-500 pr-2">{k}</td>
                      <td className="py-0.5 text-stone-700 font-mono text-right">{formatVal(v)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Détail des apports de fertilisants */}
            {details && details.length > 0 && (
              <div className="mt-2 space-y-1">
                {details.map((d, i) => (
                  <div key={i} className="text-xs text-stone-500 border-t border-stone-200 pt-1">
                    {Object.entries(d)
                      .filter(([, v]) => typeof v !== 'object')
                      .map(([k, v]) => `${k}: ${formatVal(v)}`)
                      .join(' · ')}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default function ResultsPage() {
  const { simulationId } = useParams();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedYear, setExpandedYear] = useState(null);

  useEffect(() => {
    if (!simulationId) { setLoading(false); return; }
    getSimulationResults(simulationId)
      .then((res) => setResults(res.data))
      .catch((err) => toast.error(err.response?.data?.detail || 'Erreur'))
      .finally(() => setLoading(false));
  }, [simulationId]);

  if (!simulationId) {
    return (
      <div>
        <PageHeader title="Résultats" subtitle="Sélectionnez une simulation depuis la page Simulations." />
        <div className="card p-12 text-center">
          <Scale className="w-12 h-12 text-stone-300 mx-auto mb-4" />
          <p className="text-stone-500">Aucune simulation sélectionnée</p>
          <Link to="/simulations" className="text-palm-600 hover:text-palm-700 text-sm font-medium mt-2 inline-block">
            Voir les simulations →
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="w-8 h-8 border-4 border-palm-200 border-t-palm-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!results) return <p className="text-stone-500">Résultats non disponibles</p>;

  const { simulation, yearly_results, cycle_result } = results;

  const yearlyChartData = yearly_results.map((yr) => ({
    year: yr.year,
    age: yr.palm_age,
    ...Object.fromEntries(Object.keys(INPUT_LABELS).map((k) => [`in_${k}`, yr[k]])),
    ...Object.fromEntries(Object.keys(OUTPUT_LABELS).map((k) => [`out_${k}`, -yr[k]])),
    balance: yr.balance,
  }));

  const cycleInputs = cycle_result?.summary?.inputs || {};
  const cycleOutputs = cycle_result?.summary?.outputs || {};

  const pieInputs = Object.entries(cycleInputs)
    .filter(([, v]) => v > 0)
    .map(([k, v]) => ({ name: INPUT_LABELS[k] || k, value: Math.round(v * 10) / 10, color: INPUT_COLORS[k] }));

  const pieOutputs = Object.entries(cycleOutputs)
    .filter(([, v]) => v > 0)
    .map(([k, v]) => ({ name: OUTPUT_LABELS[k] || k, value: Math.round(v * 10) / 10, color: OUTPUT_COLORS[k] }));

  return (
    <div>
      <Toaster position="top-right" />

      <Link
        to="/simulations"
        className="inline-flex items-center gap-1.5 text-sm text-stone-500 hover:text-stone-700 mb-4 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Retour aux simulations
      </Link>

      <PageHeader
        title={simulation.name}
        subtitle={`Dataset météo : ${simulation.rainfall_dataset} · ${yearly_results.length} années`}
      />

      {/* Résumé cycle complet */}
      {cycle_result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
          <div className="card p-6">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="w-5 h-5 text-palm-500" />
              <p className="text-sm text-stone-500 font-medium">Total entrées N</p>
            </div>
            <p className="text-2xl font-display text-palm-700">
              {Math.round(cycle_result.total_n_inputs)} <span className="text-sm font-body text-stone-400">kg N/ha</span>
            </p>
          </div>
          <div className="card p-6">
            <div className="flex items-center gap-2 mb-1">
              <TrendingDown className="w-5 h-5 text-soil-500" />
              <p className="text-sm text-stone-500 font-medium">Total sorties N</p>
            </div>
            <p className="text-2xl font-display text-soil-700">
              {Math.round(cycle_result.total_n_outputs)} <span className="text-sm font-body text-stone-400">kg N/ha</span>
            </p>
          </div>
          <div className="card p-6">
            <div className="flex items-center gap-2 mb-1">
              <Scale className="w-5 h-5 text-sky-500" />
              <p className="text-sm text-stone-500 font-medium">Bilan</p>
            </div>
            <p className={`text-2xl font-display ${cycle_result.total_balance >= 0 ? 'text-palm-700' : 'text-red-600'}`}>
              {cycle_result.total_balance >= 0 ? '+' : ''}
              {Math.round(cycle_result.total_balance)}{' '}
              <span className="text-sm font-body text-stone-400">kg N/ha</span>
            </p>
          </div>
        </div>
      )}

      {/* Graphique bilan annuel */}
      <div className="card p-6 mb-6">
        <h2 className="font-display text-lg text-stone-800 mb-4">Bilan azoté annuel (kg N/ha/an)</h2>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={yearlyChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
            <XAxis dataKey="year" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value, name) => [
                `${Math.abs(Math.round(value * 10) / 10)} kg N/ha`,
                name.replace('in_n_', '').replace('out_n_', ''),
              ]}
            />
            <Legend />
            {Object.entries(INPUT_LABELS).map(([key, label]) => (
              <Bar key={`in_${key}`} dataKey={`in_${key}`} stackId="inputs" fill={INPUT_COLORS[key]} name={label} />
            ))}
            {Object.entries(OUTPUT_LABELS).map(([key, label]) => (
              <Bar key={`out_${key}`} dataKey={`out_${key}`} stackId="outputs" fill={OUTPUT_COLORS[key]} name={label} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Pie charts cycle */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="card p-6">
          <h2 className="font-display text-lg text-stone-800 mb-4">Répartition entrées N (cycle)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieInputs} cx="50%" cy="50%" outerRadius={100} innerRadius={50} dataKey="value"
                label={({ name, value }) => `${name}: ${value}`} labelLine={true}>
                {pieInputs.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="card p-6">
          <h2 className="font-display text-lg text-stone-800 mb-4">Répartition sorties N (cycle)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieOutputs} cx="50%" cy="50%" outerRadius={100} innerRadius={50} dataKey="value"
                label={({ name, value }) => `${name}: ${value}`} labelLine={true}>
                {pieOutputs.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tableau détaillé avec lignes expandables */}
      <div className="card p-6">
        <h2 className="font-display text-lg text-stone-800 mb-1">Détail annuel</h2>
        <p className="text-xs text-stone-400 mb-4">Cliquez sur une ligne pour voir le détail des calculs intermédiaires.</p>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b-2 border-stone-200">
                <th className="w-6 py-2 px-2" />
                <th className="text-left py-2 px-2 font-medium text-stone-600">Année</th>
                <th className="text-left py-2 px-2 font-medium text-stone-600">Âge</th>
                <th className="text-right py-2 px-2 font-medium text-palm-600">Entrées</th>
                <th className="text-right py-2 px-2 font-medium text-soil-600">Sorties</th>
                <th className="text-right py-2 px-2 font-medium text-sky-600">Bilan</th>
              </tr>
            </thead>
            <tbody>
              {yearly_results.map((yr) => {
                const isExpanded = expandedYear === yr.year;
                return (
                  <>
                    <tr
                      key={yr.year}
                      onClick={() => setExpandedYear(isExpanded ? null : yr.year)}
                      className="border-b border-stone-100 hover:bg-stone-50 cursor-pointer select-none"
                    >
                      <td className="py-2 px-2 text-stone-400">
                        {isExpanded
                          ? <ChevronDown className="w-3.5 h-3.5" />
                          : <ChevronRight className="w-3.5 h-3.5" />}
                      </td>
                      <td className="py-2 px-2 font-mono">{yr.year}</td>
                      <td className="py-2 px-2 text-stone-500">{yr.palm_age}</td>
                      <td className="py-2 px-2 text-right text-palm-700 font-medium">
                        {Math.round(yr.total_inputs * 10) / 10}
                      </td>
                      <td className="py-2 px-2 text-right text-soil-700 font-medium">
                        {Math.round(yr.total_outputs * 10) / 10}
                      </td>
                      <td className={`py-2 px-2 text-right font-bold ${yr.balance >= 0 ? 'text-palm-600' : 'text-red-600'}`}>
                        {yr.balance >= 0 ? '+' : ''}{Math.round(yr.balance * 10) / 10}
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr key={`${yr.year}-detail`} className="bg-stone-50 border-b border-stone-200">
                        <td colSpan={6} className="px-4 py-4">
                          <YearDetail intermediates={yr.intermediate_results} yr={yr} />
                        </td>
                      </tr>
                    )}
                  </>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
