import uvicorn
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Run Mirror.exe Dashboard')
    parser.add_argument('--host', default='127.0.0.1', help='Host to run the dashboard on')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the dashboard on')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    args = parser.parse_args()

    # Ensure the dashboard directory is in the Python path
    dashboard_dir = Path(__file__).parent / 'dashboard'
    
    print(f"🌟 Starting Mirror.exe Dashboard on http://{args.host}:{args.port}")
    
    uvicorn.run(
        "dashboard.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main() 