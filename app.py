from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html><body style="font-family:sans-serif;text-align:center;padding:60px;background:#0b0b0c;color:#c9a24b">
    <h1>WALLAET CLOUD LIVE ✅</h1>
    <p style="color:#f4f1ea">Cloud server chal raha hai. Ab Wallaet app yahan aayega.</p>
    </body></html>
    """

@app.route("/health")
def health():
    return {"status": "ok", "service": "wallaet-cloud"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
