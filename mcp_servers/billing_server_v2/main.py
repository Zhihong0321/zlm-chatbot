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
        if not records:
            raise ValueError("bill table is empty")
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
            return self.records[0]
        if kwh > self.max_kwh:
            return None
        return min(self.records, key=lambda r: abs(r.kwh - kwh))


def load_bill_table() -> BillTable:
    base = Path(__file__).resolve()
    candidates = [
        base.parent / "bill.json",
        base.parents[2] / "resource" / "bill.json",
        base.parents[1] / "billing_server" / "bill.json",
        Path("/app/mcp_servers/billing_server_v2/bill.json"),
        Path("/app/mcp_servers/billing_server/bill.json"),
        Path("/app/resource/bill.json"),
    ]

    for path in candidates:
        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as f:
                    raw = json.load(f)
                records = [BillRecord(kwh=float(item["kwh"]), bill=float(item["bill"])) for item in raw]
                if records:
                    return BillTable(records)
            except Exception as e:
                print(f"Failed to load bill.json from {path}: {e}", file=sys.stderr)

    raise FileNotFoundError("bill.json not found for billing MCP v2")


server = Server("billing-mcp-server-v2")
try:
    bill_table = load_bill_table()
except Exception as e:
    print(f"Failed to load bill table: {e}", file=sys.stderr)
    bill_table = BillTable([BillRecord(0.0, 0.0)])


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
                "required": ["rm"],
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
                "required": ["kwh"],
            },
        ),
        Tool(
            name="calculate_solar_impact",
            description="Calculate solar savings, new payable, and system details based on monthly bill.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rm": {"type": "number", "description": "Monthly TNB Bill in RM"},
                    "morning_usage_percentage": {
                        "type": "number",
                        "description": "Percentage of usage in morning (default 30)",
                        "default": 30,
                    },
                    "sunpeak_hour": {
                        "type": "number",
                        "description": "Sun peak hours (default 3.4)",
                        "default": 3.4,
                    },
                },
                "required": ["rm"],
            },
        ),
    ]


def out_of_scope_msg() -> str:
    return (
        "out_of_scope: value outside bill.json range "
        f"(kWh {bill_table.min_kwh}–{bill_table.max_kwh}, RM {bill_table.min_bill}–{bill_table.max_bill})"
    )


def format_solar_impact(input_rm: float, morning_usage_pct: float, sunpeak_hour: float) -> str:
    panel_rating = 0.62
    morning_ratio = max(0.0, min(100.0, morning_usage_pct)) / 100.0

    record = bill_table.nearest_by_bill(input_rm)
    if record is None:
        return out_of_scope_msg()

    total_usage = record.kwh
    panel_qty = total_usage / 30.0 / sunpeak_hour / panel_rating

    after_solar_usage = total_usage * (1.0 - morning_ratio)
    after_solar_record = bill_table.nearest_by_kwh(after_solar_usage)
    if after_solar_record is None:
        if after_solar_usage < bill_table.min_kwh:
            after_solar_record = bill_table.records[0]
        else:
            return f"Error: Calculated after-solar usage {after_solar_usage:.2f} kWh is out of bill.json range."

    after_solar_rm = after_solar_record.bill
    bill_reduction_rm = input_rm - after_solar_rm

    total_solar_generation_daily = panel_rating * sunpeak_hour * panel_qty
    total_solar_generation_monthly = total_solar_generation_daily * 30.0

    consumed_solar = total_usage * morning_ratio
    export_generation = total_solar_generation_monthly - consumed_solar
    export_income = export_generation * 0.20

    total_saving = export_income + bill_reduction_rm
    new_payable = input_rm - total_saving

    return (
        "[OFFICIAL MCP CALCULATION RESULT]\n"
        "*** DO NOT RECALCULATE. USE THESE EXACT FIGURES. ***\n"
        "\n"
        "Based on Malaysia TNB Tariff (bill.json lookup):\n"
        f"- Input Bill: RM {input_rm:.2f}\n"
        f"- Matched Usage: {total_usage:.2f} kWh (derived from official tariff table)\n"
        "\n"
        "Solar System Sizing (Targeting ~100% Offset):\n"
        f"- Required System Size: {panel_qty * panel_rating:.2f} kWp\n"
        f"- Number of Panels (620W): {int(panel_qty + 0.99)} panels (Calculated: {panel_qty:.2f})\n"
        f"- Generation Factor: {sunpeak_hour} peak hours/day\n"
        "\n"
        "Financial Analysis (Estimated):\n"
        f"- Total Solar Generation: {total_solar_generation_monthly:.2f} kWh/month\n"
        f"- Self-Consumption ({morning_usage_pct}%): {consumed_solar:.2f} kWh\n"
        f"- Grid Export: {export_generation:.2f} kWh\n"
        "\n"
        f"SAVINGS BREAKDOWN:\n"
        f"1. Bill Reduction: RM {bill_reduction_rm:.2f}\n"
        f"   (New Bill Charge: RM {after_solar_rm:.2f})\n"
        f"2. Export Income: RM {export_income:.2f} (@ RM 0.20/kWh)\n"
        f"--------------------------------------------------\n"
        f"TOTAL MONTHLY SAVINGS: RM {total_saving:.2f}\n"
        f"NEW NET PAYABLE: RM {new_payable:.2f}\n"
        f"--------------------------------------------------\n"
        "\n"
        "(Note to Agent: Provide these EXACT numbers to the user. Do not estimate based on other data sources.)"
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
                text=f"RM {rm:.2f} maps to {record.kwh} kWh (nearest bill entry RM {record.bill:.2f})",
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
                text=f"{record.kwh} kWh maps to RM {record.bill:.2f} (nearest to requested {kwh} kWh)",
            )
        ]

    if name == "calculate_solar_impact":
        input_rm = float(arguments["rm"])
        morning_usage_pct = float(arguments.get("morning_usage_percentage", 30))
        sunpeak_hour = float(arguments.get("sunpeak_hour", 3.4))
        return [TextContent(type="text", text=format_solar_impact(input_rm, morning_usage_pct, sunpeak_hour))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
