MLX_WHEEL ?= mlx-2.2/ubuntu/mlx-2.2-py3-none-any.whl
 
VENV    := venv
PYTHON  := $(VENV)/bin/python3
PIP     := $(VENV)/bin/pip
MAIN    := a_maze_ing.py
CONFIG  ?= config.txt

MYPY_FLAGS := --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs

.PHONY: install run debug clean lint lint-strict build

install:
	@test -f $(MLX_WHEEL) || \
		(echo "Error: MLX wheel not found: $(MLX_WHEEL)" >&2; exit 1)
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy build
	$(PIP) install $(MLX_WHEEL)

run:
	$(PYTHON) $(MAIN) $(CONFIG)
 
debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -path ./$(VENV) -prune -o -type d -name "__pycache__" \
		-exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist *.egg-info
	rm -rf mazegen-1.0.0-py3-none-any.whl mazegen-1.0.0.tar.gz

lint:
	$(PYTHON) -m flake8 . --exclude=venv,.venv
	$(PYTHON) -m mypy . $(MYPY_FLAGS)
 
lint-strict:
	$(PYTHON) -m flake8 . --exclude=venv,.venv
	$(PYTHON) -m mypy . --strict $(MYPY_FLAGS)

build:  # Non funziona
	$(PYTHON) -m build
	cp dist/mazegen-* .