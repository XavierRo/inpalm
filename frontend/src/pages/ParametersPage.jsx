import { useState, useEffect } from 'react';
import { Settings, ChevronDown, ChevronRight } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import {
  getFertilizers,
  getEmissionFactors,
  getPalmUptakeParams,
  getVolatilizationParams,
  getLeachingParams,
  getMethods,
  getFuzzyModules,
  getFuzzyFactors,
  getFuzzyRules,
  getFuzzyNominalConversions,
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
        {open ? <ChevronDown className="w-5 h-5 text-stone-400" /> : <ChevronRight className="w-5 h-5 text-stone-400" />}
      </button>
      {open && <div className="px-6 pb-6 border-t border-stone-100 pt-4">{children}</div>}
    </div>
  );
}

function DataTable({ columns, data, emptyMessage }) {
  if (!data || data.length === 0) {
    return <p className="text-sm text-stone-400 py-4 text-center italic">{emptyMessage || 'Aucune donnée'}</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-stone-200">
            {columns.map((col) => (
              <th key={col.key} className="text-left py-2 px-3 text-xs uppercase tracking-wider text-stone-500 font-medium">
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

// Affiche les facteurs, règles et conversions nominales d'un module fuzzy
function FuzzyModuleDetail({ moduleCode, factors, rules, nominals }) {
  const moduleFacts = factors.filter((f) => f.module_code === moduleCode);
  const moduleRules = rules.filter((r) => r.module_code === moduleCode);
  const moduleNominals = nominals.filter((n) => n.module_code === moduleCode);

  return (
    <div className="space-y-5">
      {/* Facteurs */}
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-stone-500 mb-2">
          Facteurs ({moduleFacts.length})
        </h4>
        <DataTable
          columns={[
            { key: 'factor_name', label: 'Facteur' },
            { key: 'label', label: 'Libellé' },
            { key: 'unit', label: 'Unité' },
            { key: 'unfav_limit', label: 'Limite Défavorable' },
            { key: 'fav_limit', label: 'Limite Favorable' },
            { key: 'is_intermediate', label: 'Intermédiaire', render: (v) => (v ? '✓' : '') },
          ]}
          data={moduleFacts}
          emptyMessage="Aucun facteur"
        />
      </div>

      {/* Règles */}
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-stone-500 mb-2">
          Règles ({moduleRules.length})
        </h4>
        <DataTable
          columns={[
            { key: 'rule_number', label: 'N°' },
            {
              key: 'conditions',
              label: 'Conditions (F=Favorable, U=Défavorable)',
              render: (v) => (
                <span className="font-mono text-xs">
                  {Object.entries(v).map(([k, c]) => (
                    <span key={k} className={`mr-2 ${c === 'F' ? 'text-palm-600' : 'text-soil-600'}`}>
                      {k}={c}
                    </span>
                  ))}
                </span>
              ),
            },
            { key: 'conclusion', label: 'Valeur de sortie' },
            { key: 'conclusion_label', label: 'Étiquette' },
          ]}
          data={moduleRules}
          emptyMessage="Aucune règle"
        />
      </div>

      {/* Conversions nominales */}
      {moduleNominals.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-stone-500 mb-2">
            Conversions nominales ({moduleNominals.length})
          </h4>
          <DataTable
            columns={[
              { key: 'factor_name', label: 'Facteur' },
              { key: 'nominal_value', label: 'Valeur nominale' },
              { key: 'numeric_value', label: 'Valeur numérique' },
            ]}
            data={moduleNominals}
            emptyMessage="Aucune conversion nominale"
          />
        </div>
      )}
    </div>
  );
}

const STEP_LABELS = {
  1: 'Étape 1 — Volatilisation NH₃',
  2: 'Étape 2 — Sol et eau',
  3: 'Étape 3 — Dénitrification',
  4: 'Étape 4 — Azote sol',
  5: 'Étape 5 — Dénitrification basale & lessivage',
};

function FuzzySection({ modules, factors, rules, nominals }) {
  const [selectedCode, setSelectedCode] = useState(modules[0]?.module_code || null);

  if (!modules.length) {
    return <p className="text-sm text-stone-400 py-4 text-center italic">Aucun module fuzzy chargé.</p>;
  }

  const selectedModule = modules.find((m) => m.module_code === selectedCode);

  // Grouper les modules par étape
  const byStep = modules.reduce((acc, m) => {
    if (!acc[m.step]) acc[m.step] = [];
    acc[m.step].push(m);
    return acc;
  }, {});

  return (
    <div>
      {/* Sélecteur de module groupé par étape */}
      <div className="mb-5 space-y-2">
        {Object.entries(byStep).map(([step, mods]) => (
          <div key={step}>
            <p className="text-xs font-semibold uppercase tracking-wider text-stone-400 mb-1">{STEP_LABELS[step]}</p>
            <div className="flex flex-wrap gap-2">
              {mods.map((m) => (
                <button
                  key={m.module_code}
                  onClick={() => setSelectedCode(m.module_code)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                    selectedCode === m.module_code
                      ? 'bg-palm-600 text-white'
                      : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
                  }`}
                >
                  {m.module_code}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Détail du module sélectionné */}
      {selectedModule && (
        <div className="border border-stone-200 rounded-lg p-4">
          <div className="mb-4 flex items-start justify-between">
            <div>
              <p className="font-medium text-stone-800">{selectedModule.module_name}</p>
              <p className="text-xs text-stone-500 mt-0.5">
                {selectedModule.report_section} · Sortie : {selectedModule.output_unit}
                {selectedModule.output_min != null && ` [${selectedModule.output_min} – ${selectedModule.output_max}]`}
              </p>
              {selectedModule.reference && (
                <p className="text-xs text-stone-400 mt-1 italic">{selectedModule.reference}</p>
              )}
            </div>
          </div>
          <FuzzyModuleDetail
            moduleCode={selectedCode}
            factors={factors}
            rules={rules}
            nominals={nominals}
          />
        </div>
      )}
    </div>
  );
}

export default function ParametersPage() {
  const [fertilizers, setFertilizers] = useState([]);
  const [emissions, setEmissions] = useState([]);
  const [palmUptake, setPalmUptake] = useState([]);
  const [volatilization, setVolatilization] = useState([]);
  const [leaching, setLeaching] = useState([]);
  const [methods, setMethods] = useState([]);
  const [fuzzyModules, setFuzzyModules] = useState([]);
  const [fuzzyFactors, setFuzzyFactors] = useState([]);
  const [fuzzyRules, setFuzzyRules] = useState([]);
  const [fuzzyNominals, setFuzzyNominals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getFertilizers(),
      getEmissionFactors(),
      getPalmUptakeParams(),
      getVolatilizationParams(),
      getLeachingParams(),
      getMethods(),
      getFuzzyModules(),
      getFuzzyFactors(),
      getFuzzyRules(),
      getFuzzyNominalConversions(),
    ])
      .then(([fert, em, palm, vol, leach, meth, fmod, ffact, frules, fnom]) => {
        setFertilizers(fert.data);
        setEmissions(em.data);
        setPalmUptake(palm.data);
        setVolatilization(vol.data);
        setLeaching(leach.data);
        setMethods(meth.data);
        setFuzzyModules(fmod.data);
        setFuzzyFactors(ffact.data);
        setFuzzyRules(frules.data);
        setFuzzyNominals(fnom.data);
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
        subtitle="Coefficients, facteurs d'émission et arbres de décision floue utilisés dans les simulations."
      />

      <div className="space-y-4">

        <ParamSection title="Logique floue IN-Palm" defaultOpen={true}>
          <FuzzySection
            modules={fuzzyModules}
            factors={fuzzyFactors}
            rules={fuzzyRules}
            nominals={fuzzyNominals}
          />
        </ParamSection>

        <ParamSection title="Captation N par les palmiers (table par âge)">
          <DataTable
            columns={[
              { key: 'palm_age', label: 'Âge (ans)' },
              { key: 'yield_unfav_limit', label: 'Rendement limite défav. (t FFB/ha)' },
              { key: 'yield_fav_limit', label: 'Rendement limite fav. (t FFB/ha)' },
              { key: 'n_uptake_low', label: 'Captation N basse (kg N/ha/an)' },
              { key: 'n_uptake_high', label: 'Captation N haute (kg N/ha/an)' },
            ]}
            data={palmUptake}
            emptyMessage="Aucun paramètre de captation configuré."
          />
        </ParamSection>

        <ParamSection title="Propriétés des fertilisants">
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
            emptyMessage="Aucun fertilisant configuré."
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
