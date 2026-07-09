"""Server Flask per il generatore di nomi progetto."""

import os
from flask import Flask, render_template, request, jsonify, session

from nome_generatore import genera_nomi

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nomixprogetto-dev-secret-2026")


@app.route("/")
def index():
    """Pagina principale — frontend del generatore."""
    return render_template("index.html")


@app.route("/api/genera", methods=["POST"])
def api_genera():
    """Endpoint che riceve la descrizione e restituisce i nomi generati."""
    data = request.get_json(silent=True) or {}
    descrizione = data.get("descrizione", "").strip()

    if not descrizione:
        return jsonify({"errore": "Inserisci una descrizione."}), 400

    # Recupera i nomi già generati nella sessione
    nomi_precedenti: set[str] = set(session.get("nomi_generati", []))

    try:
        nomi = genera_nomi(descrizione, nomi_esistenti=nomi_precedenti, count=8)
    except ValueError as e:
        return jsonify({"errore": str(e)}), 400

    # Aggiorna la sessione
    session["nomi_generati"] = sorted(nomi_precedenti | set(nomi))

    return jsonify({"nomi": nomi})


@app.route("/robots.txt")
def robots():
    """Serve robots.txt."""
    return app.send_static_file("robots.txt")


@app.route("/sitemap.xml")
def sitemap():
    """Serve sitemap.xml."""
    return app.send_static_file("sitemap.xml")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4601))
    app.run(host="0.0.0.0", port=port, debug=False)
