import requests
import json

EMAILS_FILE = "emails.json"
OLLAMA_URL = "http://172.18.0.1:11434/api/chat"
MODEL_NAME = "mistral"  # Updated to use llama2

# Load emails from JSON file
def load_emails(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
        category_data = data.get("emails", [])
    return data.get("value", [])  # Extracts the list of emails

# Function to analyze an email with Ollama
def analyze_email(email):
    prompt = f"""
    Categorize the following email and analyze its emotion.

    Email Subject: {email["subject"]}
    Sender: {email["sender"]["emailAddress"]["name"]} ({email["sender"]["emailAddress"]["address"]})
    Received: {email["receivedDateTime"]}
    Email Preview: {email["bodyPreview"]}

    Provide the result in strict JSON format with exactly two keys from these options:
    - "category": work, personal, spam, newsletter, notification
    - "emotion": happy, neutral, urgent, frustrated, excited
    
    Example Output:
    ```json
    {{"category": "work", "emotion": "neutral"}}
    ```
    """

    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=data)
        response.raise_for_status()  # Raise an error for bad status codes
        response_json = response.json()

        # Extract the content from the response
        analysis_result = json.loads(response_json["message"]["content"])
        return analysis_result
    except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError) as e:
        print(f"Error analyzing email: {e}")
        return {"category": "unknown", "emotion": "unknown"}

# Main execution
if __name__ == "__main__":
    emails = load_emails(EMAILS_FILE)
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
