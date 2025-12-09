import katex from "katex";
import "katex/dist/katex.min.css";

/**
 * Renders mathematical equations in LaTeX format using KaTeX
 * @param text - The text that may contain LaTeX equations
 * @returns
 */
export function renderEquations(text: string): string {
  if (!text) return '';
  
  // Regular expression to find LaTeX equations between $$ delimiters
  const equationRegex = /\$\$(.*?)\$\$/g;
  
  return text.replace(equationRegex, (match, equation) => {
    try {
      // Render the equation using KaTeX
      const renderedHtml = katex.renderToString(equation.trim(), {
        throwOnError: false,
        displayMode: true,
        output: 'html'
      });
      return renderedHtml;
    } catch (error) {
      console.error('Error rendering equation:', error);
      return match; // Return original equation if rendering fails
    }
  });
}

/**
 * Renders inline mathematical equations in LaTeX format using KaTeX
 * @param text - The text that may contain inline LaTeX equations
 * @returns HTML string with rendered equations
 */
export function renderInlineEquations(text: string): string {
  if (!text) return '';
  
  // Regular expression to find inline LaTeX equations between $ delimiters
  const inlineEquationRegex = /\$(.*?)\$/g;
  
  return text.replace(inlineEquationRegex, (match, equation) => {
    try {
      // Render the equation using KaTeX
      const renderedHtml = katex.renderToString(equation.trim(), {
        throwOnError: false,
        displayMode: false,
        output: 'html'
      });
      return renderedHtml;
    } catch (error) {
      console.error('Error rendering inline equation:', error);
      return match; // Return original equation if rendering fails
    }
  });
}

/**
 * Renders both inline and display mathematical equations
 * @param text - The text that may contain LaTeX equations
 * @returns HTML string with rendered equations
 */
export function renderAllEquations(text: string): string {
  if (!text) return '';
  
  // First render display equations
  let processedText = renderEquations(text);
  
  // Then render inline equations
  processedText = renderInlineEquations(processedText);
  
  return processedText;
}