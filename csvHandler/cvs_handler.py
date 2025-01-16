import csv
import os
from datetime import datetime


class CsvFileGenerator:
    def __init__(self, storage_directory="csv_files"):
        self.storage_directory = storage_directory

        # Ensure the storage directory exists
        if not os.path.exists(self.storage_directory):
            os.makedirs(self.storage_directory)

    def generate_csv(self, header=None):
        """Generates a CSV file with a timestamp-based filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"data_{timestamp}.csv"
        file_path = os.path.join(self.storage_directory, file_name)

        data = [
            ["Name", "Age", "City"],
            ["Alice", 30, "New York"],
            ["Bob", 25, "Los Angeles"],
            ["Charlie", 35, "Chicago"]
        ]


        # Open the file in write mode and create a CSV writer object
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write the header if provided
            if header:
                writer.writerow(header)

            # Write the data rows
            writer.writerows(data)

        print(f"CSV file '{file_name}' created successfully at '{file_path}'")
        return file_path