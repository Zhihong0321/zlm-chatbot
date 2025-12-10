import sys
import os
from pathlib import Path

# Add the server directory to path so we can import main
server_dir = Path("e:/oneapi/mcp_servers/billing_server_v2")
sys.path.append(str(server_dir))

# Mock the current working directory or ensure file paths work
# The script checks multiple locations, so it should find resource/bill.json from e:\oneapi\resource\bill.json
# if we run from e:\oneapi
os.chdir("e:/oneapi")

try:
    import main as billing_mcp
except ImportError as e:
    print(f"Error importing billing mcp: {e}")
    sys.exit(1)

def test_calculation():
    input_rm = 600.0
    
    print(f"Testing Solar Impact for RM {input_rm}")
    
    # Reload bill table just in case
    try:
        billing_mcp.bill_table = billing_mcp.load_bill_table()
        print(f"Bill table loaded. Range: {billing_mcp.bill_table.min_bill} - {billing_mcp.bill_table.max_bill} RM")
    except Exception as e:
        print(f"Failed to load bill table: {e}")
        return

    # Call the logic directly
    # format_solar_impact(input_rm: float, morning_usage_pct: float, sunpeak_hour: float)
    result = billing_mcp.format_solar_impact(input_rm, 30, 3.4)
    print("\n--- Result from MCP Logic ---")
    print(result)

if __name__ == "__main__":
    test_calculation()
