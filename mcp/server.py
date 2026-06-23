"""
server.py — MCP server entrypoint.
Exposes search_schemes, check_eligibility, fetch_app_link as MCP tools.

Run:
    python mcp/server.py
"""
from __future__ import annotations
import json, logging, os, sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("kisan_samman.mcp_server")

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp.server import MCPServer, tool
    _MCP_LIB = True
except ImportError:
    logger.warning("mcp library not installed. Run: pip install mcp")
    _MCP_LIB = False

from mcp.tools.search_schemes import search_schemes
from mcp.tools.check_eligibility import check_eligibility
from mcp.tools.fetch_app_link import fetch_app_link

HOST = os.getenv("MCP_SERVER_HOST", "localhost")
PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))


if _MCP_LIB:
    server = MCPServer(name="kisan-samman-mcp", version="1.0.0")

    @tool(server)
    def search_schemes_tool(query: str, state: str = "", crop_type: str = "") -> str:
        """Search government scheme database by keyword, state and crop type."""
        results = search_schemes(query=query, state=state, crop_type=crop_type)
        return json.dumps(results, ensure_ascii=False)

    @tool(server)
    def check_eligibility_tool(scheme_ids: list, farmer_profile: dict) -> str:
        """Check which schemes a farmer is eligible for given their profile."""
        results = check_eligibility(scheme_ids=scheme_ids, farmer_profile=farmer_profile)
        return json.dumps(results, ensure_ascii=False)

    @tool(server)
    def fetch_app_link_tool(scheme_id: str, district: str = "") -> str:
        """Get application portal URL and nearest CSC for a scheme."""
        result = fetch_app_link(scheme_id=scheme_id, district=district)
        return json.dumps(result, ensure_ascii=False)

    if __name__ == "__main__":
        logger.info("Starting Kisan Samman MCP Server on %s:%s", HOST, PORT)
        server.run(host=HOST, port=PORT)
else:
    # Fallback: minimal HTTP server for testing without mcp library
    import http.server, socketserver

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            tool_name = body.get("tool")
            args = body.get("args", {})
            dispatch = {
                "search_schemes": search_schemes,
                "check_eligibility": check_eligibility,
                "fetch_app_link": fetch_app_link,
            }
            fn = dispatch.get(tool_name)
            if fn is None:
                self.send_response(404)
                self.end_headers()
                return
            result = fn(**args)
            data = json.dumps(result, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        def log_message(self, *_): pass

    if __name__ == "__main__":
        logger.info("Starting fallback HTTP MCP server on %s:%d", HOST, PORT)
        with socketserver.TCPServer((HOST, PORT), _Handler) as httpd:
            httpd.serve_forever()
