import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FlaskConical, Plus, Trash2, Clock, CheckCircle2, AlertCircle, Loader2, BarChart3,
} from 'lucide-react';
import PageHeader from '../components/PageHeader';
import {
  getSimulations, createSimulation, deleteSimulation,
  getFields,
} from '../services/api';
import toast, { Toaster } from 'react-hot-toast';

const STATUS_CONFIG = {
  pending: { icon: Clock, color: 'text-amber-500', bg: 'bg-amber-50', label: 'En attente' },
  running: { icon: Loader2, color: 'text-sky-500', bg: 'bg-sky-50', label: 'En cours', animate: true },
  completed: { icon: CheckCircle2, color: 'text-palm-500', bg: 'bg-palm-50', label: 'Terminée' },
  error: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-50', label: 'Erreur' },
};

export default function SimulationsPage() {
  const [simulations, setSimulations] = useState([]);
  const [fields, setFields] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [creating, setCreating] = useState(false);

  // Form
  const [formName, setFormName] = useState('');
  const [formFieldId, setFormFieldId] = useState('');
  const [formDataset, setFormDataset] = useState('default');
  const [formDescription, setFormDescription] = useState('');

  const fetchData = async () => {
    try {
      const [simsRes, fieldsRes] = await Promise.all([getSimulations(), getFields()]);
      setSimulations(simsRes.data);
      setFields(fieldsRes.data);
    } catch {
      toast.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!formName || !formFieldId) {
      toast.error('Veuillez remplir les champs obligatoires');
      return;
    }
    setCreating(true);
    try {
      await createSimulation({
        name: formName,
        field_id: parseInt(formFieldId),
        rainfall_dataset: formDataset,
        description: formDescription,
      });
      toast.success('Simulation créée et exécutée !');
      setShowForm(false);
      setFormName('');
      setFormFieldId('');
      setFormDataset('default');
      setFormDescription('');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erreur lors de la création');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Supprimer la simulation "${name}" ?`)) return;
    try {
      await deleteSimulation(id);
      toast.success('Simulation supprimée');
      fetchData();
    } catch {
      toast.error('Erreur lors de la suppression');
    }
  };

  return (
    <div>
      <Toaster position="top-right" />

      <PageHeader
        title="Simulations"
        subtitle="Lancez des simulations de bilan azoté sur vos parcelles."
      >
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Nouvelle simulation
        </button>
      </PageHeader>

      {/* Formulaire création */}
      {showForm && (
        <form onSubmit={handleCreate} className="card p-6 mb-6">
          <h3 className="font-display text-lg text-stone-800 mb-4">Nouvelle simulation</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Nom *
              </label>
              <input
                type="text"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="ex: Sangara baseline"
                className="input-field"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Parcelle *
              </label>
              <select
                value={formFieldId}
                onChange={(e) => setFormFieldId(e.target.value)}
                className="input-field"
                required
              >
                <option value="">Sélectionner une parcelle</option>
                {fields.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.field_name} ({f.localisation})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Jeu de données météo
              </label>
              <input
                type="text"
                value={formDataset}
                onChange={(e) => setFormDataset(e.target.value)}
                placeholder="default"
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Description
              </label>
              <input
                type="text"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                placeholder="Optionnel"
                className="input-field"
              />
            </div>
          </div>
          <div className="flex items-center gap-3 mt-5">
            <button type="submit" disabled={creating} className="btn-primary flex items-center gap-2">
              {creating && <Loader2 className="w-4 h-4 animate-spin" />}
              {creating ? 'Exécution...' : 'Lancer la simulation'}
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">
              Annuler
            </button>
          </div>
        </form>
      )}

      {/* Liste simulations */}
      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-4 border-palm-200 border-t-palm-600 rounded-full animate-spin" />
        </div>
      ) : simulations.length === 0 ? (
        <div className="card p-12 text-center">
          <FlaskConical className="w-12 h-12 text-stone-300 mx-auto mb-4" />
          <p className="text-stone-500">Aucune simulation</p>
        </div>
      ) : (
        <div className="space-y-3">
          {simulations.map((sim) => {
            const statusConf = STATUS_CONFIG[sim.status] || STATUS_CONFIG.pending;
            const StatusIcon = statusConf.icon;

            return (
              <div key={sim.id} className="card p-5 flex items-center justify-between group">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${statusConf.bg}`}>
                    <StatusIcon
                      className={`w-5 h-5 ${statusConf.color} ${statusConf.animate ? 'animate-spin' : ''}`}
                    />
                  </div>
                  <div>
                    <h4 className="font-medium text-stone-800">{sim.name}</h4>
                    <p className="text-sm text-stone-500">
                      Parcelle #{sim.field_id} · {new Date(sim.created_at).toLocaleDateString('fr-FR')}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`badge ${statusConf.bg} ${statusConf.color}`}>
                    {statusConf.label}
                  </span>

                  {sim.status === 'completed' && (
                    <Link
                      to={`/results/${sim.id}`}
                      className="btn-secondary flex items-center gap-1.5 text-sm py-2 px-3"
                    >
                      <BarChart3 className="w-4 h-4" />
                      Résultats
                    </Link>
                  )}

                  <button
                    onClick={() => handleDelete(sim.id, sim.name)}
                    className="opacity-0 group-hover:opacity-100 p-2 rounded-lg hover:bg-red-50 text-stone-400 hover:text-red-500 transition-all"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
