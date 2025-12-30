import { useState } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { ThumbsUp, ThumbsDown, Send } from "lucide-react";
import { useToast } from "../hooks/use-toast";
import * as api from "../lib/api";

interface QuizFeedbackProps {
  worksheetId: string;
  token: string;
  onFeedbackSubmitted?: () => void;
}

export function QuizFeedback({ worksheetId, token, onFeedbackSubmitted }: QuizFeedbackProps) {
  const [feedbackType, setFeedbackType] = useState<"thumbs_up" | "thumbs_down" | null>(null);
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async () => {
    if (!feedbackType) {
      toast({
        title: "Please select feedback type",
        description: "Click thumbs up or thumbs down to provide feedback",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await api.submitQuizFeedback(
        {
          worksheet_id: worksheetId,
          feedback_type: feedbackType,
          comment: comment.trim() || undefined,
        },
        token
      );
      
      toast({
        title: "Feedback submitted",
        description: "Thank you for your feedback!",
      });
      
      // Reset form
      setFeedbackType(null);
      setComment("");
      
      // Notify parent component
      if (onFeedbackSubmitted) {
        onFeedbackSubmitted();
      }
    } catch (error) {
      console.error("Error submitting feedback:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to submit feedback",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="p-4">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">How was this quiz?</h3>
        <p className="text-sm text-muted-foreground">
          Your feedback helps us improve our quiz generation
        </p>
        
        <div className="flex gap-4">
          <Button
            variant={feedbackType === "thumbs_up" ? "default" : "outline"}
            onClick={() => setFeedbackType(feedbackType === "thumbs_up" ? null : "thumbs_up")}
            className="flex items-center gap-2"
          >
            <ThumbsUp className="h-4 w-4" />
            <span>Good</span>
          </Button>
          
          <Button
            variant={feedbackType === "thumbs_down" ? "default" : "outline"}
            onClick={() => setFeedbackType(feedbackType === "thumbs_down" ? null : "thumbs_down")}
            className="flex items-center gap-2"
          >
            <ThumbsDown className="h-4 w-4" />
            <span>Needs Improvement</span>
          </Button>
        </div>
        
        <Textarea
          placeholder="Leave a comment (optional)"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          className="min-h-[80px]"
        />
        
        <div className="flex justify-end">
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || !feedbackType}
            className="flex items-center gap-2"
          >
            <Send className="h-4 w-4" />
            <span>{isSubmitting ? "Submitting..." : "Submit Feedback"}</span>
          </Button>
        </div>
      </div>
    </Card>
  );
}