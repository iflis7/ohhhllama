import requests
import json
import logging
from typing import Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

EMAILS_FILE = "emails.json"
OLLAMA_URL = "http://172.18.0.1:11434/api/chat"
MODEL_NAME = "llama3.2"

# Load emails from JSON file
def load_emails(filename: str) -> List[Dict]:
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            # Adjust based on your emails.json structure
            if "value" in data:
                return data["value"]
            elif "emails" in data:
                return data["emails"]
            else:
                return data  # If structure is flat, return it directly
    except Exception as e:
        logging.error(f"Error loading emails from {filename}: {e}")
        return []

# Function to analyze an email with Ollama
def analyze_email(email: Dict) -> Dict:
    prompt = f"""
    Categorize the following email and analyze its emotion.

    Email Subject: {email["subject"]}
    Sender: {email["sender"]["emailAddress"]["name"]} ({email["sender"]["emailAddress"]["address"]})
    Received: {email["receivedDateTime"]}
    Email Preview: {email["bodyPreview"]}

    Provide the result in strict JSON format with exactly two keys:
    - "category": "work", "personal", "spam", "newsletter", or "notification"
    - "emotion": "happy", "neutral", "urgent", "frustrated", or "excited"
    
    Do not include any additional text or explanations outside of the JSON object.
    Example Output:
    {{"category": "work", "emotion": "neutral"}}
    """

    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=30)
        response.raise_for_status()  # Raise an error for bad status codes
        response_json = response.json()

        # Log the raw response for debugging
        logging.debug(f"Raw Ollama response: {response_json}")

        # Extract content safely
        content = response_json.get("message", {}).get("content", "")
        if not content:
            logging.error("Empty content in Ollama response")
            return {"category": "unknown", "emotion": "unknown"}

        # Try to parse the content as JSON
        try:
            analysis_result = json.loads(content)
            # Validate the structure
            if not all(key in analysis_result for key in ["category", "emotion"]):
                logging.error(f"Invalid JSON structure: {content}")
                return {"category": "unknown", "emotion": "unknown"}
            return analysis_result
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse Ollama response as JSON: {content}, Error: {e}")
            return {"category": "unknown", "emotion": "unknown"}

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error while analyzing email: {e}")
        return {"category": "unknown", "emotion": "unknown"}
    except Exception as e:
        logging.error(f"Unexpected error while analyzing email: {e}")
        return {"category": "unknown", "emotion": "unknown"}

# Main execution
if __name__ == "__main__":
    emails = load_emails(EMAILS_FILE)
    if not emails:
        logging.error("No emails loaded. Exiting.")
        exit(1)

    analyzed_results = []

    for email in emails:
        result = analyze_email(email)
        analyzed_data = {
            "id": email["id"],
            "subject": email["subject"],
            "sender": email["sender"]["emailAddress"]["address"],
            "category": result["category"],
            "emotion": result["emotion"]
        }
        analyzed_results.append(analyzed_data)
        print(json.dumps(analyzed_data, indent=4))

    # Save the results to a JSON file
    with open("email_analysis_results.json", "w", encoding="utf-8") as output_file:
        json.dump(analyzed_results, output_file, indent=4)
    
    print("\nAnalysis complete! Results saved to 'email_analysis_results.json'")