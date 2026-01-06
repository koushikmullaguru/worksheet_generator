import { useState, useEffect } from "react";
import { Header } from "../components/Header";
import { ResultsPanel } from "../components/ResultsPanel";
import { useToast } from "../hooks/use-toast";
import * as api from "../lib/api";
import type { ExamGenerationRequest } from "../lib/api";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Badge } from "../components/ui/badge";
import { X } from "lucide-react";
import { boards, type Chapter, type Topic, type Subject } from "../lib/mockData";

const ExamCreation = () => {
  const [questions, setQuestions] = useState<api.Question[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentTopics, setCurrentTopics] = useState<string[]>([]);
  const [currentTopicIds, setCurrentTopicIds] = useState<string[]>([]);
  const [selectedTopicId, setSelectedTopicId] = useState<string>('');
  const [selectedTopicName, setSelectedTopicName] = useState<string>('');
  const [topicsList, setTopicsList] = useState<{id: string, name: string}[]>([]);
  const [selectedChapter, setSelectedChapter] = useState<string>('');
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [grades, setGrades] = useState<api.Grade[]>([]);
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [selectedBoard, setSelectedBoard] = useState<string>('CBSE');
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('hard');
  const [mcqCount, setMcqCount] = useState<number>(10);
  const [shortAnswerCount, setShortAnswerCount] = useState<number>(5);
  const [longAnswerCount, setLongAnswerCount] = useState<number>(3);
  const [useBloomsTaxonomy, setUseBloomsTaxonomy] = useState<boolean>(false);
  const [bloomsTaxonomyLevel, setBloomsTaxonomyLevel] = useState<'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create'>('apply');
  const { toast } = useToast();

  useEffect(() => {
    document.documentElement.classList.add('dark');
    fetchGrades();
  }, []);

  useEffect(() => {
    if (selectedGrade) {
      fetchSubjectsByGrade(selectedGrade);
    }
  }, [selectedGrade]);

  const fetchGrades = async () => {
    try {
      const gradesData = await api.getGrades();
      setGrades(gradesData);
    } catch (error) {
      console.error('Failed to fetch grades:', error);
    }
  };

  const fetchSubjectsByGrade = async (gradeId: string) => {
    try {
      const subjectsData = await api.getSubjectsByGrade(gradeId);
      setSubjects(subjectsData as Subject[]);
      setSelectedSubject('');
      setChapters([]);
      setTopicsList([]);
    } catch (error) {
      console.error('Failed to fetch subjects by grade:', error);
      toast({
        title: "Error",
        description: "Failed to load subjects for selected grade",
        variant: "destructive",
      });
    }
  };

  const handleAddTopic = () => {
    if (selectedTopicId && selectedTopicName && !currentTopicIds.includes(selectedTopicId)) {
      setCurrentTopics([...currentTopics, selectedTopicName]);
      setCurrentTopicIds([...currentTopicIds, selectedTopicId]);
      setSelectedTopicId('');
      setSelectedTopicName('');
    }
  };

  const handleRemoveTopic = (topicId: string) => {
    setCurrentTopics(currentTopics.filter((_, index) => currentTopicIds[index] !== topicId));
    setCurrentTopicIds(currentTopicIds.filter(id => id !== topicId));
  };

  const handleGenerate = async () => {
    if (currentTopicIds.length === 0) {
      toast({
        title: "Error",
        description: "Please select at least one topic for the exam",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);
    toast({
      title: "Generating exam",
      description: "Creating questions based on your filters...",
    });

    try {
      // Get the subject name
      let subjectName = '';
      if (selectedSubject) {
        const selectedSubjectObj = subjects.find(s => s.id === selectedSubject);
        if (selectedSubjectObj) {
          subjectName = selectedSubjectObj.name;
        }
      }
      
      // Generate exam from backend API
      const includeImages = false; // We're not including images for now
      
      // Prepare the request parameters based on which option is selected
      const examRequest: ExamGenerationRequest = {
        topic_ids: currentTopicIds,
        mcq_count: mcqCount,
        short_answer_count: shortAnswerCount,
        long_answer_count: longAnswerCount,
        subject_name: subjectName,
        include_images: includeImages,
      };

      // Add either difficulty OR Bloom's taxonomy, but not both
      if (difficulty) {
        examRequest.difficulty = difficulty;
      } else if (useBloomsTaxonomy && bloomsTaxonomyLevel) {
        examRequest.use_blooms_taxonomy = true;
        examRequest.blooms_taxonomy_level = bloomsTaxonomyLevel;
      }

      const generatedQuestions = await api.generateExam(
        examRequest,
        '' // This is the token argument
      );

      setQuestions(generatedQuestions);
      setIsGenerating(false);
      
      // Debug: Log the generated questions
      console.log("Generated exam questions:", generatedQuestions);
      
      toast({
        title: "Exam generated",
        description: `${generatedQuestions.length} questions created successfully`,
      });
    } catch (error) {
      console.error('Error generating exam:', error);
      setIsGenerating(false);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to generate exam',
        variant: "destructive",
      });
    }
  };

  const fetchChaptersAndTopics = async (subjectId: string) => {
    try {
      const chaptersData = await api.getChapters(subjectId);
      setChapters(chaptersData as Chapter[]);
      setSelectedChapter('');
      setTopicsList([]);
    } catch (error) {
      console.error('Failed to fetch chapters:', error);
      toast({
        title: "Error",
        description: "Failed to load chapters for selected subject",
        variant: "destructive",
      });
    }
  };

  const fetchTopicsForChapter = async (chapterId: string) => {
    try {
      const topicsData = await api.getTopics(chapterId);
      setTopicsList(topicsData);
    } catch (error) {
      console.error('Failed to fetch topics:', error);
      toast({
        title: "Error",
        description: "Failed to load topics for selected chapter",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      
      <div className="flex-1 flex flex-col lg:flex-row">
        <aside className="w-full lg:w-80 xl:w-96 flex-shrink-0">
          <div className="space-y-6 p-6 border-b border-border lg:border-b-0 lg:border-r">
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Exam Configuration</h2>
              <p className="text-sm text-muted-foreground">
                Configure your exam by selecting board, grade, and topics.
              </p>
              
              <div className="space-y-2">
                <Label htmlFor="board">Board</Label>
                <Select value={selectedBoard} onValueChange={setSelectedBoard}>
                  <SelectTrigger id="board">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {boards.map(board => (
                      <SelectItem key={board} value={board}>{board}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="grade">Grade</Label>
                <Select value={selectedGrade} onValueChange={setSelectedGrade}>
                  <SelectTrigger id="grade">
                    <SelectValue placeholder="Select grade" />
                  </SelectTrigger>
                  <SelectContent>
                    {grades.map(grade => (
                      <SelectItem key={grade.id} value={grade.id}>{grade.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              {subjects.length > 0 && (
                <div className="space-y-2">
                  <Label htmlFor="subject">Subject</Label>
                  <Select value={selectedSubject} onValueChange={(value) => {
                    setSelectedSubject(value);
                    fetchChaptersAndTopics(value);
                  }}>
                    <SelectTrigger id="subject">
                      <SelectValue placeholder="Select subject to load chapters" />
                    </SelectTrigger>
                    <SelectContent>
                      {subjects.map(subject => (
                        <SelectItem key={subject.id} value={subject.id}>{subject.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {chapters.length > 0 && (
                <div className="space-y-2">
                  <Label htmlFor="chapter">Chapter</Label>
                  <Select value={selectedChapter} onValueChange={(value) => {
                    setSelectedChapter(value);
                    fetchTopicsForChapter(value);
                  }}>
                    <SelectTrigger id="chapter">
                      <SelectValue placeholder="Select chapter to load topics" />
                    </SelectTrigger>
                    <SelectContent>
                      {chapters.map(chapter => (
                        <SelectItem key={chapter.id} value={chapter.id}>{chapter.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {topicsList.length > 0 && (
                <div className="space-y-2">
                  <Label htmlFor="topic">Topic</Label>
                  <div className="flex gap-2">
                    <Select
                      value={selectedTopicId}
                      onValueChange={(value) => {
                        const topic = topicsList.find(t => t.id === value);
                        if (topic) {
                          setSelectedTopicId(topic.id);
                          setSelectedTopicName(topic.name);
                        }
                      }}
                    >
                      <SelectTrigger id="topic" className="flex-1">
                        <SelectValue placeholder="Select topic" />
                      </SelectTrigger>
                      <SelectContent>
                        {topicsList.map(topic => (
                          <SelectItem key={topic.id} value={topic.id}>{topic.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button
                      onClick={handleAddTopic}
                      disabled={!selectedTopicId}
                      size="sm"
                    >
                      Add
                    </Button>
                  </div>
                </div>
              )}

              {currentTopics.length > 0 && (
                <div className="space-y-2">
                  <Label>Selected Topics</Label>
                  <div className="flex flex-wrap gap-2">
                    {currentTopics.map((topic, index) => (
                      <Badge key={currentTopicIds[index]} variant="secondary" className="flex items-center gap-1">
                        {topic}
                        <button
                          onClick={() => handleRemoveTopic(currentTopicIds[index])}
                          className="ml-1 rounded-full hover:bg-muted"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="border-t border-border pt-6 mt-6 space-y-4">
              <h3 className="text-lg font-semibold">Question Settings</h3>
              
              <div className="space-y-2">
                <Label htmlFor="difficulty">Difficulty Level</Label>
                <Select value={difficulty} onValueChange={(value) => setDifficulty(value as 'easy' | 'medium' | 'hard')}>
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

              <Button
                onClick={handleGenerate}
                className="w-full"
                disabled={currentTopicIds.length === 0 || isGenerating}
              >
                {isGenerating ? "Generating..." : "Generate Exam"}
              </Button>
            </div>
          </div>
        </aside>
        
        <main className="flex-1 overflow-auto scrollbar-thin">
          <ResultsPanel
            questions={questions}
            topic={currentTopics.join(", ")}
            topicId={currentTopicIds.join(",")}
            onQuestionsChange={setQuestions}
            isLoading={isGenerating}
            contentType="exam"
          />
        </main>
      </div>
    </div>
  );
};

export default ExamCreation;