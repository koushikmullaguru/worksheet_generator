import * as api from './api';
import { renderAllEquations } from './equationUtils';

// Declare html2pdf on the window object
declare global {
    interface Window {
        html2pdf: {
            (): {
                set: (options: object) => {
                    from: (element: HTMLElement) => {
                        save: () => Promise<void>;
                    };
                };
            };
        };
    }
}

export interface ExportOptions {
    includeAnswers: boolean;
    format: 'pdf' | 'txt';
    filename?: string;
}

// --- CORE HTML GENERATION FUNCTION ---

export function generateWorksheetHTML(
    topic: string,
    questions: api.Question[],
    includeAnswers: boolean = false
): string {
    const totalMarks = questions.reduce((sum, q) => sum + q.marks, 0);
    const date = new Date().toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    const questionsHTML = questions.map((q, index) => {
        // Process LaTeX equations in question text
        const processedQuestionText = renderAllEquations(q.text);
        
        let questionHTML = `
            <div class="question-item">
                <p class="question-text">
                    Q${index + 1}. ${processedQuestionText}
                    <span class="marks-float">
                        (${q.marks} mark${q.marks > 1 ? 's' : ''})
                    </span>
                </p>
        `;

        // --- NEW LOGIC: RENDER EMBEDDED BASE64 IMAGE FOR EXPORT ---
        if (q.images && q.images.length > 0) {
            // The image is a Base64 Data URI, which is embedded directly.
            // This is crucial for offline rendering and PDF export (html2pdf.js).
            questionHTML += `
                <div class="question-image" style="margin-bottom: 15px; text-align: center; page-break-inside: avoid;">
                    <img src="${q.images[0]}" alt="Question Diagram" style="max-width: 100%; height: auto; border: 1px solid #ddd; padding: 5px;"/>
                </div>
            `;
        }
        // --- END NEW LOGIC ---

        // Add options for MCQ
        if (q.type === 'mcq' && q.options) {
            questionHTML += `<div class="mcq-options">`;
            q.options.forEach((option, i) => {
                // Process LaTeX equations in options
                const processedOption = renderAllEquations(option);
                questionHTML += `<p><strong>${String.fromCharCode(65 + i)}.</strong> ${processedOption}</p>`;
            });
            questionHTML += `</div>`;
        }

        // Add answer section
        if (includeAnswers) {
            // Process LaTeX equations in correct answer
            let processedAnswer = '';
            if (q.type === 'mcq' && typeof q.correct_answer === 'number') {
                const answerIndex = q.correct_answer;
                processedAnswer = String.fromCharCode(65 + answerIndex);
            } else if (q.type === 'mcq' && Array.isArray(q.correct_answer)) {
                processedAnswer = q.correct_answer.map(i => String.fromCharCode(65 + i)).join(', ');
            } else {
                processedAnswer = String(q.correct_answer) || 'N/A';
            }
            
            // Process LaTeX equations in explanation
            const processedExplanation = renderAllEquations(q.explanation || '');
            
            questionHTML += `
                <div class="answer-box">
                    <p><strong class="answer-label">Answer:</strong> ${renderAllEquations(processedAnswer)}</p>
                    <p><strong class="explanation-label">Explanation:</strong> ${processedExplanation}</p>
                </div>`;
        }

        // Add space for short/long answer questions
        if (q.type === 'short' || q.type === 'long') {
            const lines = q.type === 'short' ? 5 : 8;
            questionHTML += `<div class="answer-space" style="height: ${lines * 18}px;"></div>`;
        }

        questionHTML += `</div>`;
        return questionHTML;
    }).join('');

    const html = `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>${topic || 'Worksheet'}</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
            <style>
                /* Base Styles */
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.5;
                    color: #333;
                    background: white;
                }
                .container {
                    max-width: 750px;
                    margin: 0 auto;
                    padding: 30px 20px;
                }
                
                /* Header */
                .header {
                    text-align: center;
                    margin-bottom: 25px;
                    border-bottom: 2px solid #333;
                    padding-bottom: 15px;
                }
                .header h1 { font-size: 22px; margin-bottom: 8px; color: #2c3e50; }
                .meta-info {
                    display: flex;
                    justify-content: space-between;
                    font-size: 13px;
                    color: #7f8c8d;
                    margin-top: 5px;
                }
                
                /* Question Styling */
                .question-item {
                    margin-bottom: 25px;
                    padding-bottom: 5px;
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                .question-text {
                    margin: 0 0 10px 0;
                    font-weight: bold;
                    font-size: 15px;
                    display: block;
                    width: 100%;
                }
                .marks-float {
                    float: right;
                    font-size: 13px;
                    font-weight: normal;
                    display: inline-block;
                }
                .mcq-options { margin-left: 20px; margin-bottom: 10px; font-weight: normal; font-size: 14px; }
                .mcq-options p { margin: 5px 0; }
                
                /* Answer Space for short/long answers */
                .answer-space {
                    margin-top: 10px;
                    border-bottom: 1px dotted #999;
                    display: block;
                }

                /* Answer/Explanation Box */
                .answer-box {
                    margin-top: 10px;
                    padding: 8px 10px;
                    background-color: #f7f7f7;
                    border-left: 4px solid #4CAF50;
                    font-size: 14px;
                    page-break-inside: avoid;
                }
                .answer-box p { margin: 5px 0; }
                .answer-label { color: #4CAF50; font-weight: bold; }
                .explanation-label { color: #2196F3; font-weight: bold; }

                /* Print/PDF Specific Styles */
                @page {
                    size: A4;
                    margin: 10mm;
                }
                
                /* KaTeX specific styles for PDF export */
                .katex {
                    font-family: KaTeX_Main, Times New Roman, serif;
                    font-size: 1.1em;
                }
                .katex-display {
                    display: block;
                    margin: 0.5em 0;
                    text-align: center;
                }
                .katex-inline {
                    display: inline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>${topic || 'Worksheet'}</h1>
                    <div class="meta-info">
                        <span>Questions: ${questions.length}</span>
                        <span>Total Marks: ${totalMarks}</span>
                        <span>Date: ${date}</span>
                    </div>
                </div>
                <div class="questions">
                    ${questionsHTML}
                </div>
            </div>
        </body>
        </html>
    `;

    return html;
}

// --- PDF EXPORT FUNCTION (REVISED) ---

export async function exportToPDF(
    topic: string,
    questions: api.Question[],
    includeAnswers: boolean = false,
    filename: string = 'worksheet.pdf'
) {
    const html2pdf = window.html2pdf;
    
    if (!html2pdf) {
        alert("PDF library not loaded. Please refresh the page and try again.");
        return Promise.reject(new Error("html2pdf not available"));
    }

    const htmlContent = generateWorksheetHTML(topic, questions, includeAnswers);
    const tempElement = document.createElement('div');
    tempElement.innerHTML = htmlContent;

    const pdfOptions = {
        margin: 10,
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    try {
        await html2pdf().set(pdfOptions).from(tempElement).save();
        return Promise.resolve();
    } catch (error) {
        console.error("PDF Export Error:", error);
        alert("Failed to export PDF. Check the console for details.");
        return Promise.reject(error);
    }
}


// --- OTHER EXPORT FUNCTIONS (UNMODIFIED) ---

export function exportToText(
    topic: string,
    questions: api.Question[],
    includeAnswers: boolean = false
): string {
    let text = `${topic}\n`;
    text += `${'='.repeat(topic.length)}\n\n`;
    text += `Questions: ${questions.length}\n`;
    text += `Total Marks: ${questions.reduce((sum, q) => sum + q.marks, 0)}\n`;
    text += `Date: ${new Date().toLocaleDateString()}\n\n`;
    text += `${'='.repeat(50)}\n\n`;

    questions.forEach((q, index) => {
        text += `Q${index + 1}. ${q.text} (${q.marks} mark${q.marks > 1 ? 's' : ''})\n`;

        if (q.type === 'mcq' && q.options) {
            q.options.forEach((option, i) => {
                text += `${String.fromCharCode(65 + i)}. ${option}\n`;
            });
        }

        if (includeAnswers) {
            text += `\nAnswer: `;
            if (q.type === 'mcq' && typeof q.correct_answer === 'number') {
                text += String.fromCharCode(65 + q.correct_answer);
            } else if (q.type === 'mcq' && Array.isArray(q.correct_answer)) {
                text += q.correct_answer.map(i => String.fromCharCode(65 + i)).join(', ');
            } else {
                text += q.correct_answer || 'N/A';
            }
            text += `\n\nExplanation: ${q.explanation}\n`;
        }

        text += `\n${'─'.repeat(50)}\n\n`;
    });

    return text;
}

export function downloadFile(content: string, filename: string, mimeType: string = 'text/plain') {
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}

export async function exportWorksheet(
    topic: string,
    questions: api.Question[],
    options: ExportOptions
) {
    const sanitizedTopic = topic.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    const filename = options.filename || `worksheet_${sanitizedTopic}_${Date.now()}`;

    if (options.format === 'pdf') {
        return exportToPDF(topic, questions, options.includeAnswers, `${filename}.pdf`);
    } else if (options.format === 'txt') {
        const content = exportToText(topic, questions, options.includeAnswers);
        downloadFile(content, `${filename}.txt`);
        return Promise.resolve(true);
    }

    throw new Error(`Unsupported format: ${options.format}`);
}