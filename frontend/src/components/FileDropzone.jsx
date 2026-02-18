import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileSpreadsheet, CheckCircle2, AlertCircle } from 'lucide-react';

export default function FileDropzone({ onFileAccepted, label, status, message }) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onFileAccepted(acceptedFiles[0]);
      }
    },
    [onFileAccepted]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 1,
  });

  const statusColors = {
    idle: 'border-stone-300 bg-stone-50 hover:bg-stone-100 hover:border-palm-400',
    loading: 'border-sky-300 bg-sky-50',
    success: 'border-palm-400 bg-palm-50',
    error: 'border-red-300 bg-red-50',
  };

  return (
    <div
      {...getRootProps()}
      className={`relative rounded-2xl border-2 border-dashed p-8 text-center cursor-pointer transition-all duration-300 ${
        isDragActive ? 'border-palm-500 bg-palm-50 scale-[1.02]' : statusColors[status || 'idle']
      }`}
    >
      <input {...getInputProps()} />

      {status === 'success' ? (
        <div className="flex flex-col items-center gap-2">
          <CheckCircle2 className="w-10 h-10 text-palm-500" />
          <p className="font-medium text-palm-700">{message || 'Import réussi !'}</p>
        </div>
      ) : status === 'error' ? (
        <div className="flex flex-col items-center gap-2">
          <AlertCircle className="w-10 h-10 text-red-500" />
          <p className="font-medium text-red-700">{message || 'Erreur lors de l\'import'}</p>
        </div>
      ) : status === 'loading' ? (
        <div className="flex flex-col items-center gap-2">
          <div className="w-10 h-10 border-4 border-sky-200 border-t-sky-500 rounded-full animate-spin" />
          <p className="font-medium text-sky-700">Import en cours...</p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3">
          {isDragActive ? (
            <FileSpreadsheet className="w-12 h-12 text-palm-500" />
          ) : (
            <Upload className="w-10 h-10 text-stone-400" />
          )}
          <div>
            <p className="font-medium text-stone-700">
              {isDragActive ? 'Déposez le fichier ici' : label || 'Glissez un fichier CSV ici'}
            </p>
            <p className="text-sm text-stone-500 mt-1">ou cliquez pour sélectionner</p>
          </div>
        </div>
      )}
    </div>
  );
}
