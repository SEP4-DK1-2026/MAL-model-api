# Makefile for automation (we can add more as we go)

install:
	pip install -r requirements.txt

run:
	uvicorn api.main:app --reload

# lint:
# 	ruff check .

# format:
# 	ruff format .
# I don't know if these are useful now and what behavior we want. We could for example just do it on a single file at a time.