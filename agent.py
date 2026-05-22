import json
from google import genai
from google.genai import types
from config import Config
import mcp_client
import bigquery_helper

SYSTEM_PROMPT = """You are AgriSync, an AI-powered Farm Co-Pilot for Nigerian farmers.
You help with:
- Crop recommendations based on season, soil, and Nigerian state
- Pest and disease identification and management
- Weather-based planting advice
- Data pipeline management via Fivetran MCP tools
- Farm data analysis from BigQuery

You have tools to:
1. Check Fivetran data pipeline status (list connectors, sync status, trigger resyncs)
2. Query farm data from BigQuery
3. Give agricultural advice for Nigerian farming contexts

Always be practical, friendly, and consider Nigerian crops (maize, yam, rice, cassava, sorghum),
states (Kano, Benue, Kaduna, Oyo, Enugu), and seasons (wet/dry).
When asked about data or pipelines, always use the Fivetran MCP tools.
Keep responses concise and actionable.
"""

TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="list_fivetran_connectors",
                description="List all Fivetran data connectors and their sync status. Use when farmer asks about data pipelines or connections.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={}
                )
            ),
            types.FunctionDeclaration(
                name="get_fivetran_connector",
                description="Get detailed info about a specific Fivetran connector by ID.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "connector_id": types.Schema(
                            type=types.Type.STRING,
                            description="The Fivetran connector ID"
                        )
                    },
                    required=["connector_id"]
                )
            ),
            types.FunctionDeclaration(
                name="trigger_fivetran_sync",
                description="Trigger a manual data sync for a Fivetran connector.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "connector_id": types.Schema(
                            type=types.Type.STRING,
                            description="The connector ID to sync"
                        )
                    },
                    required=["connector_id"]
                )
            ),
            types.FunctionDeclaration(
                name="check_sync_status",
                description="Check the latest sync status for a Fivetran connector.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "connector_id": types.Schema(
                            type=types.Type.STRING,
                            description="The connector ID to check"
                        )
                    },
                    required=["connector_id"]
                )
            ),
            types.FunctionDeclaration(
                name="list_fivetran_groups",
                description="List all Fivetran destination groups and warehouses.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={}
                )
            ),
            types.FunctionDeclaration(
                name="get_crop_summary",
                description="Get crop yield summary from the farm database in BigQuery.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={}
                )
            ),
            types.FunctionDeclaration(
                name="get_weather_data",
                description="Get recent weather data for a Nigerian state.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "state": types.Schema(
                            type=types.Type.STRING,
                            description="Nigerian state name e.g. Kano, Lagos, Benue, Kaduna"
                        )
                    }
                )
            ),
            types.FunctionDeclaration(
                name="get_sensor_readings",
                description="Get the latest IoT sensor readings from farm devices.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={}
                )
            ),
        ]
    )
]


def _execute_tool(name: str, args: dict) -> str:
    """Execute a tool and return the result as a JSON string."""
    try:
        if name == "list_fivetran_connectors":
            result = mcp_client.list_connectors()
        elif name == "get_fivetran_connector":
            result = mcp_client.get_connector(args.get("connector_id"))
        elif name == "trigger_fivetran_sync":
            result = mcp_client.trigger_sync(args.get("connector_id"))
        elif name == "check_sync_status":
            result = mcp_client.get_sync_status(args.get("connector_id"))
        elif name == "list_fivetran_groups":
            result = mcp_client.list_groups()
        elif name == "get_crop_summary":
            df = bigquery_helper.get_crop_summary()
            result = {"success": True, "data": df.to_dict(orient="records")}
        elif name == "get_weather_data":
            df = bigquery_helper.get_weather_summary(args.get("state", "Kano"))
            result = {"success": True, "data": df.to_dict(orient="records")}
        elif name == "get_sensor_readings":
            df = bigquery_helper.get_recent_sensor_readings()
            result = {"success": True, "data": df.to_dict(orient="records")}
        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


class AgriSyncAgent:
    def __init__(self):
        self.client = genai.Client(
    api_key=Config.GOOGLE_API_KEY
        )
        self.model = "gemini-2.0-flash"
        self.conversation_history = []
        self.tool_calls_log = []

    def chat(self, user_message: str) -> dict:
        """Send a message and get a response, executing any tool calls."""
        self.conversation_history.append(
            types.Content(role="user", parts=[types.Part(text=user_message)])
        )

        current_tool_calls = []

        # Agentic loop — keeps running until Gemini gives a final text response
        while True:
            response = self.client.models.generate_content(
                model=self.model,
                contents=self.conversation_history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=TOOLS,
                    temperature=0.7,
                )
            )

            candidate = response.candidates[0]
            parts     = candidate.content.parts

            # Check for function calls in the response
            has_function_call = any(
                hasattr(p, "function_call") and p.function_call for p in parts
            )

            if has_function_call:
                self.conversation_history.append(candidate.content)
                tool_results = []

                for part in parts:
                    if hasattr(part, "function_call") and part.function_call:
                        fc        = part.function_call
                        tool_name = fc.name
                        tool_args = dict(fc.args) if fc.args else {}
                        result    = _execute_tool(tool_name, tool_args)

                        log_entry = {"tool": tool_name, "args": tool_args, "result": result}
                        current_tool_calls.append(log_entry)
                        self.tool_calls_log.append(log_entry)

                        tool_results.append(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    response={"result": result}
                                )
                            )
                        )

                self.conversation_history.append(
                    types.Content(role="user", parts=tool_results)
                )

            else:
                # Final text response — exit loop
                final_text = "".join(
                    p.text for p in parts if hasattr(p, "text") and p.text
                )
                self.conversation_history.append(candidate.content)
                return {"response": final_text, "tool_calls": current_tool_calls}

    def clear_history(self):
        self.conversation_history = []
        self.tool_calls_log = []