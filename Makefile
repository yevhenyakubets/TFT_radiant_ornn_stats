run-backend:
	cd backend && source .venv/Scripts/activate && uvicorn app.main:app --reload
run-frontend:
	cd frontend && npm run dev