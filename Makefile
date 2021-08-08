.PHONY: run test

all: run

test:
	pipenv run python -m unittest

run:
	pipenv run python supermarkt_price_index/main.py

