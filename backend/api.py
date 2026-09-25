from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from backend.services.orders import get_order, load_orders
from backend.services.risk import is_at_risk


def create_app() -> Flask:
    frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
    app = Flask(__name__, static_folder=str(frontend_dir), static_url_path="")

    @app.get("/api/orders")
    def list_orders():
        return jsonify(load_orders())

    @app.get("/api/at-risk-orders")
    def list_at_risk_orders():
        orders = load_orders()
        risky_orders = [order for order in orders if is_at_risk(order)]
        # Sort by estimated_delay_minutes descending (most urgent first)
        risky_orders.sort(key=lambda o: o.get("estimated_delay_minutes", 0), reverse=True)
        return jsonify(risky_orders)

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
