import { useState } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { ChevronDown, Edit2, RefreshCw, Image as ImageIcon, Save, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import * as api from "../lib/api";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical } from "lucide-react";

interface QuestionCardProps {
  question: api.Question;
  index: number;
  showAnswers: boolean;
  onRegenerate: (id: string) => void;
  onUpdate: (id: string, updates: Partial<api.Question>) => void;
}

export function QuestionCard({ question, index, showAnswers, onRegenerate, onUpdate }: QuestionCardProps) {
  const [isOpen, setIsOpen] = useState(showAnswers);
  const [isEditing, setIsEditing] = useState(false);
  const [imageOpen, setImageOpen] = useState(false);
  const [editData, setEditData] = useState(question);
  
  // Debug: Log question data
  console.log(`Question ${index + 1} data:`, question);

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: question.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  useState(() => {
    setIsOpen(showAnswers);
  });

  const handleSave = () => {
    onUpdate(question.id, editData);
    setIsEditing(false);
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'mcq': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'short': return 'bg-purple-500/10 text-purple-500 border-purple-500/20';
      case 'long': return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
      case 'image': return 'bg-green-500/10 text-green-500 border-green-500/20';
      default: return '';
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'mcq': return 'MCQ';
      case 'short': return 'Short Answer';
      case 'long': return 'Long Answer';
      case 'image': return 'Image-based';
      default: return type;
    }
  };

  return (
    <>
      <motion.div
        ref={setNodeRef}
        style={style}
        layout
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ delay: index * 0.05 }}
      >
        <Card className="question-card p-6 space-y-4">
          <div className="flex items-start gap-4">
            <button
              className="mt-1 cursor-grab active:cursor-grabbing touch-none"
              {...attributes}
              {...listeners}
            >
              <GripVertical className="h-5 w-5 text-muted-foreground" />
            </button>
            
            <div className="flex-1 space-y-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="text-lg font-semibold">Q{index + 1}.</span>
                  <Badge variant="outline" className={getTypeColor(question.type)}>
                    {getTypeLabel(question.type)}
                  </Badge>
                  <Badge variant="secondary">{question.marks} mark{question.marks > 1 ? 's' : ''}</Badge>
                </div>
                <div className="flex gap-2">
                  <Button 
                    size="icon" 
                    variant="ghost"
                    onClick={() => setIsEditing(!isEditing)}
                  >
                    <Edit2 className="h-4 w-4" />
                  </Button>
                  <Button 
                    size="icon" 
                    variant="ghost"
                    onClick={() => onRegenerate(question.id)}
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {isEditing ? (
                <motion.div 
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="space-y-4 p-4 border border-border rounded-lg"
                >
                  <div className="space-y-2">
                    <Label>Question Text</Label>
                    <Textarea
                      value={editData.text}
                      onChange={(e) => setEditData({ ...editData, text: e.target.value })}
                      rows={3}
                    />
                  </div>
                  {question.type === 'mcq' && (
                    <div className="space-y-2">
                      <Label>Options (one per line)</Label>
                      <Textarea
                        value={editData.options?.join('\n')}
                        onChange={(e) => setEditData({ ...editData, options: e.target.value.split('\n') })}
                        rows={4}
                      />
                    </div>
                  )}
                  <div className="space-y-2">
                    <Label>Explanation</Label>
                    <Textarea
                      value={editData.explanation}
                      onChange={(e) => setEditData({ ...editData, explanation: e.target.value })}
                      rows={3}
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleSave}>
                      <Save className="h-4 w-4 mr-2" />
                      Save
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setIsEditing(false)}>
                      <X className="h-4 w-4 mr-2" />
                      Cancel
                    </Button>
                  </div>
                </motion.div>
              ) : (
                <>
                  <p className="text-foreground leading-relaxed">{question.text}</p>

                  {question.images && question.images.length > 0 && (
                    <div
                      className="relative w-40 h-24 rounded-lg overflow-hidden border border-border cursor-pointer hover:ring-2 hover:ring-primary transition-all"
                      onClick={() => setImageOpen(true)}
                    >
                      <img
                        src={question.images[0]}
                        alt="Question diagram"
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                        <ImageIcon className="h-6 w-6 text-white" />
                      </div>
                    </div>
                  )}

                  {(question.options && question.options.length > 0) && (
                    <div className="space-y-2 pl-4">
                      {question.options.map((option, i) => (
                        <div key={i} className="flex items-start gap-2">
                          <span className="text-muted-foreground min-w-[20px]">{String.fromCharCode(65 + i)}.</span>
                          <span>{option}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  <Collapsible open={isOpen} onOpenChange={setIsOpen}>
                    <CollapsibleTrigger asChild>
                      <Button variant="ghost" size="sm" className="gap-2 text-primary">
                        <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                        {isOpen ? 'Hide' : 'Show'} Answer & Explanation
                      </Button>
                    </CollapsibleTrigger>
                    <AnimatePresence>
                      {isOpen && (
                        <CollapsibleContent forceMount>
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="mt-4 p-4 bg-muted/30 rounded-lg space-y-3"
                          >
                            {question.correct_answer !== undefined && (
                              <div>
                                <span className="font-semibold text-primary">Correct Answer: </span>
                                {Array.isArray(question.correct_answer) ? (
                                  <span>{question.correct_answer.map(i => String.fromCharCode(65 + i)).join(', ')}</span>
                                ) : typeof question.correct_answer === 'number' ? (
                                  <span>{question.options?.[question.correct_answer]}</span>
                                ) : (
                                  <span>{question.correct_answer}</span>
                                )}
                              </div>
                            )}
                            <div>
                              <span className="font-semibold">Explanation: </span>
                              <span className="text-muted-foreground">{question.explanation}</span>
                            </div>
                          </motion.div>
                        </CollapsibleContent>
                      )}
                    </AnimatePresence>
                  </Collapsible>
                </>
              )}
            </div>
          </div>
        </Card>
      </motion.div>

      <Dialog open={imageOpen} onOpenChange={setImageOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Question Diagram</DialogTitle>
          </DialogHeader>
          {question.images && (
            <img 
              src={question.images[0]} 
              alt="Question diagram full size"
              className="w-full rounded-lg"
            />
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
