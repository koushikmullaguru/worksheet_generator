import { useState, useEffect } from "react";
import { Header } from "../components/Header";
import { QuizFilterPanel, QuizFilters } from "../components/QuizFilterPanel";
import { ResultsPanel } from "../components/ResultsPanel";
import { QuizResults } from "../components/QuizResultsFixed";
import { useToast } from "../hooks/use-toast";
import * as api from "../lib/api";
import type { QuizGenerationRequest } from "../lib/api";

const QuizCreation = () => {
  const [questions, setQuestions] = useState<api.Question[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentTopic, setCurrentTopic] = useState<string>('');
  const [currentTopicId, setCurrentTopicId] = useState<string>('');
  const [showQuizResults, setShowQuizResults] = useState(false);
  const [worksheetId, setWorksheetId] = useState<string>('');
  const { toast } = useToast();

  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const handleGenerate = async (filters: QuizFilters) => {
    setIsGenerating(true);
    toast({
      title: "Generating quiz",
      description: "Creating questions based on your filters...",
    });

    try {
      // Get the topic name from the API
      const topicsData = await api.getTopics(filters.chapter);
      const selectedTopic = topicsData.find(t => t.id === filters.topic);
      setCurrentTopic(selectedTopic?.name || 'Generated Quiz');
      setCurrentTopicId(filters.topic);

      // Generate quiz from backend API
      const mcqCount = filters.mcqCount || 5; // Default to 5 MCQs for quizzes
      const shortAnswerCount = filters.shortAnswerCount || 0; // Use short answer count from filters
      const longAnswerCount = filters.longAnswerCount || 0; // Use long answer count from filters
      const difficulty = filters.difficulty || 'easy'; // Default to easy difficulty for quizzes
      
      // Determine if we should include images based on the question type and user preferences
      const includeImages = filters.includeImagesForMCQ && mcqCount > 0;

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
      
      // Prepare the request parameters based on which option is selected
      const quizRequest: QuizGenerationRequest = {
        topic_id: filters.topic,
        mcq_count: mcqCount,
        short_answer_count: shortAnswerCount,
        long_answer_count: longAnswerCount,
        subject_name: subjectName,
        include_images: includeImages,
        generate_real_images: filters.generateRealImages || false,
      };

      // Add either difficulty OR Bloom's taxonomy, but not both
      if (filters.difficulty) {
        quizRequest.difficulty = filters.difficulty;
      } else if (filters.useBloomsTaxonomy && filters.bloomsTaxonomyLevel) {
        quizRequest.use_blooms_taxonomy = true;
        quizRequest.blooms_taxonomy_level = filters.bloomsTaxonomyLevel;
      }

      const generatedQuestions = await api.generateQuiz(
        quizRequest,
        '' // This is the token argument
      );

      setQuestions(generatedQuestions);
      setIsGenerating(false);
      
      // Debug: Log the generated questions
      console.log("Generated quiz questions:", generatedQuestions);
      
      toast({
        title: "Quiz generated",
        description: `${generatedQuestions.length} questions created successfully`,
      });
    } catch (error) {
      console.error('Error generating quiz:', error);
      setIsGenerating(false);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to generate quiz',
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      
      <div className="flex-1 flex flex-col lg:flex-row">
        <aside className="w-full lg:w-80 xl:w-96 flex-shrink-0">
          <QuizFilterPanel onGenerate={handleGenerate} />
        </aside>
        
        <main className="flex-1 overflow-auto scrollbar-thin">
          <ResultsPanel
            questions={questions}
            topic={currentTopic}
            topicId={currentTopicId}
            onQuestionsChange={setQuestions}
            isLoading={isGenerating}
            contentType="quiz"
            quizMode={true}
            onSubmitQuiz={async (topicId, answers) => {
              try {
                // First, create a worksheet with the questions
                const worksheetName = `${currentTopic} - Quiz`;
                const questionIds = questions.map(q => q.id);
                const worksheet = await api.saveWorksheet(worksheetName, topicId, questionIds, '');
                
                // Now submit the quiz answers with the worksheet ID
                const submission: api.QuizSubmission = {
                  worksheet_id: worksheet.id,
                  answers: answers
                };
                await api.submitQuizAnswers(submission, '');
                setWorksheetId(worksheet.id);
                setShowQuizResults(true);
                toast({
                  title: "Quiz submitted",
                  description: "Your answers have been recorded",
                });
              } catch (error) {
                console.error('Error submitting quiz:', error);
                toast({
                  title: "Error",
                  description: error instanceof Error ? error.message : 'Failed to submit quiz',
                  variant: "destructive",
                });
              }
            }}
          />
        </main>
      </div>
      
      <QuizResults
        isOpen={showQuizResults}
        onClose={() => setShowQuizResults(false)}
        worksheetId={worksheetId}
      />
    </div>
  );
};

export default QuizCreation;