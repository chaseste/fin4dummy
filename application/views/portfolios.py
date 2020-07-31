""" Application stock portfolio routes """
from datetime import datetime

from flask import flash, request, session
from flask import current_app as app

from ..internal.redirects import Redirects
from ..internal.stocks import Stocks
from ..manager import PortfolioManager

from .decorators import authenticated
from .forms import PortfolioForms as _forms
from .templates import PortfolioTemplates as _templates

def portfolio():
	"""Show portfolio of stocks"""
	if PortfolioManager.is_market_closed():
		flash("Market is closed!", "error")
	return _templates.portfolio(PortfolioManager.portfolio())

@app.route("/")
def index():
	return Redirects.authenticated(lambda : portfolio(), lambda : _templates.index())

@app.route("/closed-positions", methods=["GET"])
@authenticated
def closed_positions():
	"""Show closed positions"""
	return _templates.closed_positions(PortfolioManager.closed_positions())

@app.route("/position", methods=["GET"])
@authenticated
def position():
	"""Get stock position."""
	if PortfolioManager.is_market_closed():
		flash("Market is closed!", "error")
	return _templates.position(PortfolioManager.position(request.args.get("symbol")))

@app.route("/history")
@authenticated
def history():
	"""Show history of transactions"""
	return _templates.history(PortfolioManager.history(request.args.get("page", 1, type=int)))

@app.route("/insights", methods=["GET"])
@authenticated
def insights():
	"""Market Insights"""
	return _templates.insights(PortfolioManager.insights())

@app.route("/quote", methods=["GET", "POST"])
@authenticated
def quote():
	"""Get stock quote."""
	quote = None

	form = _forms.quote(request)
	if request.method == "POST" and form.validate_on_submit():
		quote = PortfolioManager.quote(form.symbol.data)
		if quote is None:
			flash("Invalid Symbol.")
	elif request.method == "GET":
		form.symbol.data = request.args.get("symbol", default = "")
		if form.symbol.data != "":
			quote = PortfolioManager.quote(form.symbol.data)
			if quote is None:
				flash("Invalid Symbol.")
	
	if PortfolioManager.is_market_closed():
		flash("Market is closed!", "error")
	return _templates.quote(form) if quote is None else _templates.quoted(quote)  

@app.route("/buy", methods=["GET", "POST"])
@authenticated
def buy():
	"""Buy shares of stock"""
	form = _forms.buy(request)
	if request.method == "POST" and form.validate_on_submit():
		if PortfolioManager.buy(form.symbol.data, form.shares.data):
			return Redirects.home()
		flash(" ".join(["Buying", str(form.shares.data), "shares would exceed cash on hand."]), "error")
	
	if PortfolioManager.is_market_closed():
		flash("Market is closed!", "error")
	return _templates.buy(form)

@app.route("/sell", methods=["GET", "POST"])
@authenticated
def sell():
	"""Sell shares of stock"""
	form = _forms.sell(request)
	if request.method == "POST" and form.validate_on_submit():
		PortfolioManager.sell(form.selected_holding(), form.shares.data)
		return Redirects.home()
	
	if PortfolioManager.is_market_closed():
		flash("Market is closed!", "error")
	return _templates.sell(form)
