import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Calendar, Layers, Trash2, Eye } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import { getFields, deleteField } from '../services/api';
import toast, { Toaster } from 'react-hot-toast';

export default function FieldsPage() {
  const [fields, setFields] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchFields = async () => {
    try {
      const res = await getFields();
      setFields(res.data);
    } catch {
      toast.error('Erreur lors du chargement des parcelles');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFields();
  }, []);

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Supprimer la parcelle "${name}" et toutes ses données ?`)) return;
    try {
      await deleteField(id);
      toast.success(`Parcelle "${name}" supprimée`);
      fetchFields();
    } catch {
      toast.error('Erreur lors de la suppression');
    }
  };

  return (
    <div>
      <Toaster position="top-right" />

      <PageHeader
        title="Parcelles"
        subtitle="Liste des parcelles importées avec leurs caractéristiques."
      >
        <Link to="/import" className="btn-primary">
          Importer
        </Link>
      </PageHeader>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-4 border-palm-200 border-t-palm-600 rounded-full animate-spin" />
        </div>
      ) : fields.length === 0 ? (
        <div className="card p-12 text-center">
          <MapPin className="w-12 h-12 text-stone-300 mx-auto mb-4" />
          <p className="text-stone-500">Aucune parcelle importée</p>
          <Link to="/import" className="text-palm-600 hover:text-palm-700 text-sm font-medium mt-2 inline-block">
            Importer des données →
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {fields.map((field) => (
            <div key={field.id} className="card p-6 group">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-display text-lg text-stone-900">
                    {field.field_name}
                  </h3>
                  <div className="flex items-center gap-1.5 mt-1 text-sm text-stone-500">
                    <MapPin className="w-3.5 h-3.5" />
                    {field.localisation}
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(field.id, field.field_name)}
                  className="opacity-0 group-hover:opacity-100 p-2 rounded-lg hover:bg-red-50 text-stone-400 hover:text-red-500 transition-all"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-stone-600">
                  <Calendar className="w-4 h-4 text-stone-400" />
                  <span>
                    {field.year_planting} → {field.end_field}
                    <span className="text-stone-400 ml-1">
                      ({field.end_field - field.year_planting} ans)
                    </span>
                  </span>
                </div>
                <div className="flex items-center gap-2 text-stone-600">
                  <Layers className="w-4 h-4 text-stone-400" />
                  <span>{field.texture || '—'} · pH {field.ph || '—'} · C org. {field.organic_carbon || '—'}%</span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-stone-100 flex items-center gap-2">
                <span className="badge-info">Pente {field.slope}%</span>
                <span className={field.terraces === 'Yes' ? 'badge-success' : 'badge-warning'}>
                  {field.terraces === 'Yes' ? 'Terrasses' : 'Sans terrasses'}
                </span>
              </div>

              <Link
                to={`/fields/${field.id}`}
                className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-palm-600 hover:text-palm-700 transition-colors"
              >
                <Eye className="w-4 h-4" />
                Voir le détail
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
