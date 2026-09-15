PYTHON := venv311/Scripts/python.exe
HOST ?= 127.0.0.1
PORT ?= 8000

.PHONY: run dev migrate seed shell help

run:
	$(PYTHON) manage.py runserver $(HOST):$(PORT)

dev: run

migrate:
	$(PYTHON) manage.py migrate

seed:
	$(PYTHON) manage.py seed_demo

shell:
	$(PYTHON) manage.py shell

help:
	@echo "Available targets:"
	@echo "  make run            - runserver $(HOST):$(PORT)"
	@echo "  make run PORT=8001  - runserver custom port"
	@echo "  make migrate        - apply migrations"
	@echo "  make seed           - seed demo user/data"
	@echo "  make shell          - django shell"
