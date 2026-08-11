"""Local development entry point."""
from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402  must load .env before importing config

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
