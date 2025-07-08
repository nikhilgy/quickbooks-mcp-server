# 🧾 QuickBooks MCP Server

> A secure, local-first Model Context Protocol (MCP) server to query QuickBooks data using natural language inside Claude Desktop.

--- 

## ✅ MCP Review Certification

This MCP Server is **[certified by MCP Review](https://mcpreview.com/mcp-servers/nikhilgy/quickbooks-mcp-server)**.

Being listed and certified on MCP Review ensures this server adheres to MCP standards and best practices, and is trusted by the developer community.

---

## Requirements:
1. Python 3.10 or higher

## Environment Setup
For local development, create a `.env` file in the project root with your QuickBooks credentials:

```bash
# Copy the template and fill in your actual credentials
cp env_template.txt .env
```

Then edit the `.env` file with your actual QuickBooks API credentials:
```
QUICKBOOKS_CLIENT_ID=your_actual_client_id
QUICKBOOKS_CLIENT_SECRET=your_actual_client_secret
QUICKBOOKS_REFRESH_TOKEN=your_actual_refresh_token
QUICKBOOKS_COMPANY_ID=your_actual_company_id
QUICKBOOKS_ENV='sandbox' or 'production'
```

**Note:** The `.env` file is automatically ignored by git for security reasons.

## Step 1. Install uv:
   - MacOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
   - Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

## Step 2. Configure Claude Desktop
1. Download [Claude Desktop](https://claude.ai/download).
2. Launch Claude and go to Settings > Developer > Edit Config.
3. Modify `claude_desktop_config.json` with:
```json
{
  "mcpServers": {
    "QuickBooks": {
      "command": "uv",
      "args": [
        "--directory",
        "<absolute_path_to_quickbooks_mcp_folder>",
        "run",
        "main_quickbooks_mcp.py"
      ]
    }
  }
}
```
4. Relaunch Claude Desktop.

The first time you open Claude Desktop with these setting it may take
10-20 seconds before the QuickBooks tools appear in the interface due to
the installation of the required packages and the download of the most 
recent QuickBooks API documentation.

Everytime you launch Claude Desktop, the most recent QuickBooks API tools are made available 
to your AI assistant.

## Step 3. Launch Claude Desktop and let your assistant help you
### Examples
**Query Accounts**
```text
Get all accounts from QuickBooks.
```

**Query Bills**
```text
Get all bills from QuickBooks created after 2024-01-01.
```

**Query Customers**
```text
Get all customers from QuickBooks.
``` 
