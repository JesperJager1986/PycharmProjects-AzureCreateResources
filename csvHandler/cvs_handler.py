import csv
import os
import random


class RandomNameGenerator:
    def __init__(self):
        self.first_names = [
            "Alice", "Bob", "Charlie", "David", "Eva", "Frank", "Grace", "Hannah", "Ivy", "Jack",
            "Kara", "Leo", "Mona", "Nina", "Oscar", "Paul", "Quincy", "Rachel", "Sam", "Tina",
            "Ursula", "Victor", "Wendy", "Xander", "Yara", "Zane", "Aiden", "Bella", "Caleb", "Diana",
            "Ethan", "Faith", "Gavin", "Holly", "Isaac", "Jasmine", "Kyle", "Liam", "Megan", "Nathan",
            "Olivia", "Penny", "Quinn", "Ryan", "Sophia", "Travis", "Uriah", "Vera", "Wyatt", "Xena",
            "Yvonne", "Zara"
        ]

        self.last_names = [
            "Anderson", "Baker", "Clark", "Davis", "Evans", "Fox", "Green", "Harris", "Irwin", "Jackson",
            "Kelly", "Lee", "Mitchell", "Norris", "Parker", "Quinn", "Roberts", "Smith", "Taylor", "Williams",
            "Adams", "Bennett", "Carter", "Dixon", "Ellis", "Foster", "Graham", "Hill", "Ingram", "Johnson",
            "King", "Lloyd", "Morgan", "Nelson", "O'Connor", "Price", "Richards", "Scott", "Thompson", "Underwood",
            "Vaughn", "Walker", "Young", "Zimmerman", "Abbott", "Bishop", "Chavez", "Douglas", "Elliott"
        ]

        self.cities = [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego",
            "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus", "Indianapolis", "Charlotte",
            "San Francisco", "Seattle", "Denver", "Washington", "Boston", "El Paso", "Detroit", "Nashville",
            "Portland", "Memphis", "Oklahoma City", "Las Vegas", "Louisville", "Baltimore", "Milwaukee", "Albuquerque",
            "Tucson", "Fresno", "Sacramento", "Kansas City", "Long Beach", "Mesa", "Atlanta", "Colorado Springs",
            "Raleigh", "Omaha", "Miami", "Cleveland", "Tulsa", "Minneapolis", "Wichita", "New Orleans", "Arlington",
            "Bakersfield", "Tampa", "Aurora", "Honolulu", "Anaheim", "Santa Ana", "St. Louis", "Riverside",
            "Corpus Christi"
        ]

    def generate_random_first_name(self) -> str:
        return random.choice(self.first_names)

    def generate_random_last_name(self) -> str:
        return random.choice(self.last_names)

    def generate_random_city(self) -> str:
        return random.choice(self.cities)

class CsvFileGenerator:
    def __init__(self):
        self.storage_directory = "/Users/jesperthoftillemannjaeger/PycharmProjects/PycharmProjects-AzureCreateResources/dummyFolder"
        self.random_generator = RandomNameGenerator()
        # Ensure the storage directory exists
        if not os.path.exists(self.storage_directory):
            os.makedirs(self.storage_directory)

    def generate_csv(self, header=None, file_name = None) -> str:
        """Generates a CSV file with a timestamp-based filename."""

        file_path = os.path.join(self.storage_directory, file_name)

        data = [
            ["Name", "Age", "City"],
            [self.random_generator.generate_random_last_name(), 30, self.random_generator.generate_random_city()],
            [self.random_generator.generate_random_last_name(), 25, self.random_generator.generate_random_city()],
            [self.random_generator.generate_random_last_name(), 35, self.random_generator.generate_random_city()]
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