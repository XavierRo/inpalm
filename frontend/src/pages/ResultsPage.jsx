import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, TrendingUp, TrendingDown, Scale } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  AreaChart, Area, PieChart, Pie, Cell,
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

export default function ResultsPage() {
  const { simulationId } = useParams();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!simulationId) {
      setLoading(false);
      return;
    }
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

  // Données pour le graphique barres empilées
  const yearlyChartData = yearly_results.map((yr) => ({
    year: yr.year,
    age: yr.palm_age,
    ...Object.fromEntries(
      Object.keys(INPUT_LABELS).map((k) => [`in_${k}`, yr[k]])
    ),
    ...Object.fromEntries(
      Object.keys(OUTPUT_LABELS).map((k) => [`out_${k}`, -yr[k]])
    ),
    balance: yr.balance,
  }));

  // Données pour les pie charts du cycle complet
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
            <p
              className={`text-2xl font-display ${
                cycle_result.total_balance >= 0 ? 'text-palm-700' : 'text-red-600'
              }`}
            >
              {cycle_result.total_balance >= 0 ? '+' : ''}
              {Math.round(cycle_result.total_balance)}{' '}
              <span className="text-sm font-body text-stone-400">kg N/ha</span>
            </p>
          </div>
        </div>
      )}

      {/* Graphique évolution du bilan annuel */}
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
                name.replace('in_', '').replace('out_', ''),
              ]}
            />
            <Legend />
            {/* Entrées (positives) */}
            {Object.entries(INPUT_LABELS).map(([key, label]) => (
              <Bar
                key={`in_${key}`}
                dataKey={`in_${key}`}
                stackId="inputs"
                fill={INPUT_COLORS[key]}
                name={label}
              />
            ))}
            {/* Sorties (négatives) */}
            {Object.entries(OUTPUT_LABELS).map(([key, label]) => (
              <Bar
                key={`out_${key}`}
                dataKey={`out_${key}`}
                stackId="outputs"
                fill={OUTPUT_COLORS[key]}
                name={label}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Pie charts cycle complet */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="card p-6">
          <h2 className="font-display text-lg text-stone-800 mb-4">Répartition entrées N (cycle)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieInputs}
                cx="50%"
                cy="50%"
                outerRadius={100}
                innerRadius={50}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
                labelLine={true}
              >
                {pieInputs.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-6">
          <h2 className="font-display text-lg text-stone-800 mb-4">Répartition sorties N (cycle)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieOutputs}
                cx="50%"
                cy="50%"
                outerRadius={100}
                innerRadius={50}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
                labelLine={true}
              >
                {pieOutputs.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tableau détaillé */}
      <div className="card p-6">
        <h2 className="font-display text-lg text-stone-800 mb-4">Détail annuel</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b-2 border-stone-200">
                <th className="text-left py-2 px-2 font-medium text-stone-600">Année</th>
                <th className="text-left py-2 px-2 font-medium text-stone-600">Âge</th>
                <th className="text-right py-2 px-2 font-medium text-palm-600">Entrées</th>
                <th className="text-right py-2 px-2 font-medium text-soil-600">Sorties</th>
                <th className="text-right py-2 px-2 font-medium text-sky-600">Bilan</th>
              </tr>
            </thead>
            <tbody>
              {yearly_results.map((yr) => (
                <tr key={yr.year} className="border-b border-stone-100 hover:bg-stone-50">
                  <td className="py-2 px-2 font-mono">{yr.year}</td>
                  <td className="py-2 px-2 text-stone-500">{yr.palm_age}</td>
                  <td className="py-2 px-2 text-right text-palm-700 font-medium">
                    {Math.round(yr.total_inputs * 10) / 10}
                  </td>
                  <td className="py-2 px-2 text-right text-soil-700 font-medium">
                    {Math.round(yr.total_outputs * 10) / 10}
                  </td>
                  <td
                    className={`py-2 px-2 text-right font-bold ${
                      yr.balance >= 0 ? 'text-palm-600' : 'text-red-600'
                    }`}
                  >
                    {yr.balance >= 0 ? '+' : ''}
                    {Math.round(yr.balance * 10) / 10}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
