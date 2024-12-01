import json
import re


def extract_longest_json(text):
    try:
        # Find all potential JSON strings (enclosed in curly braces)
        json_pattern = r"{[^{}]*(?:{[^{}]*}[^{}]*)*}"
        matches = re.finditer(json_pattern, text)

        # Store valid JSON strings and their lengths
        valid_jsons = []

        for match in matches:
            potential_json = match.group()
            try:
                # Try to parse the string as JSON
                parsed = json.loads(potential_json)
                valid_jsons.append((potential_json, len(potential_json)))
            except json.JSONDecodeError:
                continue

        # Return the longest valid JSON string, or None if none found
        if valid_jsons:
            return max(valid_jsons, key=lambda x: x[1])[0]
        return None

    except Exception as e:
        print(f"Error: {e}")
        return None
