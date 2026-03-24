"""
Entry point: launches the Flask web server instead of Streamlit.
Run: python app.py
"""

from server import app

if __name__ == "__main__":
    app.run(debug=False, port=5000)