.PHONY: check test lint typecheck format frontend

check: lint typecheck test

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy src/

test:
	uv run pytest tests/ -v 

verify:
	uv run python -c "import apex; print('✓ apex package importable')"
	@ls uv.lock > /dev/null 2>&1 && echo "✓ uv.lock exists" || echo "✗ uv.lock not found"
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) test

frontend:
	PYTHONPATH=src uv run streamlit run src/apex/frontend/app.py
