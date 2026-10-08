import os
import json
from PIL import Image
import google.generativeai as genai
load_dotenv()
# Setup Google Gemini Connection Environment
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_gemini_recommendations(category: str, budget: float, preferences: str, image_bytes: bytes = None) -> dict:
    \"\"\"
    Interfaces directly with Google Generative AI to generate structured 
    budget allocation JSON logs mapping matching consumer platforms.
    \"\"\"
    if not api_key:
        return {
            "error": "Gemini API key is missing. Please configure your GEMINI_API_KEY environment variable.",
            "total_budget": budget,
            "breakdown": [],
            "suggestions": ["Add a valid Google AI studio key to unblock dynamic real-time generations."]
        }
        
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f\"\"\"
        You are PocketSmart AI, an advanced generative budget coordinator. Analyze data context:
        Category Target Domain: {category}
        Assigned Budget Allocation Limit: INR {budget}
        User Context Guidelines: {preferences}
        
        Return exclusively a valid raw JSON dictionary object matching this schema exactly:
        {{
            "total_budget": {budget},
            "category_summary": "High-level modular assessment summary sentence context.",
            "breakdown": [
                {{"item": "Specific item or provisioning name", "cost": 1000, "platform": "Amazon, Flipkart, Swiggy, Zomato, OYO, or Local Markets", "reason": "Justification reasoning text"}}
            ],
            "suggestions": ["Optimization workflow tip entries"]
        }}
        Do not include markdown triple-backtick wrapping labels or conversational headers outside the raw JSON object string.
        \"\"\"
        
        if image_bytes and category.lower() == "jewelry":
            import io
            image = Image.open(io.BytesIO(image_bytes))
            response = model.generate_content([prompt, image])
        else:
            response = model.generate_content(prompt)
            
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())
    except Exception as e:
        return {
            "error": f"LLM parser exception occurred: {str(e)}",
            "total_budget": budget,
            "breakdown": [{"item": "Emergency Fallback Provision", "cost": budget, "platform": "Local Market", "reason": "System error backup plan"}],
            "suggestions": ["Verify your input variables or network connectivity rules and resubmit."]
        }
