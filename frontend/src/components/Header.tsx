import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { Button } from "./ui/button";
import { BookOpen, Sparkles, FileText, FileCheck } from "lucide-react";
import { motion } from "framer-motion";
import { NavLink } from "./NavLink";

export function Header() {
  return (
    <motion.header 
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
    >
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <BookOpen className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold">EduWorksheets</span>
        </div>

        <nav className="hidden md:flex items-center gap-6">
          <NavLink
            to="/"
            className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors text-muted-foreground hover:text-foreground hover:bg-accent"
            activeClassName="bg-primary text-primary-foreground"
          >
            <FileText className="h-4 w-4" />
            Worksheets
          </NavLink>
          <NavLink
            to="/quiz"
            className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors text-muted-foreground hover:text-foreground hover:bg-accent"
            activeClassName="bg-primary text-primary-foreground"
          >
            <Sparkles className="h-4 w-4" />
            Quiz
          </NavLink>
          <NavLink
            to="/exam"
            className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors text-muted-foreground hover:text-foreground hover:bg-accent"
            activeClassName="bg-primary text-primary-foreground"
          >
            <FileCheck className="h-4 w-4" />
            Exam
          </NavLink>
        </nav>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex flex-col items-end">
            <span className="text-sm font-medium">Sarah Johnson</span>
            <span className="text-xs text-muted-foreground">Teacher</span>
          </div>
          <Avatar>
            <AvatarImage src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100" />
            <AvatarFallback>SJ</AvatarFallback>
          </Avatar>
        </div>
      </div>
    </motion.header>
  );
}
