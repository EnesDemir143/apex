.PHONY: check test lint typecheck format frontend k8s-local-build k8s-local-dry-run graphify-update

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

k8s-local-build:
	kubectl kustomize k8s/overlays/local

k8s-local-dry-run:
	kubectl apply --dry-run=client -k k8s/overlays/local

graphify-update:
	@echo "==> Graphify status"
	@if [ -f .planning/graphs/graph.json ]; then \
		echo "    graph.json: present"; \
		echo "    To rebuild graph: run /graphify in agent session"; \
	else \
		echo "    graph.json: missing — run /graphify first"; \
	fi
