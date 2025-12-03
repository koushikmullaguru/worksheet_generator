import { useState } from "react";
import { Button } from "./ui/button";
import { Switch } from "./ui/switch";
import { Label } from "./ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "./ui/dialog";
import { Input } from "./ui/input";
import { Download, Copy, Printer, Save, FileText } from "lucide-react";
import { motion } from "framer-motion";
import { QuestionCard } from "./QuestionCard";
import { useToast } from "../hooks/use-toast";
import * as api from "../lib/api";
import * as exportUtils from "../lib/exportUtils";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';

interface ResultsPanelProps {
  questions: api.Question[];
  topic: string;
  topicId?: string;
  onQuestionsChange: (questions: api.Question[]) => void;
  isLoading?: boolean;
}

export function ResultsPanel({ questions, topic, topicId, onQuestionsChange, isLoading }: ResultsPanelProps) {
  const [showAnswers, setShowAnswers] = useState(false);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [worksheetName, setWorksheetName] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<'pdf' | 'txt'>('pdf');
  const [exportIncludeAnswers, setExportIncludeAnswers] = useState(false);
  const { toast } = useToast();

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = questions.findIndex(q => q.id === active.id);
      const newIndex = questions.findIndex(q => q.id === over.id);
      
      onQuestionsChange(arrayMove(questions, oldIndex, newIndex));
      
      toast({
        title: "Questions reordered",
        description: "Question order has been updated",
      });
    }
  };

  const handleRegenerate = (id: string) => {
    toast({
      title: "Regenerating question",
      description: "This will generate a new question...",
    });
  };

  const handleUpdate = (id: string, updates: Partial<api.Question>) => {
    const updated = questions.map(q => q.id === id ? { ...q, ...updates } : q);
    onQuestionsChange(updated);
    toast({
      title: "Question updated",
      description: "Changes saved successfully",
    });
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const sanitizedTopic = topic.replace(/[^a-z0-9]/gi, '_').toLowerCase();
      const timestamp = new Date().toISOString().slice(0, 10);
      const filename = `worksheet_${sanitizedTopic}_${timestamp}`;

      await exportUtils.exportWorksheet(
        topic,
        questions,
        {
          format: exportFormat,
          includeAnswers: exportIncludeAnswers,
          filename
        }
      );

      toast({
        title: "Export successful",
        description: `Worksheet exported as ${exportFormat.toUpperCase()}`,
      });
      setExportDialogOpen(false);
    } catch (error) {
      console.error('Export error:', error);
      toast({
        title: "Export failed",
        description: error instanceof Error ? error.message : 'Failed to export worksheet',
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportPDF = () => {
    setExportDialogOpen(true);
  };

  const handleCopy = () => {
    const text = questions.map((q, i) => 
      `Q${i + 1}. ${q.text}\n${q.options ? q.options.map((o, j) => `${String.fromCharCode(65 + j)}. ${o}`).join('\n') : ''}`
    ).join('\n\n');
    
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied to clipboard",
      description: "Worksheet content has been copied",
    });
  };

  const handlePrint = () => {
    window.print();
    toast({
      title: "Opening print dialog",
      description: "Prepare your worksheet for printing",
    });
  };

  const handleSave = async () => {
    if (!worksheetName.trim() || !topicId) return;
    
    setIsSaving(true);
    try {
      const questionIds = questions.map(q => q.id);
      await api.saveWorksheet(worksheetName, topicId, questionIds, '');
      
      toast({
        title: "Worksheet saved",
        description: `"${worksheetName}" has been saved to your library`,
      });
      setSaveDialogOpen(false);
      setWorksheetName('');
    } catch (error) {
      console.error('Error saving worksheet:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to save worksheet',
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (questions.length === 0) {
    return (
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-center justify-center h-full p-12 text-center"
      >
        <div className="space-y-4 max-w-md">
          <FileText className="h-16 w-16 mx-auto text-muted-foreground" />
          <h3 className="text-xl font-semibold">No Worksheet Generated</h3>
          <p className="text-muted-foreground">
            Select your preferences from the filter panel and click Generate to create a custom worksheet.
          </p>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="space-y-4"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold">{topic || 'Generated Worksheet'}</h2>
            <p className="text-sm text-muted-foreground">
              {questions.length} question{questions.length > 1 ? 's' : ''} • 
              Total marks: {questions.reduce((sum, q) => sum + q.marks, 0)}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Label htmlFor="show-answers" className="cursor-pointer">Show answers</Label>
            <Switch 
              id="show-answers"
              checked={showAnswers} 
              onCheckedChange={setShowAnswers}
            />
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={handleExportPDF}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" size="sm" onClick={handleCopy}>
            <Copy className="h-4 w-4 mr-2" />
            Copy
          </Button>
          <Button variant="outline" size="sm" onClick={handlePrint}>
            <Printer className="h-4 w-4 mr-2" />
            Print
          </Button>
          <Button variant="outline" onClick={() => setSaveDialogOpen(true)}>
            <Save className="h-4 w-4 mr-2" />
            Save Worksheet
          </Button>
        </div>
      </motion.div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={questions.map(q => q.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-4">
            {questions.map((question, index) => (
              <QuestionCard
                key={question.id}
                question={question}
                index={index}
                showAnswers={showAnswers}
                onRegenerate={handleRegenerate}
                onUpdate={handleUpdate}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>

      <Dialog open={saveDialogOpen} onOpenChange={setSaveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Save Worksheet</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Worksheet Name</Label>
              <Input
                id="name"
                placeholder="e.g., Control and Coordination - Practice Set 1"
                value={worksheetName}
                onChange={(e) => setWorksheetName(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSaveDialogOpen(false)} disabled={isSaving}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={!worksheetName.trim() || isSaving}>
              {isSaving ? 'Saving...' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={exportDialogOpen} onOpenChange={setExportDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Export Worksheet</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="format">Export Format</Label>
              <select 
                id="format"
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value as 'pdf' | 'txt')}
                className="w-full px-3 py-2 border border-input rounded-md text-sm bg-background"
              >
                <option value="pdf">PDF (Formatted)</option>
                <option value="txt">Text File (Plain)</option>
              </select>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="include-answers"
                checked={exportIncludeAnswers}
                onChange={(e) => setExportIncludeAnswers(e.target.checked)}
                className="cursor-pointer"
              />
              <Label htmlFor="include-answers" className="cursor-pointer">
                Include answers and explanations
              </Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setExportDialogOpen(false)} disabled={isExporting}>
              Cancel
            </Button>
            <Button onClick={handleExport} disabled={isExporting}>
              {isExporting ? 'Exporting...' : 'Export'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
