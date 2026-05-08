import google.generativeai as genai
from app.core.config import settings

def generate_narrative(hex_id: str, old_tier: str, new_tier: str, signals: list[dict]) -> str:
    if not settings.GEMINI_API_KEY:
        return f"Risk escalated from {old_tier} to {new_tier}. Multiple critical signals detected."
        
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        signal_summary = ", ".join([f"{s['count']} {s['signal_type']} ({s['sector']})" for s in signals[:5]])
        
        prompt = f"""
        A city area (Hex ID: {hex_id}) has escalated in risk from {old_tier} to {new_tier}.
        Contributing signals: {signal_summary}.
        Generate a concise, 2-sentence analyst briefing for a city safety coordinator explaining this escalation.
        Do not use introductory phrases, just provide the briefing.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating narrative: {e}")
        return f"Risk escalated from {old_tier} to {new_tier} due to concentration of cross-sector incidents."
