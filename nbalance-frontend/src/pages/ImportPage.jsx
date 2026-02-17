import { useState } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { FileSpreadsheet, Info } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import FileDropzone from '../components/FileDropzone';
import {
  importFieldCharacteristics,
  importYearFieldData,
  importRainfallData,
  importFertilizationData,
} from '../services/api';

const IMPORT_TYPES = [
  {
    key: 'field',
    label: 'Caractéristiques parcelle',
    description: 'Field_name, Localisation, Slope, Texture, Organic_Carbon, pH, CEC...',
    example: 'Field_characteristics_example.csv',
    handler: (file) => importFieldCharacteristics(file),
  },
  {
    key: 'yearfield',
    label: 'Données annuelles',
    description: 'Yield, Understorey_biomass, Legume_fraction, Pruned_frond, Atmospheric_deposition...',
    example: 'Year_Field_data_example.csv',
    handler: (file) => importYearFieldData(file),
  },
  {
    key: 'rainfall',
    label: 'Pluviométrie',
    description: 'Rainfall (mm), Rain frequency — données mensuelles',
    example: 'Rainfall_data_example.csv',
    handler: null, // géré séparément pour le dataset_name
  },
  {
    key: 'fertilization',
    label: 'Fertilisation',
    description: 'Type, Quantity, Composition, Placement — événements mensuels',
    example: 'Fertilization_data_example.csv',
    handler: (file) => importFertilizationData(file),
  },
];

export default function ImportPage() {
  const [statuses, setStatuses] = useState({});
  const [messages, setMessages] = useState({});
  const [rainfallDataset, setRainfallDataset] = useState('default');

  const handleImport = async (key, file) => {
    setStatuses((prev) => ({ ...prev, [key]: 'loading' }));
    setMessages((prev) => ({ ...prev, [key]: '' }));

    try {
      let response;
      if (key === 'rainfall') {
        response = await importRainfallData(file, rainfallDataset);
      } else {
        const type = IMPORT_TYPES.find((t) => t.key === key);
        response = await type.handler(file);
      }

      const data = response.data;
      setStatuses((prev) => ({ ...prev, [key]: 'success' }));
      setMessages((prev) => ({
        ...prev,
        [key]: `${data.imported} enregistrement(s) importé(s)`,
      }));
      toast.success(`${data.imported} enregistrement(s) importé(s)`);
    } catch (err) {
      setStatuses((prev) => ({ ...prev, [key]: 'error' }));
      const errorMsg =
        err.response?.data?.detail || 'Erreur lors de l\'import';
      setMessages((prev) => ({ ...prev, [key]: errorMsg }));
      toast.error(errorMsg);
    }
  };

  return (
    <div>
      <Toaster position="top-right" />

      <PageHeader
        title="Import de données"
        subtitle="Importez vos fichiers CSV pour alimenter la base de données. Chaque type de fichier correspond à une catégorie de données."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {IMPORT_TYPES.map(({ key, label, description, example }) => (
          <div key={key} className="card p-6">
            <div className="flex items-center gap-3 mb-3">
              <FileSpreadsheet className="w-5 h-5 text-palm-600" />
              <h3 className="font-display text-lg text-stone-800">{label}</h3>
            </div>

            <p className="text-sm text-stone-500 mb-1">{description}</p>
            <p className="text-xs text-stone-400 mb-4 flex items-center gap-1">
              <Info className="w-3 h-3" />
              Fichier exemple : {example}
            </p>

            {/* Champ spécial pour le dataset de pluie */}
            {key === 'rainfall' && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-stone-700 mb-1">
                  Nom du jeu de données météo
                </label>
                <input
                  type="text"
                  value={rainfallDataset}
                  onChange={(e) => setRainfallDataset(e.target.value)}
                  placeholder="ex: observed_2008_2015"
                  className="input-field"
                />
              </div>
            )}

            <FileDropzone
              label={`Glissez le fichier ${label}`}
              onFileAccepted={(file) => handleImport(key, file)}
              status={statuses[key]}
              message={messages[key]}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
