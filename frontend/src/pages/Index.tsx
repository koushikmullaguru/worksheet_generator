import { useState, useEffect } from "react";
import { Header } from "../components/Header";
import { FilterPanel, WorksheetFilters } from "../components/FilterPanel";
import { ResultsPanel } from "../components/ResultsPanel";
import { useToast } from "../hooks/use-toast";
import * as api from "../lib/api";

const Index = () => {
  const [questions, setQuestions] = useState<api.Question[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentTopic, setCurrentTopic] = useState<string>('');
  const [currentTopicId, setCurrentTopicId] = useState<string>('');
  const { toast } = useToast();

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const handleGenerate = async (filters: WorksheetFilters) => {
    setIsGenerating(true);
    toast({
      title: "Generating worksheet",
      description: "Creating questions based on your filters...",
    });

    try {
      // Get the topic name from the API
      const topicsData = await api.getTopics(filters.chapter);
      const selectedTopic = topicsData.find(t => t.id === filters.topic);
      setCurrentTopic(selectedTopic?.name || 'Generated Worksheet');
      setCurrentTopicId(filters.topic);

      // Generate questions from backend API
      const mcqCount = filters.mcqCount || 0;
      const shortAnswerCount = filters.shortAnswerCount || 0;
      const longAnswerCount = filters.longAnswerCount || 0;
      const difficulty = filters.difficulty || 'medium';
      
      // Determine if we should include images based on the question type and user preferences
      const includeImages = filters.includeImagesForMCQ && mcqCount > 0 ||
                           filters.includeImagesForShort && shortAnswerCount > 0 ||
                           filters.includeImagesForLong && longAnswerCount > 0;

      // Get the subject name
      let subjectName = '';
      if (selectedTopic) {
        const chaptersData = await api.getChapters(selectedTopic.chapter_id);
        const selectedChapter = chaptersData.find(c => c.id === selectedTopic.chapter_id);
        
        if (selectedChapter) {
          const subjectsData = await api.getSubjects();
          const selectedSubject = subjectsData.find(s => s.id === selectedChapter.subject_id);
          
          if (selectedSubject) {
            subjectName = selectedSubject.name;
          }
        }
      }
      
      const generatedQuestions = await api.generateWorksheet(
        filters.topic,
        mcqCount,
        shortAnswerCount,
        longAnswerCount,
        difficulty as 'easy' | 'medium' | 'hard',
        includeImages,
        subjectName,
        '' // This is the 8th and final argument (the optional 'token' string).
      );

      setQuestions(generatedQuestions);
      setIsGenerating(false);
      
      // Debug: Log the generated questions
      console.log("Generated questions:", generatedQuestions);
      
      toast({
        title: "Worksheet generated",
        description: `${generatedQuestions.length} questions created successfully`,
      });
    } catch (error) {
      console.error('Error generating worksheet:', error);
      setIsGenerating(false);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to generate worksheet',
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      
      <div className="flex-1 flex flex-col lg:flex-row">
        <aside className="w-full lg:w-80 xl:w-96 flex-shrink-0">
          <FilterPanel onGenerate={handleGenerate} />
        </aside>
        
        <main className="flex-1 overflow-auto scrollbar-thin">
          <ResultsPanel 
            questions={questions} 
            topic={currentTopic}
            topicId={currentTopicId}
            onQuestionsChange={setQuestions}
            isLoading={isGenerating}
          />
        </main>
      </div>
    </div>
  );
};

export default Index;