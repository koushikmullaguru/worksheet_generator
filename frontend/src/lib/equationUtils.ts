import katex from "katex";
import "katex/dist/katex.min.css";

/**
 * Unescapes LaTeX expressions that might be escaped in JSON
 * @param text - The text that may contain escaped LaTeX
 * @returns Unescaped text
 */
function unescapeLatex(text: string): string {
  if (!text) return '';
  
  // Replace common escaped LaTeX patterns
  return text
    .replace(/\\\\/g, '\\')  // Replace double backslashes with single backslashes
    .replace(/\\text/g, '\\text')  // Fix escaped text commands
    .replace(/\\frac/g, '\\frac')  // Fix escaped frac commands
    .replace(/\\sqrt/g, '\\sqrt')  // Fix escaped sqrt commands
    .replace(/\\sum/g, '\\sum')    // Fix escaped sum commands
    .replace(/\\int/g, '\\int')    // Fix escaped int commands
    .replace(/\\alpha/g, '\\alpha')  // Fix escaped Greek letters
    .replace(/\\beta/g, '\\beta')
    .replace(/\\gamma/g, '\\gamma')
    .replace(/\\delta/g, '\\delta')
    .replace(/\\theta/g, '\\theta')
    .replace(/\\pi/g, '\\pi');
}

/**
 * Renders mathematical equations in LaTeX format using KaTeX
 * @param text - The text that may contain LaTeX equations
 * @returns
 */
export function renderEquations(text: string): string {
  if (!text) return '';
  
  // First unescape any escaped LaTeX
  const unescapedText = unescapeLatex(text);
  
  // Regular expression to find LaTeX equations between $$ delimiters
  const equationRegex = /\$\$(.*?)\$\$/g;
  
  return unescapedText.replace(equationRegex, (match, equation) => {
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
  
  // First unescape any escaped LaTeX
  const unescapedText = unescapeLatex(text);
  
  // Regular expression to find inline LaTeX equations between $ delimiters
  const inlineEquationRegex = /\$(.*?)\$/g;
  
  return unescapedText.replace(inlineEquationRegex, (match, equation) => {
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
  
  // First convert escaped \n to actual newlines
  let processedText = text.replace(/\\n/g, '\n');
  
  // Then convert actual newlines to HTML <br> tags
  processedText = processedText.replace(/\n/g, '<br>');
  
  // Process common LaTeX symbols that might appear outside of equation delimiters
  const latexSymbols = [
    { regex: /\\Rightarrow/g, replacement: '⇒' },
    { regex: /\\Leftarrow/g, replacement: '⇐' },
    { regex: /\\Leftrightarrow/g, replacement: '⇔' },
    { regex: /\\rightarrow/g, replacement: '→' },
    { regex: /\\leftarrow/g, replacement: '←' },
    { regex: /\\leftrightarrow/g, replacement: '↔' },
    { regex: /\\times/g, replacement: '×' },
    { regex: /\\div/g, replacement: '÷' },
    { regex: /\\pm/g, replacement: '±' },
    { regex: /\\neq/g, replacement: '≠' },
    { regex: /\\leq/g, replacement: '≤' },
    { regex: /\\geq/g, replacement: '≥' },
    { regex: /\\infty/g, replacement: '∞' },
    { regex: /\\alpha/g, replacement: 'α' },
    { regex: /\\beta/g, replacement: 'β' },
    { regex: /\\gamma/g, replacement: 'γ' },
    { regex: /\\delta/g, replacement: 'δ' },
    { regex: /\\theta/g, replacement: 'θ' },
    { regex: /\\pi/g, replacement: 'π' },
    { regex: /\\sigma/g, replacement: 'σ' },
  ];
  
  // Apply all the symbol replacements
  latexSymbols.forEach(symbol => {
    processedText = processedText.replace(symbol.regex, symbol.replacement);
  });
  
  // Then render display equations
  processedText = renderEquations(processedText);
  
  // Finally render inline equations
  processedText = renderInlineEquations(processedText);
  
  return processedText;
}