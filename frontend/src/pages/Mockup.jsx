import { useState } from 'react';
import {
  Leaf, Upload, Map, Settings, FlaskConical, BarChart3, Home,
  TrendingUp, TrendingDown, Scale, MapPin, Calendar, Layers,
  ChevronDown, ChevronUp, CheckCircle2, Loader2, AlertCircle, Clock,
  ArrowLeft, Plus, Trash2, FileText, CloudRain, Sprout, FlaskRound,
  Info,
} from 'lucide-react';
import {
  BarChart, Bar, AreaChart, Area, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';

// ─── Mock data ────────────────────────────────────────────────────────────────

const MOCK_FIELDS = [
  {
    id: 1,
    name: 'Parcelle Nord',
    location: 'Kedah, Malaisie',
    soil_texture: 'sandy_loam',
    soil_organic_carbon: 2.1,
    soil_ph: 5.8,
    cec: 12.4,
    slope_pct: 4,
    terraces: false,
    start_year: 2010,
    end_year: 2023,
    planting_year: 2009,
    initial_soil_n: 320,
    previous_crop: 'jungle',
  },
  {
    id: 2,
    name: 'Bloc Est B2',
    location: 'Riau, Indonésie',
    soil_texture: 'clay',
    soil_organic_carbon: 3.4,
    soil_ph: 4.9,
    cec: 22.1,
    slope_pct: 1,
    terraces: false,
    start_year: 2015,
    end_year: 2023,
    planting_year: 2014,
    initial_soil_n: 410,
    previous_crop: 'rubber',
  },
  {
    id: 3,
    name: 'Plot Trial T3',
    location: 'Pahang, Malaisie',
    soil_texture: 'loam',
    soil_organic_carbon: 2.8,
    soil_ph: 5.5,
    cec: 18.7,
    slope_pct: 8,
    terraces: true,
    start_year: 2018,
    end_year: 2023,
    planting_year: 2017,
    initial_soil_n: 280,
    previous_crop: 'oil_palm',
  },
];

const MOCK_YEARLY_RESULTS = [
  { year: 2010, age: 1,  inputs: 180, outputs: 95,  balance: 85,  nh3: 8,  n2o: 4,  n2: 3,  nox: 2,  leaching: 18, runoff: 5,  uptake: 55 },
  { year: 2011, age: 2,  inputs: 220, outputs: 130, balance: 90,  nh3: 12, n2o: 6,  n2: 5,  nox: 3,  leaching: 22, runoff: 6,  uptake: 76 },
  { year: 2012, age: 3,  inputs: 280, outputs: 175, balance: 105, nh3: 18, n2o: 9,  n2: 7,  nox: 4,  leaching: 30, runoff: 8,  uptake: 99 },
  { year: 2013, age: 4,  inputs: 310, outputs: 210, balance: 100, nh3: 22, n2o: 11, n2: 9,  nox: 5,  leaching: 35, runoff: 9,  uptake: 119},
  { year: 2014, age: 5,  inputs: 340, outputs: 240, balance: 100, nh3: 25, n2o: 13, n2: 10, nox: 5,  leaching: 40, runoff: 10, uptake: 137},
  { year: 2015, age: 6,  inputs: 360, outputs: 265, balance: 95,  nh3: 28, n2o: 14, n2: 11, nox: 6,  leaching: 44, runoff: 11, uptake: 151},
  { year: 2016, age: 7,  inputs: 370, outputs: 278, balance: 92,  nh3: 29, n2o: 15, n2: 12, nox: 6,  leaching: 46, runoff: 12, uptake: 158},
  { year: 2017, age: 8,  inputs: 365, outputs: 272, balance: 93,  nh3: 28, n2o: 14, n2: 11, nox: 6,  leaching: 45, runoff: 12, uptake: 156},
  { year: 2018, age: 9,  inputs: 358, outputs: 268, balance: 90,  nh3: 27, n2o: 14, n2: 11, nox: 6,  leaching: 44, runoff: 11, uptake: 155},
  { year: 2019, age: 10, inputs: 350, outputs: 260, balance: 90,  nh3: 26, n2o: 13, n2: 10, nox: 5,  leaching: 43, runoff: 11, uptake: 152},
  { year: 2020, age: 11, inputs: 345, outputs: 255, balance: 90,  nh3: 25, n2o: 13, n2: 10, nox: 5,  leaching: 42, runoff: 10, uptake: 150},
  { year: 2021, age: 12, inputs: 338, outputs: 248, balance: 90,  nh3: 24, n2o: 12, n2: 10, nox: 5,  leaching: 41, runoff: 10, uptake: 146},
  { year: 2022, age: 13, inputs: 330, outputs: 242, balance: 88,  nh3: 23, n2o: 12, n2: 9,  nox: 5,  leaching: 40, runoff: 10, uptake: 143},
  { year: 2023, age: 14, inputs: 322, outputs: 235, balance: 87,  nh3: 22, n2o: 11, n2: 9,  nox: 4,  leaching: 38, runoff: 10, uptake: 141},
];

const MOCK_RAINFALL = [
  { month: 'Jan', mm: 185 }, { month: 'Fév', mm: 142 }, { month: 'Mar', mm: 210 },
  { month: 'Avr', mm: 260 }, { month: 'Mai', mm: 198 }, { month: 'Jun', mm: 130 },
  { month: 'Jul', mm: 115 }, { month: 'Aoû', mm: 128 }, { month: 'Sep', mm: 175 },
  { month: 'Oct', mm: 240 }, { month: 'Nov', mm: 280 }, { month: 'Déc', mm: 220 },
];

const MOCK_YIELD = [
  { year: 2010, yield: 5.2 }, { year: 2011, yield: 10.8 }, { year: 2012, year_label: 2012, yield: 18.4 },
  { year: 2013, yield: 24.1 }, { year: 2014, yield: 27.8 }, { year: 2015, yield: 28.9 },
  { year: 2016, yield: 29.4 }, { year: 2017, yield: 28.6 }, { year: 2018, yield: 27.9 },
  { year: 2019, yield: 27.2 }, { year: 2020, yield: 26.5 }, { year: 2021, yield: 25.8 },
  { year: 2022, yield: 25.1 }, { year: 2023, yield: 24.6 },
];

const MOCK_FERTILIZATION = [
  { year: 2010, mineral: 45, organic: 0  }, { year: 2011, mineral: 80, organic: 0  },
  { year: 2012, mineral: 110, organic: 20 }, { year: 2013, mineral: 120, organic: 30 },
  { year: 2014, mineral: 125, organic: 40 }, { year: 2015, mineral: 130, organic: 45 },
  { year: 2016, mineral: 130, organic: 50 }, { year: 2017, mineral: 125, organic: 50 },
  { year: 2018, mineral: 120, organic: 50 }, { year: 2019, mineral: 118, organic: 48 },
  { year: 2020, mineral: 115, organic: 45 }, { year: 2021, mineral: 112, organic: 45 },
  { year: 2022, mineral: 110, organic: 42 }, { year: 2023, mineral: 108, organic: 40 },
];

const MOCK_SIMULATIONS = [
  { id: 1, name: 'Sim Parcelle Nord 2010–2023', field: 'Parcelle Nord', status: 'completed', created_at: '2024-01-15', description: 'Simulation de référence' },
  { id: 2, name: 'Scénario sans engrais organiques', field: 'Bloc Est B2', status: 'completed', created_at: '2024-02-03', description: 'Test sensibilité fertilisation' },
  { id: 3, name: 'Plot T3 — Analyse terrasses', field: 'Plot Trial T3', status: 'running', created_at: '2024-04-21', description: '' },
];

const FUZZY_MODULES = [
  { step: 1, code: 'nh3_mineral',        label: 'NH₃ Minéral',         rules: 7,  factors: 3 },
  { step: 2, code: 'soil_cover',         label: 'Couverture sol',       rules: 18, factors: 4 },
  { step: 2, code: 'water_runoff',       label: 'Ruissellement eau',    rules: 5,  factors: 2 },
  { step: 3, code: 'n2o_mineral',        label: 'N₂O Minéral',          rules: 32, factors: 5 },
  { step: 3, code: 'n2_mineral',         label: 'N₂ Minéral',           rules: 2,  factors: 2 },
  { step: 3, code: 'runoff_erosion',     label: 'Érosion ruissellement',rules: 9,  factors: 3 },
  { step: 4, code: 'understorey_fix',    label: 'Fixation sous-étage',  rules: 2,  factors: 2 },
  { step: 5, code: 'n2o_baseline',       label: 'N₂O Basale',           rules: 16, factors: 4 },
  { step: 5, code: 'n2_baseline',        label: 'N₂ Basale',            rules: 2,  factors: 2 },
  { step: 5, code: 'leaching',           label: 'Lessivage',            rules: 2,  factors: 2 },
];

const MOCK_FACTORS = {
  nh3_mineral: [
    { name: 'fertilizer_nh4_fraction', label: 'Fraction NH₄⁺', unfav_limit: 0.1, fav_limit: 0.9 },
    { name: 'soil_ph', label: 'pH sol', unfav_limit: 5.0, fav_limit: 7.5 },
    { name: 'soil_moisture', label: 'Humidité sol', unfav_limit: 0.2, fav_limit: 0.8 },
  ],
  n2o_mineral: [
    { name: 'soil_moisture', label: 'Humidité sol', unfav_limit: 0.3, fav_limit: 0.7 },
    { name: 'mineral_n_applied', label: 'N minéral apporté', unfav_limit: 0, fav_limit: 200 },
    { name: 'soil_texture_index', label: 'Texture sol', unfav_limit: 0.2, fav_limit: 0.8 },
    { name: 'soil_organic_carbon', label: 'Carbone organique', unfav_limit: 1.0, fav_limit: 4.0 },
    { name: 'drainage', label: 'Drainage', unfav_limit: 0.1, fav_limit: 0.9 },
  ],
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

const PALETTE = {
  inputs:  ['#4ade80','#86efac','#16a34a','#15803d','#bbf7d0'],
  outputs: ['#fb923c','#fbbf24','#60a5fa','#c084fc','#f87171','#a78bfa','#f472b6'],
};

const TEXTURE_LABEL = { sandy_loam: 'Sablo-limoneux', clay: 'Argileux', loam: 'Limoneux', sandy: 'Sableux' };
const CROP_LABEL    = { jungle: 'Forêt', rubber: 'Hévéa', oil_palm: 'Palmier à huile', fallow: 'Jachère' };

const statusConfig = {
  completed: { icon: CheckCircle2, color: 'text-green-600', bg: 'bg-green-50', badge: 'badge-success', label: 'Terminée' },
  running:   { icon: Loader2,      color: 'text-blue-600',  bg: 'bg-blue-50',  badge: 'badge-info',    label: 'En cours' },
  pending:   { icon: Clock,        color: 'text-amber-600', bg: 'bg-amber-50', badge: 'badge-warning', label: 'En attente' },
  error:     { icon: AlertCircle,  color: 'text-red-600',   bg: 'bg-red-50',   badge: 'badge-error',   label: 'Erreur' },
};

// ─── Sidebar ──────────────────────────────────────────────────────────────────

const NAV = [
  { id: 'dashboard',   icon: Home,         label: 'Dashboard' },
  { id: 'import',      icon: Upload,       label: 'Import données' },
  { id: 'fields',      icon: Map,          label: 'Parcelles' },
  { id: 'parameters',  icon: Settings,     label: 'Paramètres' },
  { id: 'simulations', icon: FlaskConical, label: 'Simulations' },
  { id: 'results',     icon: BarChart3,    label: 'Résultats' },
];

function Sidebar({ current, onChange }) {
  return (
    <aside className="w-64 bg-palm-800 text-white flex flex-col flex-shrink-0">
      <div className="px-6 py-6 border-b border-palm-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-palm-400 rounded-xl flex items-center justify-center">
            <Leaf className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-display text-xl tracking-tight">NBalance</h1>
            <p className="text-palm-300 text-xs mt-0.5">Bilan Azoté</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => onChange(id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
              current === id
                ? 'bg-palm-600 text-white shadow-md'
                : 'text-palm-200 hover:bg-palm-700 hover:text-white'
            }`}
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            {label}
          </button>
        ))}
      </nav>
      <div className="px-6 py-4 border-t border-palm-700">
        <p className="text-palm-400 text-xs">NBalance v0.1.0<br />Agroécologie — Palmier à huile</p>
      </div>
    </aside>
  );
}

// ─── PageHeader ───────────────────────────────────────────────────────────────

function PageHeader({ title, subtitle, children }) {
  return (
    <div className="flex items-start justify-between mb-8">
      <div>
        <h2 className="text-2xl font-display font-semibold text-stone-900">{title}</h2>
        {subtitle && <p className="text-stone-500 text-sm mt-1">{subtitle}</p>}
      </div>
      {children && <div className="flex items-center gap-3">{children}</div>}
    </div>
  );
}

// ─── VIEW: Dashboard ──────────────────────────────────────────────────────────

function ViewDashboard({ onNavigate }) {
  const totalInputs  = Math.round(MOCK_YEARLY_RESULTS.reduce((s, r) => s + r.inputs,  0) / MOCK_YEARLY_RESULTS.length);
  const totalOutputs = Math.round(MOCK_YEARLY_RESULTS.reduce((s, r) => s + r.outputs, 0) / MOCK_YEARLY_RESULTS.length);

  return (
    <>
      <PageHeader title="Dashboard" subtitle="Vue d'ensemble de vos parcelles et simulations" />

      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="card p-6 flex items-center gap-4">
          <div className="w-12 h-12 bg-palm-100 rounded-xl flex items-center justify-center">
            <Map className="w-6 h-6 text-palm-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-stone-900">3</p>
            <p className="text-sm text-stone-500">Parcelles</p>
          </div>
        </div>
        <div className="card p-6 flex items-center gap-4">
          <div className="w-12 h-12 bg-sky-100 rounded-xl flex items-center justify-center">
            <FlaskConical className="w-6 h-6 text-sky-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-stone-900">3</p>
            <p className="text-sm text-stone-500">Simulations</p>
          </div>
        </div>
        <div
          className="card p-6 flex items-center gap-4 cursor-pointer hover:border-palm-300 transition-colors"
          onClick={() => onNavigate('import')}
        >
          <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
            <Upload className="w-6 h-6 text-amber-600" />
          </div>
          <div>
            <p className="text-sm font-semibold text-stone-700">Importer des données</p>
            <p className="text-xs text-stone-400 mt-0.5">CSV parcelles, pluvio, fertilisation</p>
          </div>
        </div>
      </div>

      {/* N flux overview */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="card p-6">
          <h3 className="font-semibold text-stone-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-palm-600" />
            Entrées N <span className="text-stone-400 font-normal text-sm">(moy. cycle, kg N/ha/an)</span>
          </h3>
          <ul className="space-y-2 text-sm">
            {[
              ['N minéral sol initial', '24'],
              ['Fixation légumineuses', '18'],
              ['Résidus végétaux', '38'],
              ['Fertilisants apportés', '148'],
              ['Dépôts atmosphériques', '12'],
            ].map(([label, val]) => (
              <li key={label} className="flex justify-between">
                <span className="text-stone-600">{label}</span>
                <span className="font-medium text-stone-800">{val}</span>
              </li>
            ))}
            <li className="flex justify-between border-t pt-2 font-semibold">
              <span>Total</span>
              <span className="text-palm-700">{totalInputs}</span>
            </li>
          </ul>
        </div>
        <div className="card p-6">
          <h3 className="font-semibold text-stone-800 mb-4 flex items-center gap-2">
            <TrendingDown className="w-5 h-5 text-amber-600" />
            Sorties N <span className="text-stone-400 font-normal text-sm">(moy. cycle, kg N/ha/an)</span>
          </h3>
          <ul className="space-y-2 text-sm">
            {[
              ['Volatilisation NH₃', '25'],
              ['Lessivage NO₃⁻', '40'],
              ['Absorption palmiers', '130'],
              ['Émissions N₂O', '13'],
              ['Émissions NOx', '5'],
              ['Émissions N₂', '10'],
              ['Ruissellement & érosion', '10'],
            ].map(([label, val]) => (
              <li key={label} className="flex justify-between">
                <span className="text-stone-600">{label}</span>
                <span className="font-medium text-stone-800">{val}</span>
              </li>
            ))}
            <li className="flex justify-between border-t pt-2 font-semibold">
              <span>Total</span>
              <span className="text-amber-700">{totalOutputs}</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Quick chart */}
      <div className="card p-6">
        <h3 className="font-semibold text-stone-800 mb-4">Bilan annuel — Parcelle Nord (aperçu)</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={MOCK_YEARLY_RESULTS.slice(0, 8)} barSize={24}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
            <XAxis dataKey="year" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} unit=" kg" />
            <Tooltip formatter={(v) => `${v} kg N/ha`} />
            <Legend />
            <Bar dataKey="inputs"  name="Entrées"  fill="#4ade80" radius={[3,3,0,0]} />
            <Bar dataKey="outputs" name="Sorties"  fill="#fb923c" radius={[3,3,0,0]} />
            <Bar dataKey="balance" name="Bilan"    fill="#60a5fa" radius={[3,3,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}

// ─── VIEW: Import ─────────────────────────────────────────────────────────────

function DropzoneMock({ label, description, example, icon: Icon, status }) {
  const colors = {
    idle:    'border-stone-300 bg-stone-50 text-stone-400',
    success: 'border-palm-400 bg-palm-50 text-palm-600',
    error:   'border-red-300 bg-red-50 text-red-500',
  };
  return (
    <div className="card p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-9 h-9 bg-palm-100 rounded-lg flex items-center justify-center">
          <Icon className="w-5 h-5 text-palm-600" />
        </div>
        <div>
          <h3 className="font-semibold text-stone-800 text-sm">{label}</h3>
          <p className="text-xs text-stone-400">{description}</p>
        </div>
      </div>
      <div className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${colors[status]}`}>
        {status === 'success' ? (
          <>
            <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-palm-500" />
            <p className="text-sm font-medium text-palm-700">Fichier importé avec succès</p>
            <p className="text-xs text-palm-500 mt-1">{example}</p>
          </>
        ) : (
          <>
            <Upload className="w-8 h-8 mx-auto mb-2" />
            <p className="text-sm font-medium text-stone-600">Glisser-déposer un fichier CSV</p>
            <p className="text-xs text-stone-400 mt-1">ou cliquer pour sélectionner</p>
            <p className="text-xs text-stone-300 mt-3">Exemple : {example}</p>
          </>
        )}
      </div>
    </div>
  );
}

function ViewImport() {
  const imports = [
    { label: 'Caractéristiques parcelle', description: 'Texture, pH, pente, CEC…', example: 'field_characteristics.csv', icon: Map,       status: 'success' },
    { label: 'Données annuelles',         description: 'Rendement, biomasse sous-étage', example: 'year_field_data.csv', icon: Sprout,    status: 'success' },
    { label: 'Pluviométrie',              description: 'Données mensuelles (mm)',   example: 'rainfall_kedah_2010.csv',  icon: CloudRain, status: 'idle'    },
    { label: 'Fertilisation',             description: 'Apports par date et type',  example: 'fertilization_nord.csv',   icon: FlaskRound,status: 'idle'    },
  ];
  return (
    <>
      <PageHeader title="Import données" subtitle="Chargez vos fichiers CSV pour alimenter les simulations" />
      <div className="grid grid-cols-2 gap-6">
        {imports.map((imp) => <DropzoneMock key={imp.label} {...imp} />)}
      </div>
    </>
  );
}

// ─── VIEW: Fields list ────────────────────────────────────────────────────────

function ViewFields({ onSelectField }) {
  return (
    <>
      <PageHeader title="Parcelles" subtitle={`${MOCK_FIELDS.length} parcelles importées`} />
      <div className="grid grid-cols-3 gap-6">
        {MOCK_FIELDS.map((f) => (
          <div key={f.id} className="card p-5 flex flex-col gap-4 hover:border-palm-300 transition-colors">
            <div>
              <h3 className="font-semibold text-stone-900">{f.name}</h3>
              <p className="text-sm text-stone-400 flex items-center gap-1 mt-0.5">
                <MapPin className="w-3.5 h-3.5" /> {f.location}
              </p>
            </div>
            <div className="space-y-1.5 text-sm">
              <div className="flex items-center gap-2 text-stone-600">
                <Calendar className="w-4 h-4 text-stone-400" />
                {f.start_year}–{f.end_year}
                <span className="text-stone-400">({f.end_year - f.planting_year} ans)</span>
              </div>
              <div className="flex items-center gap-2 text-stone-600">
                <Layers className="w-4 h-4 text-stone-400" />
                {TEXTURE_LABEL[f.soil_texture]} · pH {f.soil_ph} · {f.soil_organic_carbon}% C
              </div>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="badge badge-info">{f.slope_pct}% pente</span>
              {f.terraces && <span className="badge badge-success">Terrasses</span>}
              <span className="badge">{CROP_LABEL[f.previous_crop]}</span>
            </div>
            <button
              className="btn-primary text-sm mt-auto"
              onClick={() => onSelectField(f.id)}
            >
              Voir le détail
            </button>
          </div>
        ))}
      </div>
    </>
  );
}

// ─── VIEW: Field detail ───────────────────────────────────────────────────────

function ViewFieldDetail({ fieldId, onBack }) {
  const field = MOCK_FIELDS.find((f) => f.id === fieldId) ?? MOCK_FIELDS[0];
  return (
    <>
      <PageHeader title={field.name} subtitle={field.location}>
        <button className="btn-secondary text-sm flex items-center gap-2" onClick={onBack}>
          <ArrowLeft className="w-4 h-4" /> Retour
        </button>
      </PageHeader>

      {/* Characteristics grid */}
      <div className="card p-6 mb-6">
        <h3 className="font-semibold text-stone-800 mb-4">Caractéristiques pédologiques</h3>
        <div className="grid grid-cols-4 gap-4 text-sm">
          {[
            ['Texture',           TEXTURE_LABEL[field.soil_texture]],
            ['Carbone organique', `${field.soil_organic_carbon} %`],
            ['pH',                field.soil_ph],
            ['CEC',               `${field.cec} cmol/kg`],
            ['Pente',             `${field.slope_pct} %`],
            ['Terrasses',         field.terraces ? 'Oui' : 'Non'],
            ['N initial sol',     `${field.initial_soil_n} kg N/ha`],
            ['Culture précédente',CROP_LABEL[field.previous_crop]],
          ].map(([k, v]) => (
            <div key={k} className="bg-stone-50 rounded-lg p-3">
              <p className="text-stone-400 text-xs">{k}</p>
              <p className="font-medium text-stone-800 mt-0.5">{v}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="card p-6">
          <h3 className="font-semibold text-stone-800 mb-4">Rendement RFB (t/ha/an)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={MOCK_YIELD}>
              <defs>
                <linearGradient id="yieldGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#4ade80" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#4ade80" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis dataKey="year" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} unit=" t" />
              <Tooltip formatter={(v) => `${v} tRFB/ha`} />
              <Area type="monotone" dataKey="yield" name="Rendement" stroke="#16a34a" fill="url(#yieldGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="card p-6">
          <h3 className="font-semibold text-stone-800 mb-4">Pluviométrie mensuelle — 2023 (mm)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={MOCK_RAINFALL} barSize={18}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} unit=" mm" />
              <Tooltip formatter={(v) => `${v} mm`} />
              <Bar dataKey="mm" name="Pluie" fill="#60a5fa" radius={[3,3,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="font-semibold text-stone-800 mb-4">Fertilisation annuelle (kg N/ha)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={MOCK_FERTILIZATION} barSize={18}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
            <XAxis dataKey="year" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} unit=" kg" />
            <Tooltip formatter={(v) => `${v} kg N/ha`} />
            <Legend />
            <Bar dataKey="mineral" name="Minéral" stackId="a" fill="#4ade80" radius={[0,0,0,0]} />
            <Bar dataKey="organic" name="Organique" stackId="a" fill="#a78bfa" radius={[3,3,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}

// ─── VIEW: Parameters ─────────────────────────────────────────────────────────

function CollapsibleSection({ title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="card mb-4 overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-stone-50 transition-colors"
        onClick={() => setOpen(!open)}
      >
        <span className="font-semibold text-stone-800">{title}</span>
        {open ? <ChevronUp className="w-5 h-5 text-stone-400" /> : <ChevronDown className="w-5 h-5 text-stone-400" />}
      </button>
      {open && <div className="px-6 pb-6 border-t border-stone-100">{children}</div>}
    </div>
  );
}

function ViewParameters() {
  const [selectedModule, setSelectedModule] = useState('nh3_mineral');
  const module = FUZZY_MODULES.find((m) => m.code === selectedModule);
  const factors = MOCK_FACTORS[selectedModule] ?? MOCK_FACTORS['nh3_mineral'];

  const byStep = FUZZY_MODULES.reduce((acc, m) => {
    (acc[m.step] = acc[m.step] ?? []).push(m);
    return acc;
  }, {});

  return (
    <>
      <PageHeader title="Paramètres" subtitle="Visualisation et modification des paramètres du modèle IN-Palm" />

      {/* Fuzzy section */}
      <CollapsibleSection title="Logique floue IN-Palm (11 modules)" defaultOpen>
        <div className="flex gap-6 mt-4">
          {/* Module selector */}
          <div className="w-52 flex-shrink-0">
            {Object.entries(byStep).map(([step, mods]) => (
              <div key={step} className="mb-4">
                <p className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-1.5">Étape {step}</p>
                <div className="space-y-1">
                  {mods.map((m) => (
                    <button
                      key={m.code}
                      onClick={() => setSelectedModule(m.code)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                        selectedModule === m.code
                          ? 'bg-palm-600 text-white font-medium'
                          : 'text-stone-600 hover:bg-stone-100'
                      }`}
                    >
                      {m.label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Module details */}
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-4">
              <h4 className="font-semibold text-stone-900">{module?.label}</h4>
              <span className="badge badge-info">{module?.rules} règles</span>
              <span className="badge">{module?.factors} facteurs</span>
            </div>

            {/* Factors table */}
            <h5 className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-2">Facteurs</h5>
            <table className="w-full text-sm mb-6">
              <thead>
                <tr className="border-b border-stone-200">
                  <th className="text-left py-2 text-stone-500 font-medium">Facteur</th>
                  <th className="text-right py-2 text-stone-500 font-medium">Limite défav.</th>
                  <th className="text-right py-2 text-stone-500 font-medium">Limite fav.</th>
                </tr>
              </thead>
              <tbody>
                {factors.map((f) => (
                  <tr key={f.name} className="border-b border-stone-100">
                    <td className="py-2 text-stone-700">{f.label}</td>
                    <td className="py-2 text-right font-mono text-stone-800">{f.unfav_limit}</td>
                    <td className="py-2 text-right font-mono text-stone-800">{f.fav_limit}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Rules preview */}
            <h5 className="text-xs font-semibold text-stone-400 uppercase tracking-wide mb-2">Aperçu règles (4 premières)</h5>
            <div className="space-y-1.5">
              {[
                { cond: 'NH₄⁺ = F · pH = F · Humidité = F', concl: '0.025' },
                { cond: 'NH₄⁺ = F · pH = F · Humidité = U', concl: '0.040' },
                { cond: 'NH₄⁺ = F · pH = U · Humidité = F', concl: '0.050' },
                { cond: 'NH₄⁺ = U · pH = F · Humidité = F', concl: '0.080' },
              ].map((r, i) => (
                <div key={i} className="flex items-center gap-3 text-xs bg-stone-50 px-3 py-2 rounded-lg">
                  <span className="text-stone-400 font-mono w-4">{i + 1}</span>
                  <span className="text-stone-600 flex-1">SI {r.cond}</span>
                  <span className="font-semibold text-palm-700">→ {r.concl}</span>
                </div>
              ))}
              {(module?.rules ?? 0) > 4 && (
                <p className="text-xs text-stone-400 text-center pt-1">… {(module?.rules ?? 0) - 4} règles supplémentaires</p>
              )}
            </div>
          </div>
        </div>
      </CollapsibleSection>

      {/* Palm N uptake */}
      <CollapsibleSection title="Captation N par les palmiers (table par âge)">
        <table className="w-full text-sm mt-4">
          <thead>
            <tr className="border-b border-stone-200">
              {['Âge (an)', 'Rendement min (t/ha)', 'Rendement max (t/ha)', 'N captation min', 'N captation max'].map((h) => (
                <th key={h} className="text-right first:text-left py-2 text-stone-500 font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[
              [1, 0, 5, 5, 15], [3, 5, 15, 20, 45], [5, 10, 22, 40, 80],
              [8, 15, 28, 60, 110], [12, 18, 30, 65, 120], [20, 12, 25, 55, 100],
            ].map(([age, yMin, yMax, nMin, nMax]) => (
              <tr key={age} className="border-b border-stone-100">
                <td className="py-2 font-medium">{age}</td>
                <td className="py-2 text-right">{yMin}</td>
                <td className="py-2 text-right">{yMax}</td>
                <td className="py-2 text-right">{nMin}</td>
                <td className="py-2 text-right">{nMax}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CollapsibleSection>

      {/* Fertilizer properties */}
      <CollapsibleSection title="Propriétés des fertilisants">
        <table className="w-full text-sm mt-4">
          <thead>
            <tr className="border-b border-stone-200">
              {['Fertilisant', 'Teneur N (%)', 'Fraction NH₄⁺', 'Fraction NO₃⁻'].map((h) => (
                <th key={h} className="text-right first:text-left py-2 text-stone-500 font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[
              ['Urée', 46, 0.0, 0.0], ['Sulfate ammonium', 21, 1.0, 0.0],
              ['Nitrate ammonium', 33, 0.5, 0.5], ['NPK (15-15-15)', 15, 0.5, 0.3],
              ['Tourteaux palmiste', 2.8, 0.0, 0.0], ['EFB compost', 1.2, 0.0, 0.0],
            ].map(([name, n, nh4, no3]) => (
              <tr key={name} className="border-b border-stone-100">
                <td className="py-2">{name}</td>
                <td className="py-2 text-right font-mono">{n}</td>
                <td className="py-2 text-right font-mono">{nh4}</td>
                <td className="py-2 text-right font-mono">{no3}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CollapsibleSection>
    </>
  );
}

// ─── VIEW: Simulations ────────────────────────────────────────────────────────

function ViewSimulations({ onViewResults }) {
  const [showForm, setShowForm] = useState(false);

  return (
    <>
      <PageHeader title="Simulations" subtitle="Créez et lancez des bilans azotés sur vos parcelles">
        <button className="btn-primary text-sm flex items-center gap-2" onClick={() => setShowForm(!showForm)}>
          <Plus className="w-4 h-4" />
          Nouvelle simulation
        </button>
      </PageHeader>

      {/* Create form */}
      {showForm && (
        <div className="card p-6 mb-6">
          <h3 className="font-semibold text-stone-800 mb-4">Nouvelle simulation</h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Nom *</label>
              <input className="input-field" placeholder="Ex: Sim Nord 2010–2023" defaultValue="Sim Plot T3 v2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Parcelle *</label>
              <select className="input-field">
                {MOCK_FIELDS.map((f) => <option key={f.id}>{f.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Jeu de données pluvio</label>
              <input className="input-field" placeholder="Ex: kedah_2010_2023" defaultValue="kedah_2010_2023" />
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">Description</label>
              <input className="input-field" placeholder="Optionnel" />
            </div>
          </div>
          <div className="flex gap-3">
            <button className="btn-primary text-sm">Lancer la simulation</button>
            <button className="btn-secondary text-sm" onClick={() => setShowForm(false)}>Annuler</button>
          </div>
        </div>
      )}

      {/* List */}
      <div className="space-y-4">
        {MOCK_SIMULATIONS.map((sim) => {
          const { icon: StatusIcon, color, badge, label } = statusConfig[sim.status];
          return (
            <div key={sim.id} className="card p-5 flex items-center gap-5">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${statusConfig[sim.status].bg}`}>
                <StatusIcon className={`w-5 h-5 ${color} ${sim.status === 'running' ? 'animate-spin' : ''}`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-semibold text-stone-900 truncate">{sim.name}</p>
                  <span className={`badge ${badge} flex-shrink-0`}>{label}</span>
                </div>
                <p className="text-sm text-stone-400 mt-0.5">
                  {sim.field} · {sim.created_at}
                  {sim.description && ` · ${sim.description}`}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {sim.status === 'completed' && (
                  <button className="btn-primary text-sm" onClick={() => onViewResults(sim.id)}>
                    Résultats
                  </button>
                )}
                <button className="p-2 text-stone-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}

// ─── VIEW: Results ────────────────────────────────────────────────────────────

const COLORS = ['#4ade80','#86efac','#a3e635','#fb923c','#fbbf24','#60a5fa','#c084fc'];

function ViewResults({ simId, onBack }) {
  const [expandedYear, setExpandedYear] = useState(null);
  const sim = MOCK_SIMULATIONS.find((s) => s.id === simId) ?? MOCK_SIMULATIONS[0];

  const cycleInputs  = Math.round(MOCK_YEARLY_RESULTS.reduce((s, r) => s + r.inputs,  0));
  const cycleOutputs = Math.round(MOCK_YEARLY_RESULTS.reduce((s, r) => s + r.outputs, 0));
  const cycleBalance = cycleInputs - cycleOutputs;

  const inputPie = [
    { name: 'N sol initial', value: 340 }, { name: 'Fixation', value: 250 },
    { name: 'Résidus', value: 532 }, { name: 'Fertilisants', value: 2072 },
    { name: 'Dépôts atm.', value: 168 },
  ];
  const outputPie = [
    { name: 'NH₃', value: 350 }, { name: 'Lessivage', value: 560 },
    { name: 'Absorption', value: 1820 }, { name: 'N₂O', value: 182 },
    { name: 'NOx', value: 70 }, { name: 'N₂', value: 140 }, { name: 'Ruissellement', value: 140 },
  ];

  return (
    <>
      <PageHeader title={sim.name} subtitle={`Parcelle : ${sim.field}`}>
        <button className="btn-secondary text-sm flex items-center gap-2" onClick={onBack}>
          <ArrowLeft className="w-4 h-4" /> Retour
        </button>
      </PageHeader>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="card p-6 flex items-center gap-4">
          <div className="w-12 h-12 bg-palm-100 rounded-xl flex items-center justify-center">
            <TrendingUp className="w-6 h-6 text-palm-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-stone-900">{cycleInputs.toLocaleString()}</p>
            <p className="text-sm text-stone-500">kg N/ha — Entrées cycle</p>
          </div>
        </div>
        <div className="card p-6 flex items-center gap-4">
          <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
            <TrendingDown className="w-6 h-6 text-amber-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-stone-900">{cycleOutputs.toLocaleString()}</p>
            <p className="text-sm text-stone-500">kg N/ha — Sorties cycle</p>
          </div>
        </div>
        <div className={`card p-6 flex items-center gap-4 ${cycleBalance >= 0 ? 'border-palm-300 bg-palm-50' : 'border-red-300 bg-red-50'}`}>
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${cycleBalance >= 0 ? 'bg-palm-200' : 'bg-red-100'}`}>
            <Scale className={`w-6 h-6 ${cycleBalance >= 0 ? 'text-palm-700' : 'text-red-600'}`} />
          </div>
          <div>
            <p className={`text-2xl font-bold ${cycleBalance >= 0 ? 'text-palm-800' : 'text-red-700'}`}>
              {cycleBalance >= 0 ? '+' : ''}{cycleBalance.toLocaleString()}
            </p>
            <p className="text-sm text-stone-500">kg N/ha — Bilan cycle</p>
          </div>
        </div>
      </div>

      {/* Annual bar chart */}
      <div className="card p-6 mb-6">
        <h3 className="font-semibold text-stone-800 mb-4">Bilan annuel (kg N/ha)</h3>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={MOCK_YEARLY_RESULTS} barSize={20}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
            <XAxis dataKey="year" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} unit=" kg" />
            <Tooltip formatter={(v) => `${v} kg N/ha`} />
            <Legend />
            <Bar dataKey="inputs"  name="Entrées"  fill="#4ade80" radius={[3,3,0,0]} />
            <Bar dataKey="outputs" name="Sorties"  fill="#fb923c" radius={[3,3,0,0]} />
            <Bar dataKey="balance" name="Bilan"    fill="#60a5fa" radius={[3,3,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Pie charts */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        {[
          { title: 'Répartition des entrées N', data: inputPie },
          { title: 'Répartition des sorties N', data: outputPie },
        ].map(({ title, data }) => (
          <div key={title} className="card p-6">
            <h3 className="font-semibold text-stone-800 mb-4">{title}</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={data} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={3} dataKey="value">
                  {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v) => `${v} kg N/ha`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        ))}
      </div>

      {/* Annual table */}
      <div className="card overflow-hidden">
        <div className="px-6 py-4 border-b border-stone-100">
          <h3 className="font-semibold text-stone-800">Tableau annuel détaillé</h3>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50">
              {['Année', 'Âge', 'Entrées', 'Sorties', 'Bilan', ''].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-stone-500 font-medium last:w-8">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {MOCK_YEARLY_RESULTS.map((row) => (
              <>
                <tr
                  key={row.year}
                  className="border-b border-stone-100 hover:bg-stone-50 cursor-pointer"
                  onClick={() => setExpandedYear(expandedYear === row.year ? null : row.year)}
                >
                  <td className="px-4 py-3 font-medium">{row.year}</td>
                  <td className="px-4 py-3 text-stone-500">{row.age}</td>
                  <td className="px-4 py-3 text-palm-700 font-medium">{row.inputs}</td>
                  <td className="px-4 py-3 text-amber-700 font-medium">{row.outputs}</td>
                  <td className={`px-4 py-3 font-semibold ${row.balance >= 0 ? 'text-palm-700' : 'text-red-600'}`}>
                    {row.balance >= 0 ? '+' : ''}{row.balance}
                  </td>
                  <td className="px-4 py-3 text-stone-400">
                    {expandedYear === row.year ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </td>
                </tr>
                {expandedYear === row.year && (
                  <tr key={`${row.year}-detail`} className="bg-palm-50 border-b border-stone-100">
                    <td colSpan={6} className="px-6 py-4">
                      <div className="grid grid-cols-2 gap-6 text-xs">
                        <div>
                          <p className="font-semibold text-stone-600 mb-2">Détail sorties</p>
                          <ul className="space-y-1">
                            {[
                              ['Volatilisation NH₃', row.nh3],
                              ['Lessivage NO₃⁻', row.leaching],
                              ['Absorption palmiers', row.uptake],
                              ['Émissions N₂O', row.n2o],
                              ['Émissions NOx', row.nox],
                              ['Émissions N₂', row.n2],
                              ['Ruissellement & érosion', row.runoff],
                            ].map(([k, v]) => (
                              <li key={k} className="flex justify-between">
                                <span className="text-stone-500">{k}</span>
                                <span className="font-mono font-medium">{v} kg N/ha</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <p className="font-semibold text-stone-600 mb-2">Indicateurs intermédiaires</p>
                          <ul className="space-y-1">
                            {[
                              ['Humidité sol moy.', '0.62'],
                              ['Drainage moy.', '0.38'],
                              ['Saturation sol moy.', '0.18'],
                              ['Couverture sol', '0.74'],
                              ['N minéral sol', '128 kg N/ha'],
                            ].map(([k, v]) => (
                              <li key={k} className="flex justify-between">
                                <span className="text-stone-500">{k}</span>
                                <span className="font-mono font-medium">{v}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

// ─── Root Mockup ──────────────────────────────────────────────────────────────

export default function Mockup() {
  const [view,         setView]         = useState('dashboard');
  const [selectedField, setSelectedField] = useState(null);
  const [selectedSim,   setSelectedSim]   = useState(null);

  function navigate(to) { setView(to); }

  function handleSelectField(id) { setSelectedField(id); setView('field-detail'); }
  function handleBackToFields()  { setView('fields'); }

  function handleViewResults(id) { setSelectedSim(id); setView('results'); }
  function handleBackToSims()    { setView('simulations'); }

  // Map sidebar nav ids to view ids
  function handleNav(id) {
    if (id === 'results' && selectedSim) { setView('results'); return; }
    setView(id);
  }

  const sidebarId = {
    dashboard: 'dashboard', import: 'import', fields: 'fields',
    'field-detail': 'fields', parameters: 'parameters',
    simulations: 'simulations', results: 'results',
  }[view] ?? view;

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar current={sidebarId} onChange={handleNav} />
      <main className="flex-1 overflow-y-auto">
        {/* Mockup banner */}
        <div className="bg-amber-50 border-b border-amber-200 px-8 py-2 flex items-center gap-2 text-xs text-amber-700">
          <Info className="w-3.5 h-3.5 flex-shrink-0" />
          Maquette statique — données fictives, aucun appel API
        </div>
        <div className="max-w-7xl mx-auto px-8 py-8">
          {view === 'dashboard'    && <ViewDashboard   onNavigate={navigate} />}
          {view === 'import'       && <ViewImport />}
          {view === 'fields'       && <ViewFields       onSelectField={handleSelectField} />}
          {view === 'field-detail' && <ViewFieldDetail  fieldId={selectedField} onBack={handleBackToFields} />}
          {view === 'parameters'   && <ViewParameters />}
          {view === 'simulations'  && <ViewSimulations  onViewResults={handleViewResults} />}
          {view === 'results'      && <ViewResults      simId={selectedSim} onBack={handleBackToSims} />}
        </div>
      </main>
    </div>
  );
}
