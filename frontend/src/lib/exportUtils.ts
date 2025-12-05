// // import * as api from './api';

// // export interface ExportOptions {
// //   includeAnswers: boolean;
// //   format: 'pdf' | 'txt';
// //   filename?: string;
// // }

// // /**
// //  * Generate HTML for worksheet
// //  */
// // export function generateWorksheetHTML(
// //   topic: string,
// //   questions: api.Question[],
// //   includeAnswers: boolean = false
// // ): string {
// //   const totalMarks = questions.reduce((sum, q) => sum + q.marks, 0);
// //   const date = new Date().toLocaleDateString('en-US', {
// //     year: 'numeric',
// //     month: 'long',
// //     day: 'numeric'
// //   });

// //   const questionsHTML = questions.map((q, index) => {
// //     let questionHTML = `
// //       <div style="margin-bottom: 30px; page-break-inside: avoid;">
// //         <p style="margin: 0 0 10px 0; font-weight: bold; font-size: 16px;">
// //           Q${index + 1}. ${q.text}
// //           <span style="float: right; font-size: 14px; font-weight: normal;">
// //             (${q.marks} mark${q.marks > 1 ? 's' : ''})
// //           </span>
// //         </p>
// //     `;

// //     // Add options for MCQ
// //     if (q.type === 'mcq' && q.options) {
// //       questionHTML += `<div style="margin-left: 20px; margin-bottom: 10px;">`;
// //       q.options.forEach((option, i) => {
// //         questionHTML += `<p style="margin: 5px 0;"><strong>${String.fromCharCode(65 + i)}.</strong> ${option}</p>`;
// //       });
// //       questionHTML += `</div>`;
// //     }

// //     // Add answer section
// //     if (includeAnswers) {
// //       questionHTML += `
// //         <div style="margin-top: 10px; padding: 10px; background-color: #f0f0f0; border-left: 3px solid #4CAF50;">
// //           <p style="margin: 0 0 5px 0;"><strong style="color: #4CAF50;">Answer:</strong> `;

// //       if (q.type === 'mcq' && typeof q.correct_answer === 'number') {
// //         const answerIndex = q.correct_answer;
// //         questionHTML += `${String.fromCharCode(65 + answerIndex)}`;
// //       } else if (q.type === 'mcq' && Array.isArray(q.correct_answer)) {
// //         questionHTML += q.correct_answer.map(i => String.fromCharCode(65 + i)).join(', ');
// //       } else {
// //         questionHTML += q.correct_answer || 'N/A';
// //       }

// //       questionHTML += `</p>`;
// //       questionHTML += `<p style="margin: 5px 0 0 0;"><strong style="color: #2196F3;">Explanation:</strong> ${q.explanation || ''}</p>`;
// //       questionHTML += `</div>`;
// //     }

// //     // Add space for short/long answer questions
// //     if (q.type === 'short' || q.type === 'long') {
// //       const lines = q.type === 'short' ? 5 : 8;
// //       questionHTML += `<div style="margin-top: 10px; border-bottom: 1px dotted #999; height: ${lines * 20}px;"></div>`;
// //     }

// //     questionHTML += `</div>`;
// //     return questionHTML;
// //   }).join('');

// //   const html = `
// //     <!DOCTYPE html>
// //     <html lang="en">
// //     <head>
// //       <meta charset="UTF-8">
// //       <meta name="viewport" content="width=device-width, initial-scale=1.0">
// //       <title>${topic || 'Worksheet'}</title>
// //       <style>
// //         * {
// //           margin: 0;
// //           padding: 0;
// //           box-sizing: border-box;
// //         }
// //         body {
// //           font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
// //           line-height: 1.6;
// //           color: #333;
// //           background: white;
// //         }
// //         .container {
// //           max-width: 800px;
// //           margin: 0 auto;
// //           padding: 40px 20px;
// //         }
// //         .header {
// //           text-align: center;
// //           margin-bottom: 30px;
// //           border-bottom: 2px solid #333;
// //           padding-bottom: 20px;
// //         }
// //         .header h1 {
// //           font-size: 24px;
// //           margin-bottom: 10px;
// //           color: #2c3e50;
// //         }
// //         .header p {
// //           font-size: 14px;
// //           color: #7f8c8d;
// //           margin: 5px 0;
// //         }
// //         .meta-info {
// //           display: flex;
// //           justify-content: space-between;
// //           font-size: 13px;
// //           color: #555;
// //           margin-top: 10px;
// //         }
// //         .questions {
// //           margin-top: 30px;
// //         }
// //         @media print {
// //           body {
// //             margin: 0;
// //             padding: 0;
// //           }
// //           .container {
// //             padding: 20px;
// //           }
// //         }
// //         @page {
// //           size: A4;
// //           margin: 1cm;
// //         }
// //       </style>
// //     </head>
// //     <body>
// //       <div class="container">
// //         <div class="header">
// //           <h1>${topic || 'Worksheet'}</h1>
// //           <div class="meta-info">
// //             <span>Questions: ${questions.length}</span>
// //             <span>Total Marks: ${totalMarks}</span>
// //             <span>Date: ${date}</span>
// //           </div>
// //         </div>
// //         <div class="questions">
// //           ${questionsHTML}
// //         </div>
// //       </div>
// //     </body>
// //     </html>
// //   `;

// //   return html;
// // }

// // /**
// //  * Export to PDF using jsPDF and html2canvas
// //  */
// // export async function exportToPDF(
// //   topic: string,
// //   questions: api.Question[],
// //   includeAnswers: boolean = false,
// //   filename: string = 'worksheet.pdf'
// // ) {
// //   // Dynamically import libraries
// //   const { jsPDF } = await import('jspdf');
// //   const html2canvas = (await import('html2canvas')).default;

// //   const { jsPDF: PDF } = await import('jspdf');
// //   const pdf = new PDF({
// //     orientation: 'portrait',
// //     unit: 'mm',
// //     format: 'a4',
// //   });

// //   const pageWidth = pdf.internal.pageSize.getWidth();
// //   const pageHeight = pdf.internal.pageSize.getHeight();
// //   const margin = 10;
// //   const contentWidth = pageWidth - 2 * margin;
// //   let currentY = margin;
// //   let pageNumber = 1;

// //   // Add header on first page
// //   const addHeader = () => {
// //     const totalMarks = questions.reduce((sum, q) => sum + q.marks, 0);
// //     const date = new Date().toLocaleDateString('en-US', {
// //       year: 'numeric',
// //       month: 'long',
// //       day: 'numeric'
// //     });

// //     // Title
// //     pdf.setFontSize(18);
// //     pdf.setFont(undefined, 'bold');
// //     const titleLines = pdf.splitTextToSize(topic || 'Worksheet', contentWidth);
// //     titleLines.forEach((line: string) => {
// //       pdf.text(line, margin, currentY);
// //       currentY += 6;
// //     });

// //     // Metadata
// //     currentY += 3;
// //     pdf.setFontSize(10);
// //     pdf.setFont(undefined, 'normal');
// //     pdf.text(`Questions: ${questions.length}`, margin, currentY);
// //     currentY += 5;
// //     pdf.text(`Total Marks: ${totalMarks}`, margin, currentY);
// //     currentY += 5;
// //     pdf.text(`Date: ${date}`, margin, currentY);
// //     currentY += 10;

// //     // Divider line
// //     pdf.setLineWidth(0.5);
// //     pdf.line(margin, currentY, pageWidth - margin, currentY);
// //     currentY += 5;
// //   };

// //   addHeader();

// //   // Add questions
// //   for (let index = 0; index < questions.length; index++) {
// //     const q = questions[index];

// //     // Check if we need a new page
// //     if (currentY > pageHeight - 20) {
// //       pdf.addPage();
// //       pageNumber++;
// //       currentY = margin;
      
// //       // Add page header
// //       pdf.setFontSize(10);
// //       pdf.setFont(undefined, 'normal');
// //       pdf.text(`${topic} - Page ${pageNumber}`, margin, currentY);
// //       currentY += 8;
// //     }

// //     // Question number and text
// //     pdf.setFontSize(11);
// //     pdf.setFont(undefined, 'bold');
// //     const questionTitle = `Q${index + 1}. ${q.text}`;
// //     const questionLines = pdf.splitTextToSize(questionTitle, contentWidth - 10);
    
// //     questionLines.forEach((line: string, lineIndex: number) => {
// //       if (lineIndex === questionLines.length - 1) {
// //         // Add marks on the last line
// //         pdf.text(line, margin + 5, currentY);
// //         pdf.setFont(undefined, 'normal');
// //         pdf.setFontSize(9);
// //         pdf.text(`(${q.marks} mark${q.marks > 1 ? 's' : ''})`, pageWidth - margin - 25, currentY);
// //         pdf.setFont(undefined, 'bold');
// //         pdf.setFontSize(11);
// //       } else {
// //         pdf.text(line, margin + 5, currentY);
// //       }
// //       currentY += 5;
      
// //       // Check page break
// //       if (currentY > pageHeight - 20) {
// //         pdf.addPage();
// //         pageNumber++;
// //         currentY = margin;
// //         pdf.setFontSize(10);
// //         pdf.setFont(undefined, 'normal');
// //         pdf.text(`${topic} - Page ${pageNumber}`, margin, currentY);
// //         currentY += 8;
// //         pdf.setFont(undefined, 'bold');
// //         pdf.setFontSize(11);
// //       }
// //     });

// //     // Add options for MCQ
// //     if (q.type === 'mcq' && q.options) {
// //       pdf.setFont(undefined, 'normal');
// //       pdf.setFontSize(10);
      
// //       q.options.forEach((option, i) => {
// //         const optionText = `${String.fromCharCode(65 + i)}. ${option}`;
// //         const optionLines = pdf.splitTextToSize(optionText, contentWidth - 15);
        
// //         optionLines.forEach((line: string) => {
// //           pdf.text(line, margin + 8, currentY);
// //           currentY += 4;
          
// //           // Check page break
// //           if (currentY > pageHeight - 20) {
// //             pdf.addPage();
// //             pageNumber++;
// //             currentY = margin;
// //             pdf.setFontSize(10);
// //             pdf.setFont(undefined, 'normal');
// //             pdf.text(`${topic} - Page ${pageNumber}`, margin, currentY);
// //             currentY += 8;
// //           }
// //         });
// //       });
// //     }

// //     // Add answer section if requested
// //     if (includeAnswers) {
// //       currentY += 3;
// //       pdf.setFont(undefined, 'bold');
// //       pdf.setFontSize(9);
// //       pdf.setTextColor(76, 175, 80); // Green
// //       pdf.text('Answer:', margin + 5, currentY);
// //       currentY += 4;

// //       pdf.setFont(undefined, 'normal');
// //       pdf.setTextColor(0);
      
// //       let answerText = '';
// //       if (q.type === 'mcq' && typeof q.correct_answer === 'number') {
// //         answerText = String.fromCharCode(65 + q.correct_answer);
// //       } else if (q.type === 'mcq' && Array.isArray(q.correct_answer)) {
// //         answerText = q.correct_answer.map(i => String.fromCharCode(65 + i)).join(', ');
// //       } else {
// //         answerText = q.correct_answer?.toString() || 'N/A';
// //       }

// //       const answerLines = pdf.splitTextToSize(answerText, contentWidth - 10);
// //       answerLines.forEach((line: string) => {
// //         pdf.text(line, margin + 8, currentY);
// //         currentY += 4;
        
// //         if (currentY > pageHeight - 20) {
// //           pdf.addPage();
// //           pageNumber++;
// //           currentY = margin;
// //           pdf.setFontSize(10);
// //           pdf.setFont(undefined, 'normal');
// //           pdf.text(`${topic} - Page ${pageNumber}`, margin, currentY);
// //           currentY += 8;
// //         }
// //       });

// //       // Explanation
// //       currentY += 2;
// //       pdf.setFont(undefined, 'bold');
// //       pdf.setFontSize(9);
// //       pdf.setTextColor(33, 150, 243); // Blue
// //       pdf.text('Explanation:', margin + 5, currentY);
// //       currentY += 4;

// //       pdf.setFont(undefined, 'normal');
// //       pdf.setTextColor(0);
// //       const explanationLines = pdf.splitTextToSize(q.explanation || '', contentWidth - 10);
// //       explanationLines.forEach((line: string) => {
// //         pdf.text(line, margin + 8, currentY);
// //         currentY += 4;
        
// //         if (currentY > pageHeight - 20) {
// //           pdf.addPage();
// //           pageNumber++;
// //           currentY = margin;
// //           pdf.setFontSize(10);
// //           pdf.setFont(undefined, 'normal');
// //           pdf.text(`${topic} - Page ${pageNumber}`, margin, currentY);
// //           currentY += 8;
// //         }
// //       });
// //     }

// //     // Add space for answers (short/long)
// //     if (q.type === 'short' || q.type === 'long') {
// //       currentY += 5;
// //       const lines = q.type === 'short' ? 3 : 5;
      
// //       for (let i = 0; i < lines; i++) {
// //         pdf.setLineWidth(0.1);
// //         pdf.line(margin + 5, currentY, pageWidth - margin - 5, currentY);
// //         currentY += 5;
        
// //         if (currentY > pageHeight - 20) {
// //           pdf.addPage();
// //           pageNumber++;
// //           currentY = margin;
// //           pdf.setFontSize(10);
// //           pdf.setFont(undefined, 'normal');
// //           pdf.text(`${topic} - Page ${pageNumber}`, margin, currentY);
// //           currentY += 8;
// //         }
// //       }
// //     }

// //     // Question spacing
// //     currentY += 8;
// //   }

// //   pdf.save(filename);
// //   return Promise.resolve(true);
// // }

// // /**
// //  * Export to plain text
// //  */
// // export function exportToText(
// //   topic: string,
// //   questions: api.Question[],
// //   includeAnswers: boolean = false
// // ): string {
// //   let text = `${topic}\n`;
// //   text += `${'='.repeat(topic.length)}\n\n`;
// //   text += `Questions: ${questions.length}\n`;
// //   text += `Total Marks: ${questions.reduce((sum, q) => sum + q.marks, 0)}\n`;
// //   text += `Date: ${new Date().toLocaleDateString()}\n\n`;
// //   text += `${'='.repeat(50)}\n\n`;

// //   questions.forEach((q, index) => {
// //     text += `Q${index + 1}. ${q.text} (${q.marks} mark${q.marks > 1 ? 's' : ''})\n`;

// //     if (q.type === 'mcq' && q.options) {
// //       q.options.forEach((option, i) => {
// //         text += `${String.fromCharCode(65 + i)}. ${option}\n`;
// //       });
// //     }

// //     if (includeAnswers) {
// //       text += `\nAnswer: `;
// //       if (q.type === 'mcq' && typeof q.correct_answer === 'number') {
// //         text += String.fromCharCode(65 + q.correct_answer);
// //       } else if (q.type === 'mcq' && Array.isArray(q.correct_answer)) {
// //         text += q.correct_answer.map(i => String.fromCharCode(65 + i)).join(', ');
// //       } else {
// //         text += q.correct_answer || 'N/A';
// //       }
// //       text += `\n\nExplanation: ${q.explanation}\n`;
// //     }

// //     text += `\n${'─'.repeat(50)}\n\n`;
// //   });

// //   return text;
// // }

// // /**
// //  * Download text file
// //  */
// // export function downloadFile(content: string, filename: string, mimeType: string = 'text/plain') {
// //   const blob = new Blob([content], { type: mimeType });
// //   const url = window.URL.createObjectURL(blob);
// //   const link = document.createElement('a');
// //   link.href = url;
// //   link.download = filename;
// //   document.body.appendChild(link);
// //   link.click();
// //   document.body.removeChild(link);
// //   window.URL.revokeObjectURL(url);
// // }

// // /**
// //  * Export worksheet to file
// //  */
// // export async function exportWorksheet(
// //   topic: string,
// //   questions: api.Question[],
// //   options: ExportOptions
// // ) {
// //   const sanitizedTopic = topic.replace(/[^a-z0-9]/gi, '_').toLowerCase();
// //   const filename = options.filename || `worksheet_${sanitizedTopic}_${Date.now()}`;

// //   if (options.format === 'pdf') {
// //     return exportToPDF(topic, questions, options.includeAnswers, `${filename}.pdf`);
// //   } else if (options.format === 'txt') {
// //     const content = exportToText(topic, questions, options.includeAnswers);
// //     downloadFile(content, `${filename}.txt`);
// //     return Promise.resolve(true);
// //   }

// //   throw new Error(`Unsupported format: ${options.format}`);
// // }


// // --- INTERFACES AND IMPORTS ---

// import * as api from './api';
// // Assuming html2pdf is available via dynamic import or is a global object
// // const html2pdf = (await import('html2pdf.js')).default; 

// export interface ExportOptions {
//     includeAnswers: boolean;
//     format: 'pdf' | 'txt';
//     filename?: string;
// }

// // --- CORE HTML GENERATION FUNCTION ---

// export function generateWorksheetHTML(
//     topic: string,
//     questions: api.Question[],
//     includeAnswers: boolean = false
// ): string {
//     const totalMarks = questions.reduce((sum, q) => sum + q.marks, 0);
//     const date = new Date().toLocaleDateString('en-US', {
//         year: 'numeric',
//         month: 'long',
//         day: 'numeric'
//     });

//     const questionsHTML = questions.map((q, index) => {
//         let questionHTML = `
//             <div class="question-item">
//                 <p class="question-text">
//                     Q${index + 1}. ${q.text}
//                     <span class="marks-float">
//                         (${q.marks} mark${q.marks > 1 ? 's' : ''})
//                     </span>
//                 </p>
//         `;

//         // Add options for MCQ
//         if (q.type === 'mcq' && q.options) {
//             questionHTML += `<div class="mcq-options">`;
//             q.options.forEach((option, i) => {
//                 questionHTML += `<p><strong>${String.fromCharCode(65 + i)}.</strong> ${option}</p>`;
//             });
//             questionHTML += `</div>`;
//         }

//         // Add answer section
//         if (includeAnswers) {
//             questionHTML += `
//                 <div class="answer-box">
//                     <p><strong class="answer-label">Answer:</strong> `;

//             if (q.type === 'mcq' && typeof q.correct_answer === 'number') {
//                 const answerIndex = q.correct_answer;
//                 questionHTML += `${String.fromCharCode(65 + answerIndex)}`;
//             } else if (q.type === 'mcq' && Array.isArray(q.correct_answer)) {
//                 questionHTML += q.correct_answer.map(i => String.fromCharCode(65 + i)).join(', ');
//             } else {
//                 questionHTML += q.correct_answer || 'N/A';
//             }

//             questionHTML += `</p>`;
//             questionHTML += `<p><strong class="explanation-label">Explanation:</strong> ${q.explanation || ''}</p>`;
//             questionHTML += `</div>`;
//         }

//         // Add space for short/long answer questions
//         if (q.type === 'short' || q.type === 'long') {
//             const lines = q.type === 'short' ? 5 : 8;
//             questionHTML += `<div class="answer-space" style="height: ${lines * 18}px;"></div>`;
//         }

//         questionHTML += `</div>`;
//         return questionHTML;
//     }).join('');

//     const html = `
//         <!DOCTYPE html>
//         <html lang="en">
//         <head>
//             <meta charset="UTF-8">
//             <title>${topic || 'Worksheet'}</title>
//             <style>
//                 /* Base Styles */
//                 * { margin: 0; padding: 0; box-sizing: border-box; }
//                 body {
//                     font-family: Arial, sans-serif;
//                     line-height: 1.5;
//                     color: #333;
//                     background: white;
//                 }
//                 .container {
//                     max-width: 750px;
//                     margin: 0 auto;
//                     padding: 30px 20px;
//                 }
                
//                 /* Header */
//                 .header {
//                     text-align: center;
//                     margin-bottom: 25px;
//                     border-bottom: 2px solid #333;
//                     padding-bottom: 15px;
//                 }
//                 .header h1 { font-size: 22px; margin-bottom: 8px; color: #2c3e50; }
//                 .meta-info {
//                     display: flex;
//                     justify-content: space-between;
//                     font-size: 13px;
//                     color: #7f8c8d;
//                     margin-top: 5px;
//                 }
                
//                 /* Question Styling */
//                 .question-item {
//                     margin-bottom: 25px;
//                     padding-bottom: 5px;
//                     page-break-inside: avoid; 
//                     break-inside: avoid; 
//                 }
//                 .question-text {
//                     margin: 0 0 10px 0;
//                     font-weight: bold;
//                     font-size: 15px;
//                     display: block; 
//                     width: 100%;
//                 }
//                 .marks-float {
//                     float: right;
//                     font-size: 13px;
//                     font-weight: normal;
//                     display: inline-block;
//                 }
//                 .mcq-options { margin-left: 20px; margin-bottom: 10px; font-weight: normal; font-size: 14px; }
//                 .mcq-options p { margin: 5px 0; }
                
//                 /* Answer Space for short/long answers */
//                 .answer-space {
//                     margin-top: 10px;
//                     border-bottom: 1px dotted #999;
//                     display: block;
//                 }

//                 /* Answer/Explanation Box */
//                 .answer-box {
//                     margin-top: 10px;
//                     padding: 8px 10px;
//                     background-color: #f7f7f7;
//                     border-left: 4px solid #4CAF50;
//                     font-size: 14px;
//                     page-break-inside: avoid;
//                 }
//                 .answer-box p { margin: 5px 0; }
//                 .answer-label { color: #4CAF50; font-weight: bold; }
//                 .explanation-label { color: #2196F3; font-weight: bold; }

//                 /* Print/PDF Specific Styles */
//                 @page {
//                     size: A4;
//                     margin: 10mm;
//                 }
//             </style>
//         </head>
//         <body>
//             <div class="container">
//                 <div class="header">
//                     <h1>${topic || 'Worksheet'}</h1>
//                     <div class="meta-info">
//                         <span>Questions: ${questions.length}</span>
//                         <span>Total Marks: ${totalMarks}</span>
//                         <span>Date: ${date}</span>
//                     </div>
//                 </div>
//                 <div class="questions">
//                     ${questionsHTML}
//                 </div>
//             </div>
//         </body>
//         </html>
//     `;

//     return html;
// }

// // --- PDF EXPORT FUNCTION (REVISED) ---

// export async function exportToPDF(
//     topic: string,
//     questions: api.Question[],
//     includeAnswers: boolean = false,
//     filename: string = 'worksheet.pdf'
// ) {
//     const html2pdf = (window as any).html2pdf;
    
//     if (!html2pdf) {
//         alert("PDF library not loaded. Please refresh the page and try again.");
//         return Promise.reject(new Error("html2pdf not available"));
//     }

//     const htmlContent = generateWorksheetHTML(topic, questions, includeAnswers);
//     const tempElement = document.createElement('div');
//     tempElement.innerHTML = htmlContent;

//     const pdfOptions = {
//         margin: 10,
//         filename: filename,
//         image: { type: 'jpeg', quality: 0.98 },
//         html2canvas: { scale: 2 },
//         jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
//     };

//     try {
//         await html2pdf().set(pdfOptions).from(tempElement).save();
//         return Promise.resolve();
//     } catch (error) {
//         console.error("PDF Export Error:", error);
//         alert("Failed to export PDF. Check the console for details.");
//         return Promise.reject(error);
//     }
// }


// // --- OTHER EXPORT FUNCTIONS (UNMODIFIED) ---

// export function exportToText(
//     topic: string,
//     questions: api.Question[],
//     includeAnswers: boolean = false
// ): string {
//     let text = `${topic}\n`;
//     text += `${'='.repeat(topic.length)}\n\n`;
//     text += `Questions: ${questions.length}\n`;
//     text += `Total Marks: ${questions.reduce((sum, q) => sum + q.marks, 0)}\n`;
//     text += `Date: ${new Date().toLocaleDateString()}\n\n`;
//     text += `${'='.repeat(50)}\n\n`;

//     questions.forEach((q, index) => {
//         text += `Q${index + 1}. ${q.text} (${q.marks} mark${q.marks > 1 ? 's' : ''})\n`;

//         if (q.type === 'mcq' && q.options) {
//             q.options.forEach((option, i) => {
//                 text += `${String.fromCharCode(65 + i)}. ${option}\n`;
//             });
//         }

//         if (includeAnswers) {
//             text += `\nAnswer: `;
//             if (q.type === 'mcq' && typeof q.correct_answer === 'number') {
//                 text += String.fromCharCode(65 + q.correct_answer);
//             } else if (q.type === 'mcq' && Array.isArray(q.correct_answer)) {
//                 text += q.correct_answer.map(i => String.fromCharCode(65 + i)).join(', ');
//             } else {
//                 text += q.correct_answer || 'N/A';
//             }
//             text += `\n\nExplanation: ${q.explanation}\n`;
//         }

//         text += `\n${'─'.repeat(50)}\n\n`;
//     });

//     return text;
// }

// export function downloadFile(content: string, filename: string, mimeType: string = 'text/plain') {
//     const blob = new Blob([content], { type: mimeType });
//     const url = window.URL.createObjectURL(blob);
//     const link = document.createElement('a');
//     link.href = url;
//     link.download = filename;
//     document.body.appendChild(link);
//     link.click();
//     document.body.removeChild(link);
//     window.URL.revokeObjectURL(url);
// }

// export async function exportWorksheet(
//     topic: string,
//     questions: api.Question[],
//     options: ExportOptions
// ) {
//     const sanitizedTopic = topic.replace(/[^a-z0-9]/gi, '_').toLowerCase();
//     const filename = options.filename || `worksheet_${sanitizedTopic}_${Date.now()}`;

//     if (options.format === 'pdf') {
//         return exportToPDF(topic, questions, options.includeAnswers, `${filename}.pdf`);
//     } else if (options.format === 'txt') {
//         const content = exportToText(topic, questions, options.includeAnswers);
//         downloadFile(content, `${filename}.txt`);
//         return Promise.resolve(true);
//     }

//     throw new Error(`Unsupported format: ${options.format}`);
// }

// import * as api from './api';

// export interface ExportOptions {
//   includeAnswers: boolean;
//   format: 'pdf' | 'txt';
//   filename?: string;
// }
// ... (omitted commented-out code)

// --- INTERFACES AND IMPORTS ---

import * as api from './api';
// Assuming html2pdf is available via dynamic import or is a global object
// const html2pdf = (await import('html2pdf.js')).default; 

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
        let questionHTML = `
            <div class="question-item">
                <p class="question-text">
                    Q${index + 1}. ${q.text}
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
                questionHTML += `<p><strong>${String.fromCharCode(65 + i)}.</strong> ${option}</p>`;
            });
            questionHTML += `</div>`;
        }

        // Add answer section
        if (includeAnswers) {
            questionHTML += `
                <div class="answer-box">
                    <p><strong class="answer-label">Answer:</strong> `;

            if (q.type === 'mcq' && typeof q.correct_answer === 'number') {
                const answerIndex = q.correct_answer;
                questionHTML += `${String.fromCharCode(65 + answerIndex)}`;
            } else if (q.type === 'mcq' && Array.isArray(q.correct_answer)) {
                questionHTML += q.correct_answer.map(i => String.fromCharCode(65 + i)).join(', ');
            } else {
                questionHTML += q.correct_answer || 'N/A';
            }

            questionHTML += `</p>`;
            questionHTML += `<p><strong class="explanation-label">Explanation:</strong> ${q.explanation || ''}</p>`;
            questionHTML += `</div>`;
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
    const html2pdf = (window as any).html2pdf;
    
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