# insurance_analyzer.py

import os
import re
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
import spacy
from transformers import pipeline
from pypdf import PdfReader
import pytesseract
from PIL import Image

# Download necessary NLTK data
nltk.download('punkt')


class InsuranceDocumentAnalyzer:
    def __init__(self):
        # Load NLP models
        self.nlp = spacy.load("en_core_web_sm")
        self.sentiment_analyzer = pipeline("sentiment-analysis")

        # Important terms to look for in insurance docs
        self.key_terms = {
            'exclusions': ['exclusion', 'not covered', 'excluded', 'except', 'excluding'],
            'limitations': ['limit', 'maximum', 'up to', 'no more than', 'ceiling'],
            'requirements': ['must', 'required', 'shall', 'need to', 'obligation'],
            'deadlines': ['within', 'deadline', 'by', 'no later than', 'time limit'],
            'fees': ['fee', 'charge', 'payment', 'premium', 'deductible', 'copay', 'coinsurance'],
            'coverage': ['cover', 'coverage', 'protect', 'benefit', 'reimburse', 'pay for'],
            'conditions': ['condition', 'if', 'when', 'provided that', 'subject to']
        }

        # Regular expressions for monetary values and percentages
        self.money_pattern = r'\$\d+(?:,\d+)*(?:\.\d+)?|\d+(?:,\d+)*(?:\.\d+)?\s?(?:dollars|USD)'
        self.percentage_pattern = r'\d+(?:\.\d+)?%|\d+(?:\.\d+)?\spercent'

    def extract_text_from_pdf(self, pdf_path, password=None):
        """Extract text content from a PDF file"""
        text = ""
        try:
            reader = PdfReader(pdf_path, password=password)
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            if "encryption" in str(e).lower() or "password" in str(e).lower():
                print(f"This PDF appears to be encrypted/password-protected: {e}")
                if password is None:
                    pwd = input("Enter PDF password (press Enter if none): ")
                    if pwd:
                        return self.extract_text_from_pdf(pdf_path, password=pwd)
            else:
                print(f"Error extracting text from PDF: {e}")
            return text

    def extract_text_from_image(self, image_path):
        """Extract text content from an image using OCR"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""

    # Update the extract_text method in insurance_analyzer.py
    def extract_text(self, file_path):
        """Extract text from different file types"""
        _, file_extension = os.path.splitext(file_path)

        # If no extension is provided, try to determine file type or default to PDF
        if file_extension == '':
            print("No file extension detected, attempting to process as PDF...")
            try:
                return self.extract_text_from_pdf(file_path)
            except Exception as e:
                print(f"Failed to process as PDF: {e}")
                print("Trying as plain text...")
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        return file.read()
                except Exception as e:
                    print(f"Failed to process as text: {e}")
                    return ""

        elif file_extension.lower() in ['.pdf']:
            return self.extract_text_from_pdf(file_path)
        elif file_extension.lower() in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            return self.extract_text_from_image(file_path)
        elif file_extension.lower() in ['.txt', '.doc', '.docx']:
            # For text files, simply read them
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            print(f"Unsupported file format: {file_extension}")
            return ""

    def analyze_document(self, text):
        """Analyze the insurance document text and extract key information"""
        # Break text into sentences for analysis
        sentences = sent_tokenize(text)

        # Initialize result dictionaries
        findings = {
            'exclusions': [],
            'limitations': [],
            'requirements': [],
            'deadlines': [],
            'fees': [],
            'coverage': [],
            'conditions': []
        }

        monetary_values = []
        percentages = []
        dates = []

        # Process each sentence
        for sentence in sentences:
            # Skip very short sentences
            if len(sentence.split()) < 3:
                continue

            # Check for key terms in each category
            for category, terms in self.key_terms.items():
                for term in terms:
                    if re.search(r'\b' + term + r'\b', sentence.lower()):
                        findings[category].append(sentence.strip())
                        break

            # Extract monetary values
            money_matches = re.findall(self.money_pattern, sentence)
            if money_matches:
                for match in money_matches:
                    monetary_values.append({
                        'value': match,
                        'context': sentence.strip()
                    })

            # Extract percentages
            percentage_matches = re.findall(self.percentage_pattern, sentence)
            if percentage_matches:
                for match in percentage_matches:
                    percentages.append({
                        'value': match,
                        'context': sentence.strip()
                    })

            # Extract dates using spaCy
            doc = self.nlp(sentence)
            for ent in doc.ents:
                if ent.label_ == 'DATE':
                    dates.append({
                        'date': ent.text,
                        'context': sentence.strip()
                    })

        # Remove duplicates while preserving order
        for category in findings:
            findings[category] = list(dict.fromkeys(findings[category]))

        return {
            'findings': findings,
            'monetary_values': monetary_values,
            'percentages': percentages,
            'dates': dates
        }

    def classify_pros_cons(self, text):
        """Classify key points as pros or cons for the policyholder"""
        sentences = sent_tokenize(text)
        pros = []
        cons = []
        neutral = []
        hidden_details = []

        for sentence in sentences:
            # Skip very short sentences
            if len(sentence.split()) < 5:
                continue

            # Use sentiment analysis to help classify
            sentiment = self.sentiment_analyzer(sentence)[0]

            # Check for specific indicators of pros/cons/hidden details
            is_pro = any(
                term in sentence.lower() for term in ['benefit', 'coverage', 'included', 'advantage', 'free', 'bonus'])
            is_con = any(term in sentence.lower() for term in
                         ['exclusion', 'not covered', 'limitation', 'restrict', 'charge', 'fee','co-payment'])
            is_hidden = any(
                term in sentence.lower() for term in ['fine print', 'conditions apply', 'subject to', 'restrictions'])

            # Small text often contains hidden details
            if len(sentence) < 50 and any(term in sentence.lower() for term in ['*', '†', 'note:', 'disclaimer']):
                is_hidden = True

            # Classify based on combined factors
            if is_pro and sentiment['label'] == 'POSITIVE':
                pros.append(sentence.strip())
            elif is_con or sentiment['label'] == 'NEGATIVE':
                cons.append(sentence.strip())
            elif is_hidden:
                hidden_details.append(sentence.strip())
            else:
                neutral.append(sentence.strip())

        # Remove duplicates
        pros = list(dict.fromkeys(pros))
        cons = list(dict.fromkeys(cons))
        hidden_details = list(dict.fromkeys(hidden_details))

        return {
            'pros': pros,
            'cons': cons,
            'hidden_details': hidden_details
        }

    def generate_summary(self, analysis_results, pros_cons):
        """Generate a comprehensive summary of the insurance document"""
        summary = {
            'document_summary': {
                'pros': pros_cons['pros'][:5],  # Top 5 pros
                'cons': pros_cons['cons'][:5],  # Top 5 cons
                'hidden_details': pros_cons['hidden_details'][:5],  # Top 5 hidden details
                'key_exclusions': analysis_results['findings']['exclusions'][:3],
                'key_limitations': analysis_results['findings']['limitations'][:3],
                'important_requirements': analysis_results['findings']['requirements'][:3],
                'critical_deadlines': analysis_results['findings']['deadlines'][:3],
                'significant_fees': [item['context'] for item in analysis_results['monetary_values'][:3]],
                'coverage_highlights': analysis_results['findings']['coverage'][:3]
            }
        }

        return summary

    def analyze_insurance_document(self, file_path):
        """Main function to analyze an insurance document"""
        # Extract text from the document
        text = self.extract_text(file_path)

        if not text:
            print("ERROR: No text could be extracted from the document.")
            # Return a valid but empty result structure to avoid KeyError
            return {
                'summary': {
                    'document_summary': {
                        'pros': ["No text extracted from document"],
                        'cons': ["No text extracted from document"],
                        'hidden_details': ["No text extracted from document"],
                        'key_exclusions': [],
                        'key_limitations': [],
                        'important_requirements': [],
                        'critical_deadlines': [],
                        'significant_fees': [],
                        'coverage_highlights': []
                    }
                },
                'detailed_analysis': {
                    'findings': {k: [] for k in self.key_terms.keys()},
                    'monetary_values': [],
                    'percentages': [],
                    'dates': []
                },
                'pros_cons_analysis': {
                    'pros': [],
                    'cons': [],
                    'hidden_details': []
                }
            }
        # Analyze the document text
        analysis_results = self.analyze_document(text)

        # Classify pros and cons
        pros_cons = self.classify_pros_cons(text)

        # Generate summary
        summary = self.generate_summary(analysis_results, pros_cons)

        # Combine all results
        results = {
            'summary': summary,
            'detailed_analysis': analysis_results,
            'pros_cons_analysis': pros_cons
        }

        return results

    def save_results_to_file(self, results, output_file):
        """Save analysis results to a formatted text file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== INSURANCE DOCUMENT ANALYSIS ===\n\n")

            # Write summary
            f.write("== SUMMARY ==\n\n")

            f.write("= PROS =\n")
            for item in results['summary']['document_summary']['pros']:
                f.write(f"• {item}\n")
            f.write("\n")

            f.write("= CONS =\n")
            for item in results['summary']['document_summary']['cons']:
                f.write(f"• {item}\n")
            f.write("\n")

            f.write("= HIDDEN DETAILS =\n")
            for item in results['summary']['document_summary']['hidden_details']:
                f.write(f"• {item}\n")
            f.write("\n")

            f.write("= KEY EXCLUSIONS =\n")
            for item in results['summary']['document_summary']['key_exclusions']:
                f.write(f"• {item}\n")
            f.write("\n")

            # Add more sections as needed

            f.write("== DETAILED ANALYSIS ==\n\n")
            # Write detailed findings here

            return output_file