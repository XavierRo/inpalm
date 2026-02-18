import { useState, useEffect } from 'react';
import { Settings, Plus, Pencil, Trash2, ChevronDown, ChevronRight } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import {
  getFertilizers, createFertilizer, updateFertilizer, deleteFertilizer,
  getEmissionFactors, getPalmUptakeParams, getVolatilizationParams,
  getLeachingParams, getFuzzyRules, getMethods,
} from '../services/api';
import toast, { Toaster } from 'react-hot-toast';

function ParamSection({ title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="card overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-stone-50 transition-colors"
      >
        <h3 className="font-display text-lg text-stone-800">{title}</h3>
        {open ? (
          <ChevronDown className="w-5 h-5 text-stone-400" />
        ) : (
          <ChevronRight className="w-5 h-5 text-stone-400" />
        )}
      </button>
      {open && <div className="px-6 pb-6 border-t border-stone-100 pt-4">{children}</div>}
    </div>
  );
}

function DataTable({ columns, data, emptyMessage }) {
  if (!data || data.length === 0) {
    return (
      <p className="text-sm text-stone-400 py-4 text-center italic">{emptyMessage || 'Aucune donnée'}</p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-stone-200">
            {columns.map((col) => (
              <th
                key={col.key}
                className="text-left py-2 px-3 text-xs uppercase tracking-wider text-stone-500 font-medium"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={row.id || idx} className="border-b border-stone-100 hover:bg-stone-50 transition-colors">
              {columns.map((col) => (
                <td key={col.key} className="py-2.5 px-3 text-stone-700">
                  {col.render ? col.render(row[col.key], row) : String(row[col.key] ?? '—')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function ParametersPage() {
  const [fertilizers, setFertilizers] = useState([]);
  const [emissions, setEmissions] = useState([]);
  const [palmUptake, setPalmUptake] = useState([]);
  const [volatilization, setVolatilization] = useState([]);
  const [leaching, setLeaching] = useState([]);
  const [fuzzyRules, setFuzzyRules] = useState([]);
  const [methods, setMethods] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getFertilizers(),
      getEmissionFactors(),
      getPalmUptakeParams(),
      getVolatilizationParams(),
      getLeachingParams(),
      getFuzzyRules(),
      getMethods(),
    ])
      .then(([fert, em, palm, vol, leach, fuzzy, meth]) => {
        setFertilizers(fert.data);
        setEmissions(em.data);
        setPalmUptake(palm.data);
        setVolatilization(vol.data);
        setLeaching(leach.data);
        setFuzzyRules(fuzzy.data);
        setMethods(meth.data);
      })
      .catch(() => toast.error('Erreur lors du chargement des paramètres'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="w-8 h-8 border-4 border-palm-200 border-t-palm-600 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div>
      <Toaster position="top-right" />

      <PageHeader
        title="Paramètres"
        subtitle="Configurez les coefficients, facteurs d'émission, et méthodes de calcul utilisés dans les simulations."
      />

      <div className="space-y-4">
        <ParamSection title="Propriétés des fertilisants" defaultOpen={true}>
          <DataTable
            columns={[
              { key: 'name', label: 'Nom' },
              { key: 'type', label: 'Type' },
              { key: 'n_content', label: '% N', render: (v) => `${v}%` },
              { key: 'nh4_fraction', label: 'NH₄⁺' },
              { key: 'no3_fraction', label: 'NO₃⁻' },
              { key: 'unit_conversion', label: 'Conv. unité' },
            ]}
            data={fertilizers}
            emptyMessage="Aucun fertilisant configuré. Ajoutez les propriétés N de vos fertilisants."
          />
        </ParamSection>

        <ParamSection title="Facteurs d'émission (N₂O, NOx, N₂)">
          <DataTable
            columns={[
              { key: 'flux_type', label: 'Flux' },
              { key: 'source', label: 'Source' },
              { key: 'method', label: 'Méthode' },
              { key: 'factor_value', label: 'Facteur' },
              { key: 'description', label: 'Description' },
            ]}
            data={emissions}
            emptyMessage="Aucun facteur d'émission configuré."
          />
        </ParamSection>

        <ParamSection title="Volatilisation NH₃">
          <DataTable
            columns={[
              { key: 'fertilizer_name', label: 'Fertilisant' },
              { key: 'placement', label: 'Placement' },
              { key: 'base_rate', label: 'Taux de base' },
              { key: 'ph_adjustment', label: 'Ajust. pH' },
            ]}
            data={volatilization}
            emptyMessage="Aucun paramètre de volatilisation configuré."
          />
        </ParamSection>

        <ParamSection title="Lessivage NO₃⁻">
          <DataTable
            columns={[
              { key: 'texture', label: 'Texture' },
              { key: 'slope_min', label: 'Pente min' },
              { key: 'slope_max', label: 'Pente max' },
              { key: 'terraces', label: 'Terrasses' },
              { key: 'base_leaching_fraction', label: 'Fraction' },
              { key: 'rainfall_coefficient', label: 'Coeff. pluie' },
            ]}
            data={leaching}
            emptyMessage="Aucun paramètre de lessivage configuré."
          />
        </ParamSection>

        <ParamSection title="Captation N par les palmiers">
          <DataTable
            columns={[
              { key: 'age_min', label: 'Âge min' },
              { key: 'age_max', label: 'Âge max' },
              { key: 'n_per_tffb', label: 'kg N/t FFB' },
              { key: 'vegetative_n_demand', label: 'Demande vég. (kg N/ha/an)' },
            ]}
            data={palmUptake}
            emptyMessage="Aucun paramètre de captation configuré."
          />
        </ParamSection>

        <ParamSection title="Règles de logique floue">
          <DataTable
            columns={[
              { key: 'rule_set_name', label: 'Jeu de règles' },
              { key: 'conditions', label: 'Conditions', render: (v) => JSON.stringify(v) },
              { key: 'output_value', label: 'Valeur sortie' },
              { key: 'weight', label: 'Poids' },
            ]}
            data={fuzzyRules}
            emptyMessage="Aucune règle floue configurée."
          />
        </ParamSection>

        <ParamSection title="Méthodes de calcul">
          <DataTable
            columns={[
              { key: 'flux_type', label: 'Type de flux' },
              { key: 'method_name', label: 'Méthode' },
              { key: 'is_default', label: 'Défaut', render: (v) => (v ? '✓' : '') },
              { key: 'description', label: 'Description' },
            ]}
            data={methods}
            emptyMessage="Aucune méthode de calcul configurée."
          />
        </ParamSection>
      </div>
    </div>
  );
}
