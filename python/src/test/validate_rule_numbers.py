import json

class ValidateRuleNumbers:
    def __init__(self, file_path, ignored_rules=None):
        """Initializes the class with the path to the JSON file and a list of ignored rules."""
        self.file_path = file_path
        self.data = self.load_data()
        self.ignored_rules = ignored_rules or []  # List of rules to ignore

    def load_data(self):
        """Loads the JSON data from the file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"The file {self.file_path} was not found.")
            return None
        except json.JSONDecodeError:
            print(f"The file {self.file_path} contains invalid JSON.")
            return None

    def check_rule_numbers(self, start_rule, end_rule):
        """Checks if all rule numbers are sequential and there are no gaps."""
        if not self.data:
            print("No data to check.")
            return

        # List of all existing rule numbers
        existing_rule_numbers = []

        # Collecting rule numbers from all sections
        for section in self.data:
            for rule in section.get("section_rules", []):
                rule_number = rule.get("rule_number", None)
                if rule_number:
                    existing_rule_numbers.append(int(rule_number))  # Store rule number as an integer

        # Sort the list of existing rule numbers
        existing_rule_numbers.sort()

        missing_rules = []

        # Check for missing rules
        prev_rule_number = start_rule
        for rule_number in existing_rule_numbers:
            # If the rule is in the ignored list, skip it
            if rule_number in self.ignored_rules:
                continue

            # Identify missing rules
            while prev_rule_number < rule_number:
                if prev_rule_number not in self.ignored_rules:  # If the missing rule is not in ignored rules
                    missing_rules.append(prev_rule_number)  # Add the missing rule
                prev_rule_number += 1

            prev_rule_number = rule_number + 1  # The next rule should be the current rule number + 1

        # Check if any rules are missing
        if missing_rules:
            print(f"Missing rules: {missing_rules}")
        else:
            print(f"All rules between {start_rule} and {end_rule} are present.")

# Example usage:
file_path = "../data/json/rules/rules.json"  # Adjust the path to your JSON file
# Generate ignored rules
ignored_rules = list(range(88, 100)) + list(range(103, 200))
rule_checker = ValidateRuleNumbers(file_path, ignored_rules)

# Start and end rule numbers for the check
start_rule = 1
end_rule = 202
rule_checker.check_rule_numbers(start_rule, end_rule)
