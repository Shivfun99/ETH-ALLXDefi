Project 2: ASI-powered risk engine
Backend Setup (Python/FastAPI) cd backend python3 -m venv .venv source .venv/bin/activate

Install Dependencies pip install -r app/requirements.txt

Environment Variables Copy .env.example to .env in backend/app/ (if exists) and configure as needed.

Database SQLite is used (risk.db present already) To initialize or migrate, use any scripts or just let db.py handle on launch.

Run the Backend uvicorn app.main:app --reload

Frontend Setup (React + Vite) cd frontend npm install

Run Development Server npm run dev

Scripts and Testing python app/mock_asi.py

Project Customization Python requirements: Edit backend/app/requirements.txt Frontend packages: Edit frontend/package.json Environment variables: Edit .env in each respective folder

About
ALLXDeFi blends ZKP privacy, AI risk prediction, Blockscout transparency and Hardhat automation. Its AI core predicts risk from volatility and market trends using FastAPI + TensorFlow. ZKPs prove portfolio claims securely on Sepolia, verified through Blockscout, while Hardhat streamlines deployment for a trustless AI‑driven DeFi ecosystem .


