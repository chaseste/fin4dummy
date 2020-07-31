"""Application Rest routes."""
from flask import current_app as app, request, session, jsonify
from flask_jwt_extended import jwt_required

from ..manager import PortfolioManager
from .. import csrf

@app.route("/market/suggested-symbols", methods=["GET"])
@jwt_required
@csrf.exempt
def suggested_symbols():
	"""Returns the suggested symbols"""
	return jsonify(PortfolioManager.suggested_stocks()), 200

@app.route("/market/price", methods=["GET"])
@jwt_required
@csrf.exempt
def price():
	"""Looks up the price of the stock"""
	price = PortfolioManager.asking_price(request.args.get("symbol", default = ""))
	if price is None:
		return jsonify({"msg": "Invalid Symbol"}), 400
	return jsonify(price), 200
