import { useState, useEffect } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { CheckCircle, XCircle, Trophy, BarChart3 } from "lucide-react";
import { motion } from "framer-motion";
import * as api from "../lib/api";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";

interface QuizResultsProps {
  isOpen: boolean;
  onClose: () => void;
  worksheetId: string;
  resultId?: string;
}

export function QuizResults({ isOpen, onClose, worksheetId, resultId }: QuizResultsProps) {
  const [quizResult, setQuizResult] = useState<api.QuizResult | null>(null);
  const [quizAnswers, setQuizAnswers] = useState<api.QuizAnswer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchQuizResults = async () => {
      if (!isOpen) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        // First, get the worksheet to verify it exists
        const worksheet = await api.getWorksheet(worksheetId, '');
        
        // Then fetch quiz results
        let result: api.QuizResult | null = null;
        if (resultId) {
          // Fetch specific result
          result = await api.getQuizResult(resultId, '');
        } else {
          // Fetch latest result for this worksheet
          const results = await api.getQuizResults(worksheetId, '');
          if (results.length > 0) {
            // Sort by completed_at to get the most recent result
            const sortedResults = results.sort((a, b) => 
              new Date(b.completed_at || '').getTime() - new Date(a.completed_at || '').getTime()
            );
            result = sortedResults[0];
          }
        }
        
        if (result) {
          setQuizResult(result);
        } else {
          setError('No quiz results found for this worksheet');
        }
        
        // Fetch answers for this quiz
        const answers = await api.getQuizAnswers(worksheetId, '');
        setQuizAnswers(answers);
      } catch (error) {
        console.error('Error fetching quiz results:', error);
        setError(error instanceof Error ? error.message : 'Failed to fetch quiz results');
      } finally {
        setIsLoading(false);
      }
    };

    fetchQuizResults();
  }, [isOpen, worksheetId, resultId]);

  const getScoreColor = (percentage: number) => {
    if (percentage >= 90) return "text-green-600";
    if (percentage >= 70) return "text-blue-600";
    if (percentage >= 50) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreMessage = (percentage: number) => {
    if (percentage >= 90) return "Outstanding!";
    if (percentage >= 70) return "Good job!";
    if (percentage >= 50) return "Keep practicing!";
    return "Needs improvement";
  };

  const getGrade = (percentage: number) => {
    if (percentage >= 90) return "A+";
    if (percentage >= 80) return "A";
    if (percentage >= 70) return "B";
    if (percentage >= 60) return "C";
    if (percentage >= 50) return "D";
    return "F";
  };

  if (isLoading) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Quiz Results</DialogTitle>
          </DialogHeader>
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  if (error || !quizResult) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Quiz Results</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col items-center justify-center py-12">
            <XCircle className="h-16 w-16 text-red-500 mb-4" />
            <h3 className="text-xl font-semibold">No quiz results found</h3>
            <p className="text-muted-foreground text-center">
              {error || "Complete a quiz to see your results here."}
            </p>
            <Button variant="outline" onClick={onClose} className="mt-4">
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Quiz Results</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Score Summary */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="flex justify-center mb-2">
              <div className={`text-6xl font-bold ${getScoreColor(quizResult.score_percentage)}`}>
                {quizResult.score_percentage}%
              </div>
            </div>
            
            <div className="flex justify-center items-center gap-2 mb-4">
              <Badge className={`text-lg px-3 py-1 ${getScoreColor(quizResult.score_percentage)}`}>
                Grade: {getGrade(quizResult.score_percentage)}
              </Badge>
              <span className="text-lg font-medium">
                {getScoreMessage(quizResult.score_percentage)}
              </span>
            </div>
            
            <Progress 
              value={quizResult.score_percentage} 
              className="w-full h-3 mb-2"
            />
            
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>0%</span>
              <span>100%</span>
            </div>
          </motion.div>
          
          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            <Card className="p-4 text-center">
              <div className="flex items-center justify-center mb-2">
                <BarChart3 className="h-8 w-8 text-blue-500" />
              </div>
              <div className="text-2xl font-bold">{quizResult.total_questions}</div>
              <div className="text-sm text-muted-foreground">Questions</div>
            </Card>
            
            <Card className="p-4 text-center">
              <div className="flex items-center justify-center mb-2">
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
              <div className="text-2xl font-bold">{quizResult.correct_answers}</div>
              <div className="text-sm text-muted-foreground">Correct</div>
            </Card>
            
            <Card className="p-4 text-center">
              <div className="flex items-center justify-center mb-2">
                <XCircle className="h-8 w-8 text-red-500" />
              </div>
              <div className="text-2xl font-bold">
                {quizResult.total_questions - quizResult.correct_answers}
              </div>
              <div className="text-sm text-muted-foreground">Incorrect</div>
            </Card>
          </div>
          
          {/* Answer Details */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Answer Details</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
              {quizAnswers.map((answer, index) => (
                <motion.div
                  key={answer.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`flex items-start gap-3 p-3 rounded-lg ${
                    answer.is_correct ? 'bg-green-50' : 'bg-red-50'
                  }`}
                >
                  <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                    answer.is_correct ? 'bg-green-500' : 'bg-red-500'
                  }`}>
                    {answer.is_correct ? (
                      <CheckCircle className="h-5 w-5 text-white" />
                    ) : (
                      <XCircle className="h-5 w-5 text-white" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">
                        Question {index + 1}
                      </span>
                      {answer.is_correct ? (
                        <Badge variant="outline" className="text-green-600 border-green-600">
                          Correct
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-red-600 border-red-600">
                          Incorrect
                        </Badge>
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {typeof answer.user_answer === 'number' ? 
                        `Selected option: ${String.fromCharCode(65 + answer.user_answer)}` :
                        typeof answer.user_answer === 'string' ?
                        `Answer: ${answer.user_answer}` :
                        `Selected options: ${answer.user_answer.map((a: number) => String.fromCharCode(65 + a)).join(', ')}`
                      }
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="flex justify-center gap-3 pt-4">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            <Button onClick={() => window.print()}>
              Print Results
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}