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
        if kwh < self.min_kwh or kwh > self.max_kwh:
            return None
        return min(self.records, key=lambda r: abs(r.kwh - kwh))


def load_bill_table() -> BillTable:
    base_path = Path(__file__).resolve()
    primary = base_path.parent / "bill.json"
    fallback = base_path.parents[2] / "resource" / "bill.json"
    data_path = primary if primary.exists() else fallback

    with data_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    records = [BillRecord(kwh=float(item["kwh"]), bill=float(item["bill"])) for item in raw]
    return BillTable(records)


server = Server("billing-mcp-server")
bill_table = load_bill_table()


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

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
