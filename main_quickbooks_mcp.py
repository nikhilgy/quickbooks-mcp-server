from mcp import types
from mcp.server.fastmcp import FastMCP
from quickbooks_interaction import QuickBooksSession
from api_importer import load_apis
import sys
import json
from pathlib import Path

# Initialize QuickBooks session with error handling
quickbooks = None
try:
    quickbooks = QuickBooksSession()
    print("✓ QuickBooks session initialized successfully", file=sys.stderr)
except Exception as e:
    print(f"✗ Failed to initialize QuickBooks session: {e}", file=sys.stderr)
    print("Please check your .env file and QuickBooks credentials", file=sys.stderr)

mcp = FastMCP("quickbooks")

@mcp.tool()
def get_quickbooks_entity_schema(entity_name: str) -> types.TextContent:
    """
    Fetches the schema for a given QuickBooks entity (e.g., 'Bill', 'Customer').
    Use this tool to understand the available fields for an entity before constructing a query with the `query_quickbooks` tool.
    """
    schema_path = Path(__file__).parent / 'quickbooks_entity_schemas.json'
    try:
        with open(schema_path, 'r') as f:
            all_schemas = json.load(f)
        
        entity_schema = all_schemas.get(entity_name)
        
        if entity_schema:
            return types.TextContent(type='text', text=json.dumps(entity_schema, indent=2))
        else:
            available_entities = list(all_schemas.keys())
            return types.TextContent(type='text', text=f"Error: Schema not found for entity '{entity_name}'. Available entities: {available_entities}")
    except FileNotFoundError:
        return types.TextContent(type='text', text="Error: The schema definition file `quickbooks_entity_schemas.json` was not found.")
    except Exception as e:
        return types.TextContent(type='text', text=f"An error occurred: {e}")

@mcp.tool()
def query_quickbooks(query: str) -> types.TextContent:
    """
    Executes a SQL-like query on a QuickBooks entity.
    **IMPORTANT**: Before using this tool, you MUST first use the `get_quickbooks_entity_schema` tool to get the schema for the entity you want to query (e.g., 'Bill', 'Customer'). This will show you the available fields to use in your query's `select` and `where` clauses.
    """
    if quickbooks is None:
        return types.TextContent(type='text', text="Error: QuickBooks session not initialized. Please check your credentials and restart the server.")
    
    try:
        response = quickbooks.query(query)
        return types.TextContent(type='text', text=str(response))
    except Exception as e:
        return types.TextContent(type='text', text=f"Error executing query: {e}")

def register_all_apis():
    apis = load_apis()
    for api in apis:
        response_description = api["response_description"]

        # Clean up the route and remove the company/realm part
        original_route = api['route']
        if '/v3/company/{realmId}' in original_route:
            clean_api_route = original_route.replace('/v3/company/{realmId}', '')
        else:
            clean_api_route = original_route

        clean_route_for_name = (clean_api_route.replace('/', '_').replace('-', '_').replace(':', '_')
                               .replace('{', '').replace('}', ''))

        method_name = f'{api["method"]}{clean_route_for_name}'
        clean_summary = api["summary"]
        if clean_summary is None:
            words = method_name.split('_')
            words[0] = words[0].capitalize()
            clean_summary = ' '.join(words) + '. '

        doc = clean_summary + '. '
        if response_description != "OK":
            doc += f'If successful, the outcome will be \"{api["response_description"]}\". '
        
        # Combine request_data and parameters for the docstring
        all_params = {}
        api_params_filtered = [p for p in api.get('parameters', []) if p['name'] != 'realmId']

        if api_params_filtered:
            for p in api_params_filtered:
                all_params[p['name']] = {
                    'description': p.get('description', 'No description provided'),
                    'required': p.get('required', False),
                    'type': p.get('type', 'unknown'),
                    'in': p.get('location')
                }
        
        if api.get('request_data'):
            doc += f'The request body should be a JSON object with the following structure: {json.dumps(api["request_data"])}. '

        if all_params:
            doc += f'Parameters: {json.dumps(all_params, indent=2)}. '

        # Create a more structured tool function definition
        method_str = f"""
@mcp.tool()
def {method_name}(**kwargs) -> types.TextContent:
    \"\"\"{doc}\"\"\"
    
    # Check if QuickBooks is initialized
    if quickbooks is None:
        return types.TextContent(type='text', text="Error: QuickBooks session not initialized. Please check your credentials and restart the server.")
    
    # Workaround for clients that pass all arguments as a single string in 'kwargs'
    if 'kwargs' in kwargs and isinstance(kwargs['kwargs'], str) and '=' in kwargs['kwargs']:
        try:
            key, value = kwargs['kwargs'].split('=', 1)
            # Overwrite kwargs with the parsed arguments
            kwargs = {{key: value}}
        except Exception:
            # If parsing fails, do nothing and proceed with the original kwargs
            pass

    print(f"Executing '{method_name}' with arguments: {{kwargs}}", file=sys.stderr)
    
    try:
        route = \"{clean_api_route}\"
        api_method = \"{api['method']}\"
        
        path_params = {{}}
        query_params = {{}}
        request_body = {{}}

        # Separate parameters based on their location ('in')
        api_params = {api_params_filtered}
        for p_info in api_params:
            p_name = p_info['name']
            if p_name in kwargs:
                if p_info['location'] == 'path':
                    path_params[p_name] = kwargs[p_name]
                elif p_info['location'] == 'query':
                    query_params[p_name] = kwargs[p_name]

        # The rest of kwargs are assumed to be the request body for POST/PUT/PATCH
        if api_method.lower() in ['post', 'put', 'patch']:
            body_keys = set(kwargs.keys()) - set(path_params.keys()) - set(query_params.keys())
            for k in body_keys:
                request_body[k] = kwargs[k]

        # Format the route with path parameters
        if path_params:
            try:
                route = route.format(**path_params)
            except KeyError as e:
                return types.TextContent(type='text', text=f"Error: Missing required path parameter {{e}} for route {{route}}")

        response = quickbooks.call_route(
            method_type=api_method,
            route=route,
            params=query_params,
            body=request_body if request_body else None
        )
        
        print(f"Response from '{method_name}': {{response}}", file=sys.stderr)
        return types.TextContent(type='text', text=str(response))
    except Exception as e:
        error_msg = f"Error executing {method_name}: {{e}}"
        print(error_msg, file=sys.stderr)
        return types.TextContent(type='text', text=error_msg)
"""
        exec(method_str, globals(), locals())

register_all_apis()

if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(transport='stdio') 