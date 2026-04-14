import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Upload as UploadIcon, CheckCircle2, AlertCircle } from 'lucide-react';

export default function ImportPage() {
  const queryClient = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [ftp, setFtp] = useState<string>('');
  
  const mutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('Nie wybrano pliku');
      const formData = new FormData();
      formData.append('file', file);
      if (ftp) formData.append('ftp', ftp);
      
      const res = await api.post('/workouts/import-fit', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workouts'] });
      queryClient.invalidateQueries({ queryKey: ['calendar'] });
      setFile(null);
    }
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      mutation.reset();
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.toLowerCase().endsWith('.fit')) {
        setFile(droppedFile);
        mutation.reset();
      }
    }
  };

  return (
    <div className="bg-card p-8 rounded-lg border border-border shadow-sm max-w-2xl mx-auto">
      <h2 className="font-heading text-3xl font-bold mb-8 text-foreground text-center">Import Treningu (.FIT)</h2>
      
      <div 
        className={`border-2 border-dashed rounded-lg p-12 flex flex-col items-center justify-center text-center transition-colors
          ${file ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'}
        `}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <UploadIcon className={`w-12 h-12 mb-4 ${file ? 'text-primary' : 'text-muted-foreground'}`} />
        
        {file ? (
          <div className="space-y-2">
            <p className="text-lg font-medium text-foreground">{file.name}</p>
            <p className="text-sm text-muted-foreground">Rozmiar: {(file.size / 1024).toFixed(1)} KB</p>
            <button 
              onClick={() => { setFile(null); mutation.reset(); }}
              className="text-sm text-destructive hover:underline mt-2"
            >
              Usuń i wybierz inny plik
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-lg font-medium text-foreground">Przeciągnij i upuść plik .FIT tutaj</p>
            <p className="text-sm text-muted-foreground">lub kliknij przycisk poniżej, aby wybrać plik</p>
            <label className="inline-block mt-4 px-6 py-2 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-medium rounded cursor-pointer transition-colors">
              Wybierz Plik
              <input type="file" accept=".fit" className="hidden" onChange={handleFileChange} />
            </label>
          </div>
        )}
      </div>

      <div className="mt-8 space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-muted-foreground">Opcjonalnie: Aktualne FTP (Waty) dla tego treningu</label>
          <input 
            type="number" 
            value={ftp}
            onChange={(e) => setFtp(e.target.value)}
            placeholder="Pozostaw puste, aby użyć FTP z profilu"
            className="w-full bg-background border border-border rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <button
          onClick={() => mutation.mutate()}
          disabled={!file || mutation.isPending}
          className="w-full py-3 bg-z5 hover:bg-z5/90 text-white font-bold rounded-md transition-colors disabled:opacity-50 uppercase tracking-wider mt-4"
        >
          {mutation.isPending ? 'Przetwarzanie...' : 'Importuj Trening'}
        </button>
      </div>

      {mutation.isSuccess && (
        <div className="mt-6 p-4 bg-z3/10 border border-z3/20 rounded-md flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-z3 mt-0.5" />
          <div>
            <h4 className="font-bold text-z3">Import zakończony pomyślnie!</h4>
            <p className="text-sm text-muted-foreground mt-1">
              Przetworzono próbek: {mutation.data.samples_count}<br/>
              TSS: {Math.round(mutation.data.metrics?.tss || 0)} | 
              NP: {Math.round(mutation.data.metrics?.np || 0)}W
            </p>
          </div>
        </div>
      )}

      {mutation.isError && (
        <div className="mt-6 p-4 bg-destructive/10 border border-destructive/20 rounded-md flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-destructive mt-0.5" />
          <div>
            <h4 className="font-bold text-destructive">Błąd importu</h4>
            <p className="text-sm text-destructive/80 mt-1">
              {(mutation.error as any).response?.data?.detail || mutation.error.message || 'Wystąpił nieoczekiwany błąd.'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}