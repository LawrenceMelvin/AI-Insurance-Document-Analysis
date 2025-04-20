# app.py
from insurance_analyzer import InsuranceDocumentAnalyzer


def main():
    print("==== Insurance Document Analyzer ====")

    file_path = input("Enter the path to your insurance document: ")

    analyzer = InsuranceDocumentAnalyzer()
    results = analyzer.analyze_insurance_document(file_path)

    output_file = f"{file_path.split('/')[-1].split('.')[0]}_analysis.txt"
    analyzer.save_results_to_file(results, output_file)

    print(f"\nAnalysis complete! Results saved to {output_file}")

    # Print a quick summary
    print("\n=== Quick Summary ===")
    print("\nPROS:")
    for pro in results['summary']['document_summary']['pros'][:3]:
        print(f"• {pro}")

    print("\nCONS:")
    for con in results['summary']['document_summary']['cons'][:3]:
        print(f"• {con}")

    print("\nHIDDEN DETAILS:")
    for detail in results['summary']['document_summary']['hidden_details'][:3]:
        print(f"• {detail}")


if __name__ == "__main__":
    main()