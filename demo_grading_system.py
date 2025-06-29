#!/usr/bin/env python3
"""
Demo: Automated Homework Grading System
Complete workflow demonstration from OCR to grading report
"""

import json
import time
from pathlib import Path
from automated_grading_system import HomeworkGradingSystem
from template_builder import TemplateBuilder

def demo_complete_workflow():
    """Demonstrate the complete automated grading workflow"""
    
    print("=== AUTOMATED HOMEWORK GRADING SYSTEM DEMO ===\n")
    
    # Step 1: Build template from teacher's answer key
    print("Step 1: Building template from teacher's answer key...")
    try:
        with open('output/hw_1_res.json', 'r', encoding='utf-8') as f:
            teacher_ocr = json.load(f)
        
        builder = TemplateBuilder()
        template = builder.extract_template_from_ocr(teacher_ocr)
        builder.save_template(template, 'teacher_template.json')
        
        print(f"✓ Extracted {len(template)} questions from teacher's homework")
        for q_id, question in template.items():
            print(f"  - {q_id}: {question.expected_answer} ({question.answer_type}) - {question.points} points")
        
    except Exception as e:
        print(f"✗ Error building template: {e}")
        print("Using default template instead...")
        template = None
    
    # Step 2: Initialize grading system
    print("\nStep 2: Initializing grading system...")
    grader = HomeworkGradingSystem()
    if template:
        grader.template = template
    
    # Step 3: Process student homework
    print("\nStep 3: Processing student homework...")
    student_files = list(Path("output").glob("hw_*_res.json"))
    student_files = [f for f in student_files if "hw_1" not in f.name]  # Skip teacher's answer key
    
    print(f"Found {len(student_files)} student homework files:")
    for file in student_files:
        print(f"  - {file.name}")
    
    # Step 4: Grade all homework
    print("\nStep 4: Grading homework assignments...")
    start_time = time.time()
    
    results = []
    for json_file in student_files:
        student_id = json_file.stem.replace("_res", "")
        print(f"  Grading {student_id}...")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                ocr_result = json.load(f)
            
            result = grader.grade_homework(student_id, ocr_result)
            results.append(result)
            print(f"    ✓ Score: {result.total_score:.1f}/{result.max_score:.1f} ({result.overall_accuracy:.1%})")
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    grading_time = time.time() - start_time
    print(f"\n✓ Grading completed in {grading_time:.2f} seconds")
    
    # Step 5: Generate comprehensive report
    print("\nStep 5: Generating grading report...")
    report = grader.generate_report(results, "comprehensive_grading_report.json")
    
    # Step 6: Display results
    print("\n=== GRADING RESULTS ===")
    print(f"Total students graded: {len(results)}")
    print(f"Average score: {report['summary']['average_score']:.1f}/{report['summary']['max_score']:.1f}")
    print(f"Average accuracy: {report['summary']['average_accuracy']:.1%}")
    print(f"Score range: {report['summary']['lowest_score']:.1f} - {report['summary']['highest_score']:.1f}")
    
    print("\n=== INDIVIDUAL STUDENT RESULTS ===")
    for result in results:
        print(f"{result.student_id}:")
        print(f"  Score: {result.total_score:.1f}/{result.max_score:.1f} ({result.overall_accuracy:.1%})")
        print(f"  Feedback: {', '.join(result.feedback)}")
        
        # Show some question details
        correct_answers = sum(1 for r in result.question_results if r['is_correct'])
        print(f"  Correct answers: {correct_answers}/{len(result.question_results)}")
        print()
    
    # Step 7: Save detailed analysis
    print("Step 7: Saving detailed analysis...")
    save_detailed_analysis(results, "detailed_analysis.json")
    
    print("\n=== DEMO COMPLETED ===")
    print("Files generated:")
    print("  - teacher_template.json: Answer key template")
    print("  - comprehensive_grading_report.json: Summary report")
    print("  - detailed_analysis.json: Detailed analysis")
    
    return results, report

def save_detailed_analysis(results, output_path: str):
    """Save detailed analysis of grading results"""
    analysis = {
        'question_analysis': {},
        'student_performance': {},
        'common_errors': {},
        'recommendations': []
    }
    
    # Analyze question performance
    if results:
        first_result = results[0]
        for question_result in first_result.question_results:
            q_id = question_result['question_id']
            analysis['question_analysis'][q_id] = {
                'question_text': question_result.get('question_text', ''),
                'expected_answer': question_result['expected_answer'],
                'correct_count': 0,
                'total_attempts': len(results),
                'average_score': 0.0,
                'common_student_answers': []
            }
    
    # Collect statistics
    for result in results:
        for question_result in result.question_results:
            q_id = question_result['question_id']
            if q_id in analysis['question_analysis']:
                analysis['question_analysis'][q_id]['correct_count'] += (1 if question_result['is_correct'] else 0)
                analysis['question_analysis'][q_id]['average_score'] += question_result['points_earned']
                analysis['question_analysis'][q_id]['common_student_answers'].append(question_result['student_answer'])
    
    # Calculate averages
    for q_id in analysis['question_analysis']:
        q_analysis = analysis['question_analysis'][q_id]
        q_analysis['average_score'] /= len(results)
        q_analysis['accuracy'] = q_analysis['correct_count'] / q_analysis['total_attempts']
    
    # Generate recommendations
    low_performing_questions = [
        q_id for q_id, q_analysis in analysis['question_analysis'].items()
        if q_analysis['accuracy'] < 0.5
    ]
    
    if low_performing_questions:
        analysis['recommendations'].append(
            f"Questions with low accuracy (<50%): {', '.join(low_performing_questions)}"
        )
    
    # Save analysis
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Detailed analysis saved to {output_path}")

def demo_single_student():
    """Demo grading a single student's homework"""
    print("\n=== SINGLE STUDENT DEMO ===")
    
    # Load a single student's OCR result (hw_2 is a student homework)
    student_file = "output/hw_2_res.json"
    if not Path(student_file).exists():
        print(f"Student file {student_file} not found")
        return
    
    # Initialize grader
    grader = HomeworkGradingSystem()
    
    # Load and grade
    with open(student_file, 'r', encoding='utf-8') as f:
        ocr_result = json.load(f)
    
    result = grader.grade_homework("hw_2", ocr_result)
    
    # Display detailed results
    print(f"\nStudent: {result.student_id}")
    print(f"Total Score: {result.total_score:.1f}/{result.max_score:.1f} ({result.overall_accuracy:.1%})")
    print(f"Feedback: {', '.join(result.feedback)}")
    
    print("\nQuestion-by-question breakdown:")
    for q_result in result.question_results:
        status = "✓" if q_result['is_correct'] else "✗"
        print(f"  {status} {q_result['question_id']}: {q_result['student_answer']} "
              f"(Expected: {q_result['expected_answer']}) - {q_result['points_earned']:.1f}/{q_result['max_points']:.1f} points")
        if q_result['feedback']:
            print(f"    Feedback: {', '.join(q_result['feedback'])}")

if __name__ == "__main__":
    # Run complete workflow demo
    results, report = demo_complete_workflow()
    
    # Run single student demo
    demo_single_student() 