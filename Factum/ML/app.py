from flask import Flask, request, jsonify
from ml_service import predict_news
from fact_check_service import check_fact
from database import init_db, save_prediction

app = Flask(__name__)

init_db()


@app.route("/")
def home():
    return jsonify({
        "project": "Factum API",
        "status": "running",
        "version": "1.0"
    })


@app.route("/classify", methods=["POST"])
def classify():

    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({
            "error": "Texto não enviado"
        }), 400

    text = data["text"].strip()

    if not text:
        return jsonify({
            "error": "Texto vazio"
        }), 400

    fact_result = check_fact(text)

    if fact_result:

        rating = fact_result.get("rating", "UNKNOWN")

        save_prediction(
            text,
            rating,
            "fact-check"
        )

        return jsonify({
            "success": True,
            "source": "fact-check",
            "result": {
                "claim": fact_result.get("claim", text),
                "rating": rating,
                "publisher": fact_result.get("source"),
                "url": fact_result.get("url", "")
            }
        })

    prediction = predict_news(text)

    save_prediction(
        text,
        prediction,
        "machine-learning"
    )

    return jsonify({
        "success": True,
        "source": "machine-learning",
        "classification": prediction
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Rota não encontrada"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Erro interno do servidor"
    }), 500


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )