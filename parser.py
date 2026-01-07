"""
HTML Parser Module
Extracts studentCore and manualOverall JSON data from the TCD Technical HTML report.
"""

import re
import json
from pathlib import Path


def extract_json_object(content: str, var_name: str) -> dict:
    """
    Extract a JavaScript object assigned to a variable from HTML content.
    
    Args:
        content: The HTML file content as a string
        var_name: The JavaScript variable name (e.g., 'studentCore', 'manualOverall')
    
    Returns:
        Parsed dictionary from the JSON object
    """
    # Pattern to find: const varName = { ... }
    # We need to handle nested braces properly
    pattern = rf'const\s+{var_name}\s*=\s*(\{{)'
    match = re.search(pattern, content)
    
    if not match:
        raise ValueError(f"Could not find variable '{var_name}' in content")
    
    start_pos = match.start(1)
    
    # Find the matching closing brace
    brace_count = 0
    end_pos = start_pos
    
    for i, char in enumerate(content[start_pos:], start=start_pos):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1
                break
    
    json_str = content[start_pos:end_pos]
    
    # Parse as JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON for '{var_name}': {e}")


def clean_score(value) -> float:
    """
    Clean a score value, handling various formats.
    
    Args:
        value: The raw score value (can be int, float, str like "-" or "97(Reattempt)")
    
    Returns:
        Cleaned float value (0.0 for missing/invalid values)
    """
    if value is None:
        return 0.0
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Handle "-" or empty
        if value.strip() in ["-", "", "NA", "N/A"]:
            return 0.0
        
        # Handle annotations like "97(Reattempt)" - extract the number
        numeric_match = re.match(r'^([\d.]+)', value.strip())
        if numeric_match:
            return float(numeric_match.group(1))
        
        return 0.0
    
    return 0.0


def parse_html_file(file_path: str) -> list[dict]:
    """
    Parse the TCD Technical HTML file and extract student data.
    
    Args:
        file_path: Path to the HTML file
    
    Returns:
        List of dictionaries with student data including Name, RollNo, scores, total, rank
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read the HTML content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return parse_html_file_content(content)


def parse_html_file_content(content: str) -> list[dict]:
    """
    Parse HTML content string and extract student data.
    
    Args:
        content: The HTML file content as a string
    
    Returns:
        List of dictionaries with student data including Name, RollNo, scores, total, rank
    """
    # Extract the two JSON objects we need
    student_core = extract_json_object(content, 'studentCore')
    manual_overall = extract_json_object(content, 'manualOverall')
    
    # Merge data and build records
    records = []
    
    for roll_no, core_data in student_core.items():
        # Get overall scores if available
        overall_data = manual_overall.get(roll_no, {})
        
        record = {
            'Name': core_data.get('Name', 'Unknown'),
            'RollNo': core_data.get('regdNo', roll_no),
            'OverallPseudocode': clean_score(overall_data.get('OverallPseudocode', 0)),
            'OverallCoding': clean_score(overall_data.get('OverallCoding', 0)),
            'OverallDailyTest': clean_score(overall_data.get('OverallDaily', 0)),
        }
        
        # Calculate total
        record['Total'] = (
            record['OverallPseudocode'] + 
            record['OverallCoding'] + 
            record['OverallDailyTest']
        )
        
        records.append(record)
    
    # Sort by total descending and assign ranks
    records.sort(key=lambda x: x['Total'], reverse=True)
    
    # Assign ranks (handle ties with min method)
    current_rank = 1
    for i, record in enumerate(records):
        if i > 0 and record['Total'] < records[i-1]['Total']:
            current_rank = i + 1
        record['Rank'] = current_rank
    
    return records


if __name__ == "__main__":
    # Test the parser
    import sys
    
    if len(sys.argv) > 1:
        html_path = sys.argv[1]
    else:
        html_path = r"..\TCD_Technical_GITAM_20 Dec 2025 to 6 Jan 2026.HTML"
    
    try:
        data = parse_html_file(html_path)
        print(f"Parsed {len(data)} student records")
        print("\nTop 5 students:")
        for record in data[:5]:
            print(f"  {record['Rank']}. {record['Name']} ({record['RollNo']}) - Total: {record['Total']}")
    except Exception as e:
        print(f"Error: {e}")
