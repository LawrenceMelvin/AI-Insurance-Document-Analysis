"""
promt lable
good = 1
bad = 0
The idea of the dataset is to check the 101 of insurance documents first
1. Co-payment
2. Room Rent restriction
3. Disease specific waiting period
4. Disease wise limit
5. Pre-existing disease waiting period
6. Pre and Post hospitalization
7. Restoration
8. Day Care Treatment
9. Maternity
10. No Claim bonus
11. Free Health Checkup
12. Doctor Consultation
"""

import os
import pandas as pd

def create_dataset(input_dir, output_file):
    # Initialize an empty list to store the data
    data = []

    # Loop through all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Classifying logic

                # For demonstration, let's assume we classify based on the presence of certain keywords
                label = 1 if "good" in content else 0  # Replace with your actual classification logic
                data.append({'filename': filename, 'content': content, 'label': label})

    # Create a DataFrame from the data list
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(output_file, index=False)