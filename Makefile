
PYTHON = python3
MAIN = a_maze_ing.py
CONFIG = config.txt
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
MYPY_STRICT = --strict 

all: run

install:
	pip install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	# Rimuove le cartelle nella root
	rm -rf .mypy_cache .pytest_cache
	# Trova e rimuove tutte le cartelle __pycache__ nel progetto
	find . -type d -name "__pycache__" -exec rm -rf {} +
	# Trova e rimuove tutte le cartelle .mypy_cache ovunque siano
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
lint:
	flake8 .
	mypy $(MYPY_FLAGS) .
lint-strict:
	flake8 .
	mypy $(MYPY_STRICT) .



.PHONY: all install run debug clean lint lint_strict
