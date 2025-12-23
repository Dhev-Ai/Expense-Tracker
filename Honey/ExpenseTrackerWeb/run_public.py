"""
Run Flask app with public HTTPS URL using ngrok
"""

from pyngrok import ngrok, conf
import os
import sys

# Set ngrok configuration
# If you have an ngrok auth token, uncomment and set it below:
# ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")

def run_with_ngrok():
    """Start the Flask app with ngrok tunnel"""
    
    # Kill any existing ngrok processes
    ngrok.kill()
    
    # Create a tunnel on port 5000
    print("🚀 Starting ngrok tunnel...")
    public_url = ngrok.connect(5000, "http")
    
    print("\n" + "=" * 60)
    print("🌐 PUBLIC HTTPS URL (Share this in Chrome):")
    print(f"\n   {public_url}")
    print("\n" + "=" * 60)
    print("\n📋 Copy the URL above and open it in any browser!")
    print("   Press Ctrl+C to stop the server\n")
    
    # Import and run Flask app
    from app import app
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    try:
        run_with_ngrok()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        ngrok.kill()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 If you see authentication errors, you need to:")
        print("   1. Sign up at https://ngrok.com (free)")
        print("   2. Get your auth token from https://dashboard.ngrok.com/get-started/your-authtoken")
        print("   3. Run: ngrok authtoken YOUR_TOKEN")
        ngrok.kill()
