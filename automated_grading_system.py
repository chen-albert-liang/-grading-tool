#!/usr/bin/env python3
"""
Automated Homework Grading System
Leverages PaddleOCR output to grade handwritten homework against teacher's answer key
"""

import json
import re
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Question:
    """Represents a question with its expected answer and scoring criteria"""
    question_id: str
    question_text: str
    expected_answer: str
    answer_type: str  # 'numeric', 'text', 'formula', 'multiple_choice'
    points: float
    tolerance: float = 0.1  # For numeric answers
    partial_credit: bool = True

@dataclass
class StudentAnswer:
    """Represents a student's answer to a question"""
    question_id: str
    extracted_text: str
    confidence_score: float
    bounding_box: List[int]
    is_handwritten: bool = True

@dataclass
class GradingResult:
    """Represents the grading result for a student"""
    student_id: str
    total_score: float
    max_score: float
    question_results: List[Dict[str, Any]]
    overall_accuracy: float
    feedback: List[str]

class HomeworkGradingSystem:
    """Main class for automated homework grading"""
    
    def __init__(self, template_path: str = None):
        self.template = self._load_template(template_path) if template_path else None
        self.ocr_results = {}
        
    def _load_template(self, template_path: str) -> Dict[str, Question]:
        """Load teacher's answer key template"""
        # This would be created from the teacher's answer key
        # For now, we'll create a sample template based on the homework structure
        template = {
            "1.1": Question("1.1", "填空(1)", "7", "numeric", 2.0),
            "1.2": Question("1.2", "填空(2)", "0.5", "numeric", 2.0),
            "1.3": Question("1.3", "填空(3)", "a:b=5:4", "formula", 3.0),
            "1.4": Question("1.4", "填空(4)", "24", "numeric", 2.0),
            "1.5": Question("1.5", "填空(5)", "4:5", "formula", 3.0),
            "2.1": Question("2.1", "解比例(1)", "x=1.2", "formula", 4.0),
            "2.2": Question("2.2", "解比例(2)", "x=125", "numeric", 4.0),
            "2.3": Question("2.3", "解比例(3)", "x=8", "numeric", 4.0),
            "2.4": Question("2.4", "解比例(4)", "x=9", "numeric", 4.0),
            "3.1": Question("3.1", "列比例(1)", "45:x=25:8", "formula", 5.0),
            "3.2": Question("3.2", "列比例(2)", "4.5:0.2=x:0.5", "formula", 5.0),
            "4": Question("4", "应用题", "7.5", "numeric", 6.0),
            "5": Question("5", "拓展题", "甲:96袋,乙:72袋", "text", 8.0)
        }
        return template
    
    def load_ocr_result(self, json_path: str) -> Dict[str, Any]:
        """Load OCR result from JSON file"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_answers_from_ocr(self, ocr_result: Dict[str, Any]) -> List[StudentAnswer]:
        """Extract student answers from OCR result"""
        answers = []
        
        # Get text and confidence scores
        texts = ocr_result.get('rec_texts', [])
        scores = ocr_result.get('rec_scores', [])
        boxes = ocr_result.get('rec_boxes', [])
        
        # Filter for handwritten answers (typically lower confidence scores)
        # and answers that appear to be responses (numbers, formulas, etc.)
        for i, (text, score, box) in enumerate(zip(texts, scores, boxes)):
            # Clean the text
            cleaned_text = self._clean_text(text)
            
            # Skip if text is too short or appears to be question text
            if len(cleaned_text) < 2 or self._is_question_text(cleaned_text):
                continue
                
            # Check if this looks like an answer
            if self._looks_like_answer(cleaned_text):
                answer = StudentAnswer(
                    question_id=f"answer_{i}",
                    extracted_text=cleaned_text,
                    confidence_score=score,
                    bounding_box=box,
                    is_handwritten=True
                )
                answers.append(answer)
        
        return answers
    
    def _clean_text(self, text: str) -> str:
        """Clean OCR text for better comparison"""
        # Remove common OCR artifacts
        text = re.sub(r'[^\w\s\.\-\+\=\:\/\(\)\[\]\{\}]', '', text)
        text = text.strip()
        return text
    
    def _is_question_text(self, text: str) -> bool:
        """Check if text appears to be question text rather than answer"""
        question_indicators = ['填空', '解比例', '应用题', '拓展题', '基础练习', '提高练习']
        return any(indicator in text for indicator in question_indicators)
    
    def _looks_like_answer(self, text: str) -> bool:
        """Check if text looks like a mathematical answer"""
        # Look for numbers, mathematical symbols, or short responses
        if re.match(r'^[\d\.\-\+\=\:\/\(\)\[\]\{\}]+$', text):
            return True
        if len(text) <= 10 and any(char.isdigit() for char in text):
            return True
        return False
    
    def align_answers_with_questions(self, answers: List[StudentAnswer], 
                                   template: Dict[str, Question]) -> Dict[str, StudentAnswer]:
        """Align extracted answers with template questions based on spatial position"""
        aligned_answers = {}
        
        # Sort answers by vertical position (top to bottom)
        sorted_answers = sorted(answers, key=lambda x: x.bounding_box[1])
        
        # Simple alignment based on position - in practice, you'd want more sophisticated logic
        question_ids = list(template.keys())
        
        for i, answer in enumerate(sorted_answers):
            if i < len(question_ids):
                aligned_answers[question_ids[i]] = answer
        
        return aligned_answers
    
    def grade_answer(self, student_answer: StudentAnswer, 
                    expected_question: Question) -> Dict[str, Any]:
        """Grade a single answer against the expected answer"""
        result = {
            'question_id': expected_question.question_id,
            'expected_answer': expected_question.expected_answer,
            'student_answer': student_answer.extracted_text,
            'confidence_score': student_answer.confidence_score,
            'points_earned': 0.0,
            'max_points': expected_question.points,
            'is_correct': False,
            'feedback': []
        }
        
        # Different grading logic based on answer type
        if expected_question.answer_type == 'numeric':
            result = self._grade_numeric_answer(student_answer, expected_question, result)
        elif expected_question.answer_type == 'formula':
            result = self._grade_formula_answer(student_answer, expected_question, result)
        elif expected_question.answer_type == 'text':
            result = self._grade_text_answer(student_answer, expected_question, result)
        else:
            result = self._grade_general_answer(student_answer, expected_question, result)
        
        return result
    
    def _grade_numeric_answer(self, student_answer: StudentAnswer, 
                            expected_question: Question, result: Dict[str, Any]) -> Dict[str, Any]:
        """Grade numeric answers with tolerance"""
        try:
            # Extract numbers from student answer
            student_numbers = re.findall(r'[\d\.]+', student_answer.extracted_text)
            expected_numbers = re.findall(r'[\d\.]+', expected_question.expected_answer)
            
            if not student_numbers:
                result['feedback'].append("No numeric answer found")
                return result
            
            # Compare numbers with tolerance
            student_value = float(student_numbers[0])
            expected_value = float(expected_numbers[0])
            
            if abs(student_value - expected_value) <= expected_question.tolerance:
                result['is_correct'] = True
                result['points_earned'] = expected_question.points
                result['feedback'].append("Correct!")
            else:
                result['feedback'].append(f"Expected {expected_value}, got {student_value}")
                
        except (ValueError, IndexError):
            result['feedback'].append("Could not parse numeric answer")
        
        return result
    
    def _grade_formula_answer(self, student_answer: StudentAnswer, 
                            expected_question: Question, result: Dict[str, Any]) -> Dict[str, Any]:
        """Grade formula answers using similarity matching"""
        # Normalize formulas for comparison
        student_formula = self._normalize_formula(student_answer.extracted_text)
        expected_formula = self._normalize_formula(expected_question.expected_answer)
        
        # Calculate similarity
        similarity = SequenceMatcher(None, student_formula, expected_formula).ratio()
        
        if similarity >= 0.8:  # 80% similarity threshold
            result['is_correct'] = True
            result['points_earned'] = expected_question.points
            result['feedback'].append("Correct formula!")
        elif similarity >= 0.6 and expected_question.partial_credit:
            result['points_earned'] = expected_question.points * 0.5
            result['feedback'].append(f"Partially correct (similarity: {similarity:.2f})")
        else:
            result['feedback'].append(f"Formula doesn't match (similarity: {similarity:.2f})")
        
        return result
    
    def _grade_text_answer(self, student_answer: StudentAnswer, 
                          expected_question: Question, result: Dict[str, Any]) -> Dict[str, Any]:
        """Grade text answers using similarity matching"""
        similarity = SequenceMatcher(None, 
                                   student_answer.extracted_text.lower(),
                                   expected_question.expected_answer.lower()).ratio()
        
        if similarity >= 0.8:
            result['is_correct'] = True
            result['points_earned'] = expected_question.points
            result['feedback'].append("Correct answer!")
        elif similarity >= 0.6 and expected_question.partial_credit:
            result['points_earned'] = expected_question.points * 0.5
            result['feedback'].append(f"Partially correct (similarity: {similarity:.2f})")
        else:
            result['feedback'].append(f"Answer doesn't match (similarity: {similarity:.2f})")
        
        return result
    
    def _grade_general_answer(self, student_answer: StudentAnswer, 
                            expected_question: Question, result: Dict[str, Any]) -> Dict[str, Any]:
        """General grading for other answer types"""
        similarity = SequenceMatcher(None, 
                                   student_answer.extracted_text,
                                   expected_question.expected_answer).ratio()
        
        if similarity >= 0.8:
            result['is_correct'] = True
            result['points_earned'] = expected_question.points
        elif similarity >= 0.6 and expected_question.partial_credit:
            result['points_earned'] = expected_question.points * 0.5
        
        result['feedback'].append(f"Similarity score: {similarity:.2f}")
        return result
    
    def _normalize_formula(self, formula: str) -> str:
        """Normalize mathematical formulas for comparison"""
        # Remove spaces and convert to lowercase
        formula = re.sub(r'\s+', '', formula.lower())
        # Normalize common mathematical symbols
        formula = formula.replace('×', '*').replace('÷', '/')
        return formula
    
    def grade_homework(self, student_id: str, ocr_result: Dict[str, Any]) -> GradingResult:
        """Grade a complete homework assignment"""
        if not self.template:
            raise ValueError("Template not loaded. Please load teacher's answer key first.")
        
        # Extract answers from OCR
        answers = self.extract_answers_from_ocr(ocr_result)
        
        # Align answers with questions
        aligned_answers = self.align_answers_with_questions(answers, self.template)
        
        # Grade each answer
        question_results = []
        total_score = 0.0
        max_score = sum(q.points for q in self.template.values())
        
        for question_id, expected_question in self.template.items():
            if question_id in aligned_answers:
                result = self.grade_answer(aligned_answers[question_id], expected_question)
            else:
                result = {
                    'question_id': question_id,
                    'expected_answer': expected_question.expected_answer,
                    'student_answer': 'No answer found',
                    'confidence_score': 0.0,
                    'points_earned': 0.0,
                    'max_points': expected_question.points,
                    'is_correct': False,
                    'feedback': ['No answer detected']
                }
            
            question_results.append(result)
            total_score += result['points_earned']
        
        # Calculate overall accuracy
        overall_accuracy = total_score / max_score if max_score > 0 else 0.0
        
        # Generate feedback
        feedback = []
        correct_count = sum(1 for r in question_results if r['is_correct'])
        feedback.append(f"Score: {total_score:.1f}/{max_score:.1f} ({overall_accuracy:.1%})")
        feedback.append(f"Correct answers: {correct_count}/{len(question_results)}")
        
        return GradingResult(
            student_id=student_id,
            total_score=total_score,
            max_score=max_score,
            question_results=question_results,
            overall_accuracy=overall_accuracy,
            feedback=feedback
        )
    
    def batch_grade(self, ocr_results_dir: str) -> List[GradingResult]:
        """Grade multiple homework assignments"""
        results = []
        ocr_dir = Path(ocr_results_dir)
        
        for json_file in ocr_dir.glob("hw_*_res.json"):
            if "hw_1" in json_file.name:  # Skip teacher's answer key
                continue
                
            student_id = json_file.stem.replace("_res", "")
            logger.info(f"Grading {student_id}...")
            
            try:
                ocr_result = self.load_ocr_result(str(json_file))
                result = self.grade_homework(student_id, ocr_result)
                results.append(result)
            except Exception as e:
                logger.error(f"Error grading {student_id}: {e}")
        
        return results
    
    def generate_report(self, results: List[GradingResult], output_path: str = "grading_report.json"):
        """Generate comprehensive grading report"""
        if not results:
            report = {
                'summary': {
                    'total_students': 0,
                    'average_score': 0.0,
                    'average_accuracy': 0.0,
                    'highest_score': 0.0,
                    'lowest_score': 0.0,
                    'max_score': 0.0
                },
                'student_results': []
            }
        else:
            report = {
                'summary': {
                    'total_students': len(results),
                    'average_score': np.mean([r.total_score for r in results]),
                    'average_accuracy': np.mean([r.overall_accuracy for r in results]),
                    'highest_score': max([r.total_score for r in results]),
                    'lowest_score': min([r.total_score for r in results]),
                    'max_score': results[0].max_score if results else 0.0
                },
                'student_results': [
                    {
                        'student_id': r.student_id,
                        'total_score': r.total_score,
                        'max_score': r.max_score,
                        'accuracy': r.overall_accuracy,
                        'feedback': r.feedback,
                        'question_details': r.question_results
                    }
                    for r in results
                ]
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Report saved to {output_path}")
        return report

def main():
    """Main function to demonstrate the grading system"""
    # Initialize grading system
    grader = HomeworkGradingSystem()
    
    # Grade all homework assignments
    results = grader.batch_grade("output")
    
    # Generate report
    report = grader.generate_report(results)
    
    # Print summary
    print("\n=== GRADING SUMMARY ===")
    print(f"Total students graded: {report['summary']['total_students']}")
    print(f"Average score: {report['summary']['average_score']:.1f}")
    print(f"Average accuracy: {report['summary']['average_accuracy']:.1%}")
    print(f"Score range: {report['summary']['lowest_score']:.1f} - {report['summary']['highest_score']:.1f}")
    
    # Print individual results
    print("\n=== INDIVIDUAL RESULTS ===")
    for result in results:
        print(f"{result.student_id}: {result.total_score:.1f}/{result.max_score:.1f} ({result.overall_accuracy:.1%})")

if __name__ == "__main__":
    main() 