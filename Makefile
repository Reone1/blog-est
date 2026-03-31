.PHONY: build test lint clean generate crawl publish report

# Go binaries
GOBIN := $(shell go env GOPATH)/bin

## Build
build:
	go build -o bin/generate ./cmd/generate/
	go build -o bin/crawl ./cmd/crawl/
	go build -o bin/publish ./cmd/publish/
	go build -o bin/report ./cmd/report/

## Test
test:
	go test ./core/... -v

test-config:
	go test ./core/config/ -v -run TestLoadSite

## Lint
lint:
	go vet ./...

## Content generation (via Go CLI)
generate:
	go run cmd/generate/main.go --site $(SITE) --type $(TYPE)

generate-all:
	go run cmd/generate/main.go --all

## Legacy Python commands (finance site)
legacy-setup:
	pip install -e ./tools/content-generator

legacy-daily: legacy-setup
	python -m content_generator.cli generate --type daily_briefing --output posts/

legacy-weekly: legacy-setup
	python -m content_generator.cli generate --type weekly_review --output posts/

legacy-monthly: legacy-setup
	python -m content_generator.cli generate --type monthly_review --output posts/

legacy-sidebar:
	python scripts/update_sidebar.py

legacy-sitemap:
	python scripts/update_sitemap.py

## Clean
clean:
	rm -rf bin/

## Help
help:
	@echo "Usage:"
	@echo "  make build              Build all Go binaries"
	@echo "  make test               Run all Go tests"
	@echo "  make test-config        Run config loader tests"
	@echo "  make generate SITE=tech TYPE=how-to    Generate content"
	@echo "  make generate-all       Generate for all sites"
	@echo "  make legacy-daily       Run Python daily briefing"
	@echo "  make legacy-weekly      Run Python weekly review"
	@echo "  make legacy-monthly     Run Python monthly review"
	@echo "  make clean              Remove build artifacts"
