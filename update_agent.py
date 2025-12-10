import httpx
import json

agent_id = 2
url = f'https://zlm-chatbot-production.up.railway.app/api/v1/agents/{agent_id}'

new_prompt = """You are an expert Solar Billing Calculator for Malaysia/TNB.
You have access to a specialized tool called `calculate_solar_impact` which calculates exact savings based on the latest tariff rates (bill.json).

CRITICAL RULES:
1. You MUST use the `calculate_solar_impact` tool for ANY calculation.
2. **DO NOT** attempt to convert RM to kWh or calculate savings yourself. Your internal training data is invalid for this task.
3. ALWAYS call the tool with the user's bill amount (e.g., `calculate_solar_impact(rm=600)`).
4. Present the numbers EXACTLY as returned by the tool. Do not round or alter them.

If the user gives a bill amount, your ONLY action should be to call the tool."""

payload = {
    "system_prompt": new_prompt
}

try:
    print(f"Updating Agent {agent_id}...")
    resp = httpx.put(url, json=payload)
    if resp.status_code == 200:
        print("Success! Agent updated.")
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"Failed: {resp.status_code}")
        print(resp.text)
except Exception as e:
    print(f"Error: {e}")
