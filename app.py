# app.py
import os

from insurance_analyzer import InsuranceDocumentAnalyzer


def main():
    print("==== Insurance Document Analyzer ====")

    file_path = input("Enter the path to your insurance document: ")

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    analyzer = InsuranceDocumentAnalyzer()

    try:
        results = analyzer.analyze_insurance_document(file_path)

        output_file = f"{os.path.basename(file_path)}_analysis.txt"
        analyzer.save_results_to_file(results, output_file)

        print(f"\nAnalysis complete! Results saved to {output_file}")

        # Print a quick summary
        print("\n=== Quick Summary ===")
        if results['summary']['document_summary']['pros'][0] != "No text extracted from document":
            print("\nPROS:")
            for pro in results['summary']['document_summary']['pros'][:3]:
                print(f"• {pro}")

            print("\nCONS:")
            for con in results['summary']['document_summary']['cons'][:3]:
                print(f"• {con}")

            print("\nHIDDEN DETAILS:")
            for detail in results['summary']['document_summary']['hidden_details'][:3]:
                print(f"• {detail}")
        else:
            print("\nNo valid content could be extracted from the document.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()