import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Map,
  FlaskConical,
  Upload,
  ArrowRight,
  Leaf,
  Droplets,
  Wind,
  Sprout,
} from 'lucide-react';
import PageHeader from '../components/PageHeader';
import { getFields, getSimulations } from '../services/api';

const FLUX_CARDS = [
  {
    icon: Sprout,
    label: 'Entrées N',
    items: ['Sol initial', 'Fixation légumineuses', 'Résidus', 'Fertilisants', 'Dépôt atm.'],
    color: 'palm',
  },
  {
    icon: Wind,
    label: 'Sorties N',
    items: ['Volatilisation', 'Lessivage', 'Captation palmier', 'N₂O', 'NOx', 'N₂', 'Ruissellement'],
    color: 'soil',
  },
];

export default function Dashboard() {
  const [fields, setFields] = useState([]);
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getFields(), getSimulations()])
      .then(([fieldsRes, simsRes]) => {
        setFields(fieldsRes.data);
        setSimulations(simsRes.data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageHeader
        title="NBalance"
        subtitle="Outil de diagnostic et d'aide à la décision pour le calcul du bilan azoté sur le cycle complet du palmier à huile."
      />

      {/* Quick stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
        <Link to="/fields" className="card p-6 group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-stone-500 font-medium">Parcelles</p>
              <p className="text-3xl font-display text-stone-900 mt-1">
                {loading ? '—' : fields.length}
              </p>
            </div>
            <div className="w-12 h-12 bg-palm-100 rounded-xl flex items-center justify-center group-hover:bg-palm-200 transition-colors">
              <Map className="w-6 h-6 text-palm-600" />
            </div>
          </div>
        </Link>

        <Link to="/simulations" className="card p-6 group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-stone-500 font-medium">Simulations</p>
              <p className="text-3xl font-display text-stone-900 mt-1">
                {loading ? '—' : simulations.length}
              </p>
            </div>
            <div className="w-12 h-12 bg-sky-100 rounded-xl flex items-center justify-center group-hover:bg-sky-200 transition-colors">
              <FlaskConical className="w-6 h-6 text-sky-600" />
            </div>
          </div>
        </Link>

        <Link to="/import" className="card p-6 group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-stone-500 font-medium">Importer</p>
              <p className="text-lg font-medium text-stone-700 mt-1">Fichiers CSV</p>
            </div>
            <div className="w-12 h-12 bg-soil-100 rounded-xl flex items-center justify-center group-hover:bg-soil-200 transition-colors">
              <Upload className="w-6 h-6 text-soil-600" />
            </div>
          </div>
        </Link>
      </div>

      {/* Flux overview */}
      <h2 className="text-xl font-display text-stone-800 mb-4">Flux d'azote modélisés</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
        {FLUX_CARDS.map(({ icon: Icon, label, items, color }) => (
          <div key={label} className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                  color === 'palm' ? 'bg-palm-100' : 'bg-soil-100'
                }`}
              >
                <Icon
                  className={`w-5 h-5 ${
                    color === 'palm' ? 'text-palm-600' : 'text-soil-600'
                  }`}
                />
              </div>
              <h3 className="font-display text-lg text-stone-800">{label}</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {items.map((item) => (
                <span
                  key={item}
                  className={`text-xs px-3 py-1.5 rounded-full font-medium ${
                    color === 'palm'
                      ? 'bg-palm-50 text-palm-700 border border-palm-200'
                      : 'bg-soil-50 text-soil-700 border border-soil-200'
                  }`}
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Getting started */}
      {fields.length === 0 && !loading && (
        <div className="card p-8 text-center border-dashed border-2 border-palm-300 bg-palm-50/30">
          <Leaf className="w-12 h-12 text-palm-400 mx-auto mb-4" />
          <h3 className="font-display text-xl text-stone-800 mb-2">Pour commencer</h3>
          <p className="text-stone-500 mb-6 max-w-md mx-auto">
            Importez vos fichiers CSV (caractéristiques parcelle, données annuelles, pluviométrie et fertilisation) pour démarrer votre première simulation.
          </p>
          <Link to="/import" className="btn-primary inline-flex items-center gap-2">
            Importer des données
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}
    </div>
  );
}
