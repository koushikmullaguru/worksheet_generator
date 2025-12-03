import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Tabs, TabsList, TabsTrigger } from "./ui/tabs";
import { Checkbox } from "./ui/checkbox";
import { Sparkles, X } from "lucide-react";
import { motion } from "framer-motion";
import { boards, grades, questionTypes, type Chapter, type Topic, type Subject } from "../lib/mockData";
import * as api from "../lib/api";

interface FilterPanelProps {
  onGenerate: (filters: WorksheetFilters) => void;
}

export interface WorksheetFilters {
  board: string;
  grade: string;
  subject: string;
  assessmentType: 'chapter' | 'subtopic';
  chapter: string;
  topic: string;
  questionCount: number;
  questionTypes: string[];
  difficulty?: 'easy' | 'medium' | 'hard';
  mcqCount?: number;
  shortAnswerCount?: number;
  longAnswerCount?: number;
}

export function FilterPanel({ onGenerate }: FilterPanelProps) {
  const [board, setBoard] = useState('CBSE');
  const [grade, setGrade] = useState('');
  const [subject, setSubject] = useState('');
  const [assessmentType, setAssessmentType] = useState<'chapter' | 'subtopic'>('chapter');
  const [chapter, setChapter] = useState('');
  const [topic, setTopic] = useState('');
  const [questionCount, setQuestionCount] = useState(5);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);

  // API data state
  const [grades, setGrades] = useState<api.Grade[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(false);
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [mcqCount, setMcqCount] = useState(0);
  const [shortAnswerCount, setShortAnswerCount] = useState(0);
  const [longAnswerCount, setLongAnswerCount] = useState(0);

  // Fetch grades on mount
  useEffect(() => {
    fetchGrades();
  }, []);

  // Fetch subjects when grade changes
  useEffect(() => {
    if (grade) {
      fetchSubjects(grade);
    }
  }, [grade]);

  // Fetch chapters when subject changes
  useEffect(() => {
    if (subject) {
      fetchChapters(subject);
    }
  }, [subject]);

  // Fetch topics when chapter changes
  useEffect(() => {
    if (chapter) {
      fetchTopics(chapter);
    }
  }, [chapter]);

  const fetchGrades = async () => {
    try {
      setLoading(true);
      const gradesData = await api.getGrades();
      setGrades(gradesData);
      // Auto-select first grade
      if (gradesData.length > 0 && !grade) {
        setGrade(gradesData[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch grades:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubjects = async (gradeId: string) => {
    try {
      setLoading(true);
      const subjectsData = await api.getSubjectsByGrade(gradeId);
      setSubjects(subjectsData as Subject[]);
      setSubject('');
      setChapters([]);
      setTopics([]);
    } catch (error) {
      console.error('Failed to fetch subjects:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchChapters = async (subjectId: string) => {
    try {
      setLoading(true);
      const chaptersData = await api.getChapters(subjectId);
      setChapters(chaptersData as Chapter[]);
      setChapter('');
      setTopics([]);
    } catch (error) {
      console.error('Failed to fetch chapters:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTopics = async (chapterId: string) => {
    try {
      setLoading(true);
      const topicsData = await api.getTopics(chapterId);
      setTopics(topicsData);
      setTopic('');
    } catch (error) {
      console.error('Failed to fetch topics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = () => {
    if (!topic) {
      alert('Please select a topic');
      return;
    }

    // Calculate question count
    const totalQuestions = mcqCount + shortAnswerCount + longAnswerCount || questionCount;

    onGenerate({
      board,
      grade,
      subject,
      assessmentType,
      chapter,
      topic,
      questionCount: totalQuestions,
      questionTypes: selectedTypes,
      difficulty,
      mcqCount,
      shortAnswerCount,
      longAnswerCount,
    });
  };

  const handleClear = () => {
    setChapter('');
    setTopic('');
    setQuestionCount(5);
    setSelectedTypes([]);
    setMcqCount(0);
    setShortAnswerCount(0);
    setLongAnswerCount(0);
    setDifficulty('medium');
  };

  const toggleQuestionType = (type: string) => {
    setSelectedTypes(prev => 
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  return (
    <motion.div 
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ delay: 0.1 }}
      className="space-y-6 p-6 border-b border-border lg:border-b-0 lg:border-r"
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4">
        <div className="space-y-2">
          <Label htmlFor="board">Board</Label>
          <Select value={board} onValueChange={setBoard}>
            <SelectTrigger id="board">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {boards.map(b => (
                <SelectItem key={b} value={b}>{b}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="grade">Grade</Label>
          <Select value={grade} onValueChange={setGrade} disabled={loading || grades.length === 0}>
            <SelectTrigger id="grade">
              <SelectValue placeholder="Select grade" />
            </SelectTrigger>
            <SelectContent>
              {grades.map(g => (
                <SelectItem key={g.id} value={g.id}>{g.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2 sm:col-span-2 lg:col-span-1">
          <Label htmlFor="subject">Subject</Label>
          <Select value={subject} onValueChange={setSubject} disabled={loading || subjects.length === 0}>
            <SelectTrigger id="subject">
              <SelectValue placeholder="Select subject" />
            </SelectTrigger>
            <SelectContent>
              {subjects.map(s => (
                <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2 sm:col-span-2 lg:col-span-1">
          <Label>Assessment Type</Label>
          <Tabs value={assessmentType} onValueChange={(v) => setAssessmentType(v as 'chapter' | 'subtopic')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="chapter">Chapter</TabsTrigger>
              <TabsTrigger value="subtopic">Subtopic</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <div className="space-y-2 sm:col-span-2 lg:col-span-1">
          <Label htmlFor="chapter">Chapter</Label>
          <Select value={chapter} onValueChange={setChapter} disabled={loading || chapters.length === 0}>
            <SelectTrigger id="chapter">
              <SelectValue placeholder="Select chapter" />
            </SelectTrigger>
            <SelectContent>
              {chapters.map(c => (
                <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {chapter && topics.length > 0 && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="space-y-2 sm:col-span-2 lg:col-span-1"
          >
            <Label htmlFor="topic">Topic</Label>
            <Select value={topic} onValueChange={setTopic}>
              <SelectTrigger id="topic">
                <SelectValue placeholder="Select topic" />
              </SelectTrigger>
              <SelectContent>
                {topics.map(t => (
                  <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </motion.div>
        )}

        <div className="space-y-2">
          <Label htmlFor="difficulty">Difficulty Level</Label>
          <Select value={difficulty} onValueChange={(v) => setDifficulty(v as 'easy' | 'medium' | 'hard')}>
            <SelectTrigger id="difficulty">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="easy">Easy</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="hard">Hard</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="mcq-count">MCQ Count</Label>
          <Input
            id="mcq-count"
            type="number"
            min={0}
            max={50}
            value={mcqCount}
            onChange={(e) => setMcqCount(parseInt(e.target.value) || 0)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="short-count">Short Answer Count</Label>
          <Input
            id="short-count"
            type="number"
            min={0}
            max={50}
            value={shortAnswerCount}
            onChange={(e) => setShortAnswerCount(parseInt(e.target.value) || 0)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="long-count">Long Answer Count</Label>
          <Input
            id="long-count"
            type="number"
            min={0}
            max={50}
            value={longAnswerCount}
            onChange={(e) => setLongAnswerCount(parseInt(e.target.value) || 0)}
          />
        </div>

        <div className="space-y-2 sm:col-span-2 lg:col-span-1">
          <Label>Question Types</Label>
          <div className="space-y-2">
            {questionTypes.map(type => (
              <div key={type} className="flex items-center space-x-2">
                <Checkbox 
                  id={type}
                  checked={selectedTypes.includes(type)}
                  onCheckedChange={() => toggleQuestionType(type)}
                />
                <label htmlFor={type} className="text-sm cursor-pointer">{type}</label>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex gap-3">
        <Button 
          onClick={handleGenerate} 
          className="flex-1 gap-2"
          disabled={!topic || loading}
        >
          <Sparkles className="h-4 w-4" />
          Generate
        </Button>
        <Button onClick={handleClear} variant="outline" size="icon">
          <X className="h-4 w-4" />
        </Button>
      </div>

      <p className="text-xs text-muted-foreground">
        Press <kbd className="px-1.5 py-0.5 bg-muted rounded">Enter</kbd> to generate
      </p>
    </motion.div>
  );
}
