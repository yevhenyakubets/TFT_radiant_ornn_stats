.PHONY: build-frontend run-frontend frontend

build-frontend:
	cd frontend && docker build -t tft-frontend-test .
run-frontend:
	docker run -d -p 5173:5173 --name tft-frontend-container tft-frontend-test
frontend: build-frontend run-frontend