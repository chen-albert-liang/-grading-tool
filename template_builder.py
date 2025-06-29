#!/usr/bin/env python3
"""
Template Builder for Automated Homework Grading
Extracts answer key template from teacher's homework OCR results
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from automated_grading_system import Question

class TemplateBuilder:
    """Builds grading template from teacher's answer key"""
    
    def __init__(self):
        self.question_patterns = {
            '填空': r'填空[（(](\d+)[）)]',
            '解比例': r'解比例[（(](\d+)[）)]',
            '应用题': r'应用题',
            '拓展题': r'拓展题'
        }
    
    def extract_template_from_ocr(self, ocr_result: Dict[str, Any]) -> Dict[str, Question]:
        """Extract question template from teacher's OCR result"""
        template = {}
        
        texts = ocr_result.get('rec_texts', [])
        scores = ocr_result.get('rec_scores', [])
        boxes = ocr_result.get('rec_boxes', [])
        
        # Find question sections and their answers
        current_section = None
        current_question = None
        
        # First pass: identify sections and questions
        for i, (text, score, box) in enumerate(zip(texts, scores, boxes)):
            cleaned_text = self._clean_text(text)
            
            # Identify question sections
            if self._is_section_header(cleaned_text):
                current_section = self._extract_section_name(cleaned_text)
                print(f"Found section: {current_section}")
                continue
            
            # Identify individual questions
            question_match = self._extract_question_number(cleaned_text)
            if question_match:
                current_question = question_match
                print(f"Found question: {current_question}")
                continue
        
        # Second pass: look for answers with better context
        # Look for specific answer patterns in the teacher's homework
        answer_patterns = [
            # Numeric answers
            r'(\d+(?:\.\d+)?)',  # Numbers with optional decimals
            # Formula answers
            r'([xX]\s*=\s*[\d\.]+)',  # x = number
            r'([\d\.]+\s*:\s*[\d\.]+)',  # ratio format
            # Text answers
            r'(甲[：:]\d+袋[，,]\s*乙[：:]\d+袋)',  # Chinese text answers
        ]
        
        for i, (text, score, box) in enumerate(zip(texts, scores, boxes)):
            cleaned_text = self._clean_text(text)
            
            # Skip if it's clearly not an answer
            if self._is_question_text(cleaned_text) or len(cleaned_text) < 1:
                continue
            
            # Check if this looks like an answer using patterns
            for pattern in answer_patterns:
                match = re.search(pattern, cleaned_text)
                if match:
                    answer_text = match.group(1)
                    answer_type = self._determine_answer_type(answer_text)
                    points = self._estimate_points(current_section, str(i))
                    
                    question_id = f"Q{i+1}"
                    template[question_id] = Question(
                        question_id=question_id,
                        question_text=f"Question {i+1}",
                        expected_answer=answer_text,
                        answer_type=answer_type,
                        points=points
                    )
                    print(f"Extracted answer: {question_id} = {answer_text} ({answer_type})")
                    break
        
        # If we didn't find enough answers, try a simpler approach
        if len(template) < 3:
            print("Using fallback answer extraction...")
            template = self._fallback_answer_extraction(texts, scores, boxes)
        
        return template
    
    def _clean_text(self, text: str) -> str:
        """Clean OCR text"""
        text = re.sub(r'[^\w\s\.\-\+\=\:\/\(\)\[\]\{\}]', '', text)
        return text.strip()
    
    def _is_section_header(self, text: str) -> bool:
        """Check if text is a section header"""
        section_indicators = ['基础练习', '提高练习', '拓展练习']
        return any(indicator in text for indicator in section_indicators)
    
    def _extract_section_name(self, text: str) -> str:
        """Extract section name from header"""
        if '基础练习' in text:
            return '基础练习'
        elif '提高练习' in text:
            return '提高练习'
        elif '拓展练习' in text:
            return '拓展练习'
        return '未知'
    
    def _extract_question_number(self, text: str) -> str:
        """Extract question number from text"""
        # Look for patterns like "1.", "2.", "(1)", "(2)", etc.
        patterns = [
            r'(\d+)\.',  # 1., 2., etc.
            r'[（(](\d+)[）)]',  # (1), (2), etc.
            r'（(\d+)）',  # （1）, （2）, etc.
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _looks_like_answer(self, text: str) -> bool:
        """Check if text looks like an answer"""
        # Look for numbers, mathematical symbols, or short responses
        if re.match(r'^[\d\.\-\+\=\:\/\(\)\[\]\{\}]+$', text):
            return True
        if len(text) <= 15 and any(char.isdigit() for char in text):
            return True
        return False
    
    def _determine_answer_type(self, text: str) -> str:
        """Determine the type of answer"""
        if re.match(r'^[\d\.]+$', text):
            return 'numeric'
        elif any(symbol in text for symbol in ['=', ':', '+', '-', '×', '÷']):
            return 'formula'
        else:
            return 'text'
    
    def _estimate_points(self, section: str, question: str) -> float:
        """Estimate points based on section and question type"""
        if section == '基础练习':
            return 2.0
        elif section == '提高练习':
            return 4.0
        elif section == '拓展练习':
            return 6.0
        else:
            return 3.0
    
    def _fallback_answer_extraction(self, texts, scores, boxes):
        """Fallback method to extract answers when pattern matching fails"""
        template = {}
        
        # Look for standalone numbers and short answers
        for i, (text, score, box) in enumerate(zip(texts, scores, boxes)):
            cleaned_text = self._clean_text(text)
            
            # Skip long text or question text
            if len(cleaned_text) > 20 or self._is_question_text(cleaned_text):
                continue
            
            # Look for numbers, formulas, or short answers
            if self._looks_like_answer(cleaned_text):
                answer_type = self._determine_answer_type(cleaned_text)
                points = 3.0  # Default points
                
                question_id = f"Q{i+1}"
                template[question_id] = Question(
                    question_id=question_id,
                    question_text=f"Question {i+1}",
                    expected_answer=cleaned_text,
                    answer_type=answer_type,
                    points=points
                )
                print(f"Fallback extracted: {question_id} = {cleaned_text} ({answer_type})")
        
        return template
    
    def save_template(self, template: Dict[str, Question], output_path: str):
        """Save template to JSON file"""
        template_data = {}
        for q_id, question in template.items():
            template_data[q_id] = {
                'question_id': question.question_id,
                'question_text': question.question_text,
                'expected_answer': question.expected_answer,
                'answer_type': question.answer_type,
                'points': question.points,
                'tolerance': question.tolerance,
                'partial_credit': question.partial_credit
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
        
        print(f"Template saved to {output_path}")

def main():
    """Extract template from teacher's homework"""
    # Load teacher's OCR result
    with open('output/homework1_res.json', 'r', encoding='utf-8') as f:
        teacher_ocr = json.load(f)
    
    # Build template
    builder = TemplateBuilder()
    template = builder.extract_template_from_ocr(teacher_ocr)
    
    # Save template
    builder.save_template(template, 'teacher_template.json')
    
    print(f"Extracted {len(template)} questions from teacher's homework")
    for q_id, question in template.items():
        print(f"{q_id}: {question.expected_answer} ({question.answer_type}) - {question.points} points")

if __name__ == "__main__":
    main() 