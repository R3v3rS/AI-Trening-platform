import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { PlusCircle, Trash2, GripVertical, Save } from 'lucide-react';
import * as Dialog from '@radix-ui/react-dialog';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

export type Block = {
  id: string;
  type: 'warmup' | 'steady' | 'interval' | 'cooldown';
  duration: number; // in seconds
  power?: number; // watts
  power_start?: number;
  power_end?: number;
  repeat?: number;
  on_duration?: number;
  off_duration?: number;
  on_power?: number;
  off_power?: number;
};

export function AddWorkoutModal({ date, isOpen, onOpenChange }: { date: string, isOpen: boolean, onOpenChange: (open: boolean) => void }) {
  const queryClient = useQueryClient();
  const [type, setType] = useState('z2');
  const [notes, setNotes] = useState('');
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [templateName, setTemplateName] = useState('');
  const [showTemplateNameInput, setShowTemplateNameInput] = useState(false);

  const { data: templates } = useQuery({
    queryKey: ['templates'],
    queryFn: async () => {
      const res = await api.get('/templates');
      return res.data;
    }
  });

  const loadTemplate = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = e.target.value;
    if (!id) return;
    const t = templates?.find((x: any) => x.id.toString() === id);
    if (t) {
      setType(t.type || 'z2');
      setNotes(t.description || '');
      if (t.structured_steps) {
        try {
          setBlocks(JSON.parse(t.structured_steps));
        } catch (e) {
          setBlocks([]);
        }
      } else {
        setBlocks([]);
      }
    }
  };

  const saveTemplateMutation = useMutation({
    mutationFn: async () => {
      await api.post('/templates', {
        name: templateName,
        description: notes,
        type: type,
        structured_steps: blocks.length > 0 ? JSON.stringify(blocks) : null
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      setShowTemplateNameInput(false);
      setTemplateName('');
      alert('Zapisano jako nowy szablon!');
    }
  });

  const addBlock = (blockType: Block['type']) => {
    const newBlock: Block = {
      id: Math.random().toString(36).substr(2, 9),
      type: blockType,
      duration: 300,
    };
    
    if (blockType === 'warmup') {
      newBlock.power_start = 80;
      newBlock.power_end = 150;
    } else if (blockType === 'cooldown') {
      newBlock.power_start = 150;
      newBlock.power_end = 80;
    } else if (blockType === 'steady') {
      newBlock.power = 180;
    } else if (blockType === 'interval') {
      newBlock.repeat = 5;
      newBlock.on_duration = 60;
      newBlock.on_power = 250;
      newBlock.off_duration = 60;
      newBlock.off_power = 120;
    }
    
    setBlocks([...blocks, newBlock]);
  };

  const updateBlock = (id: string, updates: Partial<Block>) => {
    setBlocks(blocks.map(b => b.id === id ? { ...b, ...updates } : b));
  };

  const removeBlock = (id: string) => {
    setBlocks(blocks.filter(b => b.id !== id));
  };

  const totalDuration = blocks.reduce((acc, b) => {
    if (b.type === 'interval') {
      return acc + ((b.repeat || 1) * ((b.on_duration || 0) + (b.off_duration || 0)));
    }
    return acc + (b.duration || 0);
  }, 0);

  const onDragEnd = (result: any) => {
    if (!result.destination) return;
    const items = Array.from(blocks);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    setBlocks(items);
  };

  const mutation = useMutation({
    mutationFn: async () => {
      const payload = {
        planned_date: date,
        type,
        duration_sec: totalDuration > 0 ? totalDuration : 3600, // fallback
        notes,
        structured_steps: blocks.length > 0 ? JSON.stringify(blocks) : null
      };
      await api.post('/planned-workouts', payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar'] });
      onOpenChange(false);
      setType('z2');
      setNotes('');
      setBlocks([]);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate();
  };

  return (
    <Dialog.Root open={isOpen} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 grid w-full max-w-2xl translate-x-[-50%] translate-y-[-50%] gap-4 border border-border bg-card p-6 shadow-lg sm:rounded-lg max-h-[90vh] overflow-y-auto">
          <Dialog.Title className="text-lg font-bold font-heading flex justify-between items-center">
            <span>Zaplanuj trening na {date}</span>
            <span className="text-sm font-normal text-muted-foreground">
              Czas: {Math.floor(totalDuration / 60)} min {totalDuration % 60} sek
            </span>
          </Dialog.Title>
          
          <form onSubmit={handleSubmit} className="space-y-6 mt-2">
            {templates && templates.length > 0 && (
              <div className="bg-z5/10 border border-z5/20 p-3 rounded-lg flex items-center justify-between">
                <span className="text-sm font-medium text-z5">Zastosuj Szablon:</span>
                <select 
                  onChange={loadTemplate}
                  className="bg-background border border-border rounded px-2 py-1 text-sm max-w-[200px]"
                >
                  <option value="">-- Wybierz --</option>
                  {templates.map((t: any) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>
            )}
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Kategoria główna</label>
                <select 
                  value={type} 
                  onChange={e => setType(e.target.value)}
                  className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm"
                >
                  <option value="recovery">Aktywna Regeneracja</option>
                  <option value="z2">Baza Tlenowa (Z2)</option>
                  <option value="tempo">Tempo (Z3)</option>
                  <option value="vo2max">Interwały VO2Max</option>
                  <option value="long_ride">Długa Jazda</option>
                  <option value="ftp_test">Test FTP</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Notatki dla siebie / trenera</label>
                <textarea 
                  value={notes} 
                  onChange={e => setNotes(e.target.value)}
                  className="w-full bg-background border border-border rounded-md px-3 py-2 min-h-[40px] text-sm"
                  placeholder="Np. Skup się na kadencji..."
                />
              </div>
            </div>

            <div className="space-y-4 border-t border-border pt-4">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium">Kroki (Workout Builder)</label>
                <div className="flex gap-2">
                  <button type="button" onClick={() => addBlock('warmup')} className="text-xs bg-muted hover:bg-muted/80 px-2 py-1 rounded">Rozgrzewka</button>
                  <button type="button" onClick={() => addBlock('steady')} className="text-xs bg-muted hover:bg-muted/80 px-2 py-1 rounded">Stała Moc</button>
                  <button type="button" onClick={() => addBlock('interval')} className="text-xs bg-muted hover:bg-muted/80 px-2 py-1 rounded">Interwał</button>
                  <button type="button" onClick={() => addBlock('cooldown')} className="text-xs bg-muted hover:bg-muted/80 px-2 py-1 rounded">Schłodzenie</button>
                </div>
              </div>

              {blocks.length === 0 ? (
                <div className="text-center p-8 border-2 border-dashed border-border rounded-lg text-muted-foreground text-sm">
                  Kliknij przyciski powyżej, aby dodać kroki treningu. Jeśli zostawisz to pole puste, zostanie wygenerowany prosty blok na podstawie kategorii.
                </div>
              ) : (
                <DragDropContext onDragEnd={onDragEnd}>
                  <Droppable droppableId="workout-blocks">
                    {(provided) => (
                      <div {...provided.droppableProps} ref={provided.innerRef} className="space-y-3">
                        {blocks.map((block, index) => (
                          <Draggable key={block.id} draggableId={block.id} index={index}>
                            {(provided) => (
                              <div
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                className="flex gap-3 items-start bg-muted/30 p-3 rounded-lg border border-border/50 shadow-sm"
                              >
                                <div {...provided.dragHandleProps} className="mt-2 text-muted-foreground cursor-grab active:cursor-grabbing">
                                  <GripVertical className="w-4 h-4" />
                                </div>
                                
                                <div className="flex-1 space-y-2">
                                  <div className="flex justify-between items-center">
                                    <span className="text-xs font-bold uppercase tracking-wider text-z5">{block.type}</span>
                                    <button type="button" onClick={() => removeBlock(block.id)} className="text-destructive hover:text-destructive/80"><Trash2 className="w-4 h-4" /></button>
                                  </div>
                                  
                                  {block.type === 'warmup' || block.type === 'cooldown' ? (
                                    <div className="flex flex-wrap gap-2 text-sm">
                                      <label className="flex items-center gap-1">Czas: <input type="number" className="w-16 bg-background border border-border rounded px-1" value={block.duration / 60} onChange={e => updateBlock(block.id, { duration: Number(e.target.value) * 60 })} /> min</label>
                                      <label className="flex items-center gap-1">Od: <input type="number" className="w-16 bg-background border border-border rounded px-1" value={block.power_start} onChange={e => updateBlock(block.id, { power_start: Number(e.target.value) })} /> W</label>
                                      <label className="flex items-center gap-1">Do: <input type="number" className="w-16 bg-background border border-border rounded px-1" value={block.power_end} onChange={e => updateBlock(block.id, { power_end: Number(e.target.value) })} /> W</label>
                                    </div>
                                  ) : block.type === 'steady' ? (
                                    <div className="flex flex-wrap gap-2 text-sm">
                                      <label className="flex items-center gap-1">Czas: <input type="number" className="w-16 bg-background border border-border rounded px-1" value={block.duration / 60} onChange={e => updateBlock(block.id, { duration: Number(e.target.value) * 60 })} /> min</label>
                                      <label className="flex items-center gap-1">Moc: <input type="number" className="w-16 bg-background border border-border rounded px-1" value={block.power} onChange={e => updateBlock(block.id, { power: Number(e.target.value) })} /> W</label>
                                    </div>
                                  ) : block.type === 'interval' ? (
                                    <div className="space-y-2 text-sm">
                                      <div className="flex flex-wrap gap-2">
                                        <label className="flex items-center gap-1">Powtórzenia: <input type="number" className="w-16 bg-background border border-border rounded px-1" value={block.repeat} onChange={e => updateBlock(block.id, { repeat: Number(e.target.value) })} /> x</label>
                                      </div>
                                      <div className="flex flex-wrap gap-2 items-center">
                                        <label className="flex items-center gap-1 text-z5 font-medium">Praca:</label>
                                        <label className="flex items-center gap-1">Czas: <input type="number" className="w-16 bg-background border border-border rounded px-1" value={(block.on_duration || 0) / 60} onChange={e => updateBlock(block.id, { on_duration: Number(e.target.value) * 60 })} /> min</label>
                                        <label className="flex items-center gap-1">Moc: <input type="number" className="w-16 bg-background border border-border rounded px-1" value={block.on_power} onChange={e => updateBlock(block.id, { on_power: Number(e.target.value) })} /> W</label>
                                      </div>
                                      <div className="flex flex-wrap gap-2 items-center">
                                        <label className="flex items-center gap-1 text-z2 font-medium">Odpoczynek:</label>
                                        <label className="flex items-center gap-1">Czas: <input type="number" className="w-16 bg-background border border-border rounded px-1" value={(block.off_duration || 0) / 60} onChange={e => updateBlock(block.id, { off_duration: Number(e.target.value) * 60 })} /> min</label>
                                        <label className="flex items-center gap-1">Moc: <input type="number" className="w-16 bg-background border border-border rounded px-1" value={block.off_power} onChange={e => updateBlock(block.id, { off_power: Number(e.target.value) })} /> W</label>
                                      </div>
                                    </div>
                                  ) : null}
                                </div>
                              </div>
                            )}
                          </Draggable>
                        ))}
                        {provided.placeholder}
                      </div>
                    )}
                  </Droppable>
                </DragDropContext>
              )}
            </div>

            <div className="flex justify-between items-center pt-4 border-t border-border">
              <div className="flex items-center gap-2">
                {!showTemplateNameInput ? (
                  <button 
                    type="button"
                    onClick={() => setShowTemplateNameInput(true)}
                    className="flex items-center gap-1 text-sm text-z5 hover:underline"
                  >
                    <Save className="w-4 h-4" /> Zapisz jako szablon
                  </button>
                ) : (
                  <div className="flex items-center gap-2">
                    <input 
                      type="text" 
                      value={templateName}
                      onChange={e => setTemplateName(e.target.value)}
                      placeholder="Nazwa szablonu..."
                      className="bg-background border border-border rounded px-2 py-1 text-sm"
                    />
                    <button 
                      type="button"
                      onClick={() => saveTemplateMutation.mutate()}
                      disabled={!templateName || saveTemplateMutation.isPending}
                      className="px-3 py-1 bg-z3 hover:bg-z3/90 text-white rounded text-sm disabled:opacity-50"
                    >
                      Zapisz
                    </button>
                    <button 
                      type="button"
                      onClick={() => setShowTemplateNameInput(false)}
                      className="text-sm text-muted-foreground hover:underline"
                    >
                      Anuluj
                    </button>
                  </div>
                )}
              </div>
              
              <div className="flex gap-3">
                <button 
                  type="button" 
                  onClick={() => onOpenChange(false)}
                  className="px-4 py-2 border border-border rounded hover:bg-muted transition-colors"
                >
                  Anuluj
                </button>
                <button 
                  type="submit"
                  disabled={mutation.isPending}
                  className="px-4 py-2 bg-z5 hover:bg-z5/90 text-white rounded font-medium disabled:opacity-50"
                >
                  {mutation.isPending ? 'Zapisywanie...' : 'Zapisz Plan'}
                </button>
              </div>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}