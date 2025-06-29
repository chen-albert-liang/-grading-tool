# Automated Homework Grading System

An intelligent system that leverages PaddleOCR to automatically grade handwritten homework assignments against a teacher's answer key.

## 🎯 Overview

This system processes scanned homework images using OCR (Optical Character Recognition) and automatically grades student answers by comparing them against a teacher's answer key. It's designed for mathematical homework with various answer types including numbers, formulas, and text.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Teacher's     │    │   Student's     │    │   Grading       │
│   Answer Key    │    │   Homework      │    │   System        │
│   (homework1)   │    │   (homework2-8) │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Template       │    │  OCR Processing │    │  Answer         │
│  Builder        │    │  (PaddleOCR)    │    │  Extraction     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Answer Key     │    │  Extracted      │    │  Grading        │
│  Template       │    │  Text & Scores  │    │  Algorithm      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  Grading Results &      │
                    │  Reports                │
                    └─────────────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run OCR on Homework Images

```bash
python pp_grading_ocr_v5.py
```

This will process all homework images in the `hw/` directory and generate JSON files in the `output/` directory.

### 3. Run the Automated Grading System

```bash
python demo_grading_system.py
```

This will:
- Extract the answer key template from `hw_1.png` (teacher's answer key)
- Grade `hw_2.png` and `hw_3.png` (student homework)
- Generate comprehensive reports

## 📁 File Structure

```
grading_tool/
├── hw/                        # Input homework images
│   ├── hw_1.png              # Teacher's answer key
│   ├── hw_2.png              # Student 1 homework
│   ├── hw_3.png              # Student 2 homework
│   └── answer_key.png        # Additional answer key (if needed)
├── output/                    # OCR results
│   ├── hw_1_res.json         # Teacher's OCR result
│   ├── hw_2_res.json         # Student 1's OCR result
│   ├── hw_3_res.json         # Student 2's OCR result
│   └── *_ocr_res_img.png     # Visualization images
├── automated_grading_system.py  # Main grading system
├── template_builder.py          # Template extraction
├── demo_grading_system.py       # Demo script
├── pp_grading_ocr_v5.py         # OCR processing
└── requirements.txt             # Dependencies
```

## 🔧 Core Components

### 1. Template Builder (`template_builder.py`)
- Extracts answer key template from teacher's homework
- Identifies question sections and expected answers
- Determines answer types (numeric, formula, text)
- Estimates point values

### 2. Automated Grading System (`automated_grading_system.py`)
- Processes OCR results from student homework
- Extracts and aligns student answers with questions
- Applies different grading algorithms based on answer type
- Generates detailed feedback and scores

### 3. Grading Algorithms

#### Numeric Answers
- Extracts numbers using regex
- Compares with tolerance (default: ±0.1)
- Handles decimal values

#### Formula Answers
- Normalizes mathematical expressions
- Uses sequence similarity matching
- Supports partial credit (80%+ = full, 60%+ = half)

#### Text Answers
- Case-insensitive similarity matching
- Handles Chinese text
- Configurable similarity thresholds

## 📊 Output Reports

### 1. Comprehensive Grading Report (`comprehensive_grading_report.json`)
```json
{
  "summary": {
    "total_students": 7,
    "average_score": 45.2,
    "average_accuracy": 0.75,
    "highest_score": 52.0,
    "lowest_score": 38.0
  },
  "student_results": [...]
}
```

### 2. Detailed Analysis (`detailed_analysis.json`)
- Question-by-question performance analysis
- Common student errors
- Recommendations for improvement

### 3. Teacher Template (`teacher_template.json`)
- Structured answer key for future use
- Configurable scoring criteria

## 🎛️ Configuration

### Answer Types
- `numeric`: Numbers with tolerance
- `formula`: Mathematical expressions
- `text`: Text-based answers
- `multiple_choice`: Multiple choice questions

### Scoring Parameters
- `tolerance`: For numeric answers (default: 0.1)
- `partial_credit`: Enable/disable partial credit
- `similarity_threshold`: For text/formula matching (default: 0.8)

### Point Values
- Basic questions: 2-3 points
- Intermediate questions: 4-5 points
- Advanced questions: 6-8 points

## 🔍 Example Usage

### Single Student Grading
```python
from automated_grading_system import HomeworkGradingSystem

# Initialize grader
grader = HomeworkGradingSystem()

# Load OCR result
with open('output/homework2_res.json', 'r') as f:
    ocr_result = json.load(f)

# Grade homework
result = grader.grade_homework("student_001", ocr_result)

# Display results
print(f"Score: {result.total_score:.1f}/{result.max_score:.1f}")
print(f"Accuracy: {result.overall_accuracy:.1%}")
```

### Batch Grading
```python
# Grade all homework assignments
results = grader.batch_grade("output")

# Generate report
report = grader.generate_report(results, "batch_report.json")
```

## 🎯 Key Features

### ✅ Intelligent Answer Extraction
- Filters out question text from answers
- Identifies handwritten vs printed text
- Handles OCR artifacts and noise

### ✅ Flexible Grading
- Multiple answer type support
- Configurable tolerance and thresholds
- Partial credit system

### ✅ Comprehensive Reporting
- Individual student reports
- Class-wide statistics
- Question performance analysis
- Detailed feedback

### ✅ Scalable Architecture
- Batch processing support
- Template-based approach
- Easy to extend for new question types

## 🔧 Customization

### Adding New Answer Types
```python
def _grade_custom_answer(self, student_answer, expected_question, result):
    # Custom grading logic
    pass
```

### Modifying Scoring Criteria
```python
template = {
    "1.1": Question("1.1", "Question text", "answer", "numeric", 5.0, tolerance=0.05)
}
```

### Adjusting Similarity Thresholds
```python
# In grading methods
if similarity >= 0.9:  # Stricter matching
    result['is_correct'] = True
```

## 🚨 Limitations & Considerations

### OCR Accuracy
- Handwriting quality affects recognition
- Mathematical symbols may be misread
- Chinese characters require good OCR support

### Answer Alignment
- Current system uses simple positional alignment
- Complex layouts may require manual adjustment
- Question numbering must be consistent

### Grading Precision
- Formula grading relies on string similarity
- Context-dependent answers may be challenging
- Partial credit thresholds may need tuning

## 🔮 Future Enhancements

### Planned Features
- [ ] Machine learning-based answer classification
- [ ] Advanced layout analysis
- [ ] Support for diagrams and graphs
- [ ] Integration with learning management systems
- [ ] Real-time grading interface

### Potential Improvements
- [ ] Better handwriting recognition
- [ ] Semantic understanding of answers
- [ ] Adaptive scoring based on difficulty
- [ ] Multi-language support

## 📞 Support

For questions or issues:
1. Check the demo output for error messages
2. Verify OCR results are generated correctly
3. Review template extraction accuracy
4. Adjust grading parameters as needed

## 📄 License

This project is designed for educational use. Please ensure compliance with your institution's policies regarding automated grading systems. 