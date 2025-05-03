from mcp import types
from mcp.server.fastmcp import FastMCP
from quickbooks_interaction import QuickBooksSession
from api_importer import load_apis
import sys

quickbooks = QuickBooksSession()
mcp = FastMCP("quickbooks")

@mcp.tool()
def query_quickbooks(query: str) -> types.TextContent:
    """Execute a QuickBooks query. The query should be in QuickBooks SQL-like syntax."""
    response = quickbooks.query(query)
    return types.TextContent(type='text', text=str(response))

def register_all_apis():
    apis = load_apis()
    for api in apis:
        response_description = api["response_description"]

        clean_route = (api['route'].replace('/', '_').replace('-', '_').replace(':', '_')
                       .replace('{', '').replace('}', ''))

        method_name = f'{api["method"]}{clean_route}'
        clean_summary = api["summary"]
        if clean_summary is None:
            words = method_name.split('_')
            words[0] = words[0].capitalize()
            clean_summary = ' '.join(words) + '. '

        doc = clean_summary + '. '
        if response_description != "OK":
            doc += f'If successful, the outcome will be \"{api["response_description"]}\". '
        if api['request_data']:
            doc += f'The request data should be: {api["request_data"]}.'
        if api['parameters']:
            doc += f'The parameters should be: {api["parameters"]}.'
        else:
            doc += f'The request data should be an empty dictionary {{}}.'

        method_str = f"""
@mcp.tool()
def {method_name}(request_data: dict = None) -> types.TextContent:
    \"\"\"{doc}\"\"\"
    print("The input of method {method_name} is", request_data, file=sys.stderr)
    if request_data is None or request_data == "" or request_data == "null" or request_data.get("request_data") == "null":
        request_data = None
    route = \"{api['route']}\"
    if '{{' in route:
        route = route.format(**request_data)
    response = quickbooks.call_route(\"{api['method']}\", route, request_data)
    print("The input of method {method_name} is", response, file=sys.stderr)
    return types.TextContent(type='text', text=str(response))
"""
        exec(method_str)

register_all_apis()

if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(transport='stdio') 