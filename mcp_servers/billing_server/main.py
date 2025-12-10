import asyncio
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
except ImportError as e:
    print(f"MCP packages not available: {e}", file=sys.stderr)
    sys.exit(1)


@dataclass
class BillRecord:
    kwh: float
    bill: float


class BillTable:
    def __init__(self, records: List[BillRecord]):
        self.records = sorted(records, key=lambda r: r.kwh)
        self.min_kwh = self.records[0].kwh
        self.max_kwh = self.records[-1].kwh
        self.min_bill = min(r.bill for r in self.records)
        self.max_bill = max(r.bill for r in self.records)

    def nearest_by_bill(self, rm: float) -> Optional[BillRecord]:
        if rm < self.min_bill or rm > self.max_bill:
            return None
        return min(self.records, key=lambda r: abs(r.bill - rm))

    def nearest_by_kwh(self, kwh: float) -> Optional[BillRecord]:
        if kwh < self.min_kwh:
             return self.records[0] # Return min if below range (likely minimal bill)
        if kwh > self.max_kwh:
            return None
        return min(self.records, key=lambda r: abs(r.kwh - kwh))


def load_bill_table() -> BillTable:
    base_path = Path(__file__).resolve()
    # Check current directory
    primary = base_path.parent / "bill.json"
    # Check resource directory (standard location)
    fallback = base_path.parents[2] / "resource" / "bill.json"
    
    data_path = primary if primary.exists() else fallback
    
    if not data_path.exists():
        # Fallback for dev environment if paths differ
        # Try to find it relative to current working directory
        cwd_path = Path.cwd() / "resource" / "bill.json"
        if cwd_path.exists():
            data_path = cwd_path
        else:
             print(f"Warning: bill.json not found at {primary}, {fallback}, or {cwd_path}", file=sys.stderr)
             # Proceeding with empty or error? Better to fail fast or empty.
             # We'll let it fail on open if not found, or use dummy if strictly needed.
             pass

    with data_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    records = [BillRecord(kwh=float(item["kwh"]), bill=float(item["bill"])) for item in raw]
    return BillTable(records)


server = Server("billing-mcp-server")
try:
    bill_table = load_bill_table()
except Exception as e:
    print(f"Failed to load bill table: {e}", file=sys.stderr)
    bill_table = BillTable([BillRecord(0,0)])


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="tnb_bill_rm_to_kwh",
            description="Convert RM amount to the nearest kWh usage using bill.json",
            inputSchema={
                "type": "object",
                "properties": {
                    "rm": {"type": "number", "description": "Bill amount in RM"}
                },
                "required": ["rm"]
            },
        ),
        Tool(
            name="tnb_bill_kwh_to_rm",
            description="Convert kWh usage to RM using bill.json",
            inputSchema={
                "type": "object",
                "properties": {
                    "kwh": {"type": "number", "description": "Usage in kWh"}
                },
                "required": ["kwh"]
            },
        ),
        Tool(
            name="calculate_solar_impact",
            description="Calculate solar savings, new payable, and system details based on monthly bill.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rm": {"type": "number", "description": "Monthly TNB Bill in RM"},
                    "morning_usage_percentage": {"type": "number", "description": "Percentage of usage in morning (default 30)", "default": 30},
                    "sunpeak_hour": {"type": "number", "description": "Sun peak hours (default 3.4)", "default": 3.4}
                },
                "required": ["rm"]
            },
        ),
    ]


def out_of_scope_msg() -> str:
    return (
        "out_of_scope: value outside bill.json range "
        f"(kWh {bill_table.min_kwh}–{bill_table.max_kwh}, RM {bill_table.min_bill}–{bill_table.max_bill})"
    )


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    if name == "tnb_bill_rm_to_kwh":
        rm = float(arguments["rm"])
        record = bill_table.nearest_by_bill(rm)
        if record is None:
            return [TextContent(type="text", text=out_of_scope_msg())]
        return [
            TextContent(
                type="text",
                text=(
                    f"RM {rm:.2f} maps to {record.kwh} kWh "
                    f"(nearest bill entry RM {record.bill:.2f})"
                ),
            )
        ]

    if name == "tnb_bill_kwh_to_rm":
        kwh = float(arguments["kwh"])
        record = bill_table.nearest_by_kwh(kwh)
        if record is None:
            return [TextContent(type="text", text=out_of_scope_msg())]
        return [
            TextContent(
                type="text",
                text=(
                    f"{record.kwh} kWh maps to RM {record.bill:.2f} "
                    f"(nearest to requested {kwh} kWh)"
                ),
            )
        ]
        
    if name == "calculate_solar_impact":
        input_rm = float(arguments["rm"])
        morning_usage_pct = float(arguments.get("morning_usage_percentage", 30))
        sunpeak_hour = float(arguments.get("sunpeak_hour", 3.4))
        panel_rating = 0.62
        
        # 1. Convert RM to Total Usage (kWh)
        record = bill_table.nearest_by_bill(input_rm)
        if record is None:
             return [TextContent(type="text", text=out_of_scope_msg())]
        total_usage = record.kwh
        
        # 2. Calculate Panel Qty
        # math = total_usage / 30 / 3.4 / 0.62 = PanelQty
        panel_qty = total_usage / 30.0 / sunpeak_hour / panel_rating
        
        # 3. Calculate After Solar Usage
        # new TNB Bill = total_usage - 30% (default)
        morning_ratio = morning_usage_pct / 100.0
        after_solar_usage = total_usage * (1.0 - morning_ratio)
        
        # 4. Get After Solar RM
        after_solar_record = bill_table.nearest_by_kwh(after_solar_usage)
        if after_solar_record is None:
             if after_solar_usage < bill_table.min_kwh:
                 after_solar_record = bill_table.records[0] # Min bill
             else:
                 return [TextContent(type="text", text=f"Error: Calculated after-solar usage {after_solar_usage:.2f} kWh is out of bill.json range.")]
        
        after_solar_rm = after_solar_record.bill
        
        # 5. Bill Reduction
        bill_reduction_rm = input_rm - after_solar_rm
        
        # 6. Solar Generation & Export
        # Total_Solar_generation = 0.62 * 3.4 * PanelQty * 30 (Monthly)
        total_solar_generation_daily = panel_rating * sunpeak_hour * panel_qty
        total_solar_generation_monthly = total_solar_generation_daily * 30.0
        
        # Un-used solar (Export)
        # Export = Total_Generation - (Morning_Ratio * Total_Usage)
        consumed_solar = total_usage * morning_ratio
        export_generation = total_solar_generation_monthly - consumed_solar
        
        # 7. Export Income
        # Export_Generation * 0.2
        export_income = export_generation * 0.20
        
        # 8. Total Saving
        total_saving = export_income + bill_reduction_rm
        
        # 9. New Payable
        new_payable = input_rm - total_saving
        
        output_text = (
            f"Solar System Impact Analysis:\n"
            f"-------------------------------\n"
            f"Input Bill: RM {input_rm:.2f} (approx. {total_usage:.2f} kWh)\n"
            f"System Size: {panel_qty:.2f} Panels (Ref: {panel_qty * panel_rating:.2f} kWp)\n"
            f"\n"
            f"Financials:\n"
            f"1. Bill Reduction: RM {bill_reduction_rm:.2f}\n"
            f"   (New Bill: RM {after_solar_rm:.2f} for {after_solar_usage:.2f} kWh)\n"
            f"2. Export Income: RM {export_income:.2f}\n"
            f"   (Exported: {export_generation:.2f} kWh)\n"
            f"\n"
            f"Total Monthly Saving: RM {total_saving:.2f}\n"
            f"New Net Payable: RM {new_payable:.2f}\n"
        )
        
        return [TextContent(type="text", text=output_text)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
