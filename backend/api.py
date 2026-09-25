from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from backend.services.orders import get_at_risk_orders, get_order, load_orders


def create_app() -> Flask:
    frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
    app = Flask(__name__, static_folder=str(frontend_dir), static_url_path="")

    @app.get("/api/orders")
    def list_orders():
        return jsonify(load_orders())

    @app.get("/api/orders/at-risk")
    def at_risk_orders():
        return jsonify(get_at_risk_orders())

    @app.get("/api/orders/<order_id>")
    def order_detail(order_id: str):
        order = get_order(order_id)
        if order is None:
            return jsonify({"error": "order_not_found"}), 404
        return jsonify(order)

    @app.get("/")
    def index():
        return send_from_directory(frontend_dir, "index.html")

    return app
