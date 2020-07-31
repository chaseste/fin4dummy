"""Application Rest routes."""
from flask import current_app as app, request, session, jsonify
from flask_jwt_extended import jwt_required

from ..manager import PortfolioManager, Registrar
from .. import csrf

@app.route("/portfolio/holdings", methods=["GET"])
@jwt_required
@csrf.exempt
def holdings():
	"""Looks up the user's holdings"""
	return jsonify(PortfolioManager.holdings()), 200

@app.route("/portfolio/holding", methods=["GET"])
@jwt_required
@csrf.exempt
def holding():
	"""Looks up the holding"""
	holding = PortfolioManager.holding(request.args.get("id", default = 0))
	if holding is None:
		return jsonify({"msg": "Invalid Holding"}), 400
	return jsonify(holding), 200

@app.route("/portfolio/holding-symbols", methods=["GET"])
@jwt_required
@csrf.exempt
def holding_symbols():
	"""Looks up the symbols for the user's holdings"""
	return jsonify(PortfolioManager.holding_symbols()), 200
