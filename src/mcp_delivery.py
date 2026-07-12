import os
import asyncio
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from mcp import ClientSession
# pyrefly: ignore [missing-import]
from mcp.client.sse import sse_client

# Load environment variables
load_dotenv()

async def main():
    doc_id = os.getenv("GOOGLE_DOC_ID")
    to_email = os.getenv("GMAIL_TO_EMAIL")

    if not doc_id or not to_email or doc_id == "your_google_doc_id_here":
        print("Missing GOOGLE_DOC_ID or GMAIL_TO_EMAIL in .env")
        return

    # Find the generated weekly pulse report
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_path = os.path.join(base_dir, 'data', 'weekly_pulse_report.md')
    
    if not os.path.exists(report_path):
        print(f"Weekly pulse report not found at {report_path}")
        return

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    mcp_url = "https://mcp-server-production-57b3.up.railway.app/sse"
    print(f"Connecting to remote MCP Server at {mcp_url}...")
    
    try:
        # Create SSE connection to the remote MCP Server
        async with sse_client(mcp_url) as streams:
            # Create a standard MCP client session over the SSE streams
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()

                # 1. Append content to Google Doc
                print(f"Appending report to Google Doc (ID: {doc_id})...")
                doc_result = await session.call_tool("gdocs_append_content", arguments={
                    "documentId": doc_id,
                    "content": "\n\n" + content
                })
                print(f"Google Docs Response: {doc_result.content}")

                # 2. Draft the Email in Gmail
                doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
                email_subject = "Groww AI Agent: Weekly Pulse Report"
                email_body = (
                    f"Hello,\n\nThe AI Agent has generated the latest Weekly Pulse Report.\n"
                    f"You can review it directly in the Google Document here: {doc_link}\n\n"
                    f"Below is a plain text copy of the pulse report:\n\n{content}"
                )
                
                print(f"Creating Gmail draft for {to_email}...")
                email_result = await session.call_tool("gmail_create_draft", arguments={
                    "to": [to_email],
                    "subject": email_subject,
                    "body": email_body
                })
                print(f"Gmail Response: {email_result.content}")
                
    except Exception as e:
        if hasattr(e, 'response'):
            print(f"MCP HTTP Error: {e.response.status_code} - {e.response.text}")
        else:
            import traceback
            traceback.print_exc()
            print(f"MCP Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
