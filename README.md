# hAIre-core
An end to end HR phone screening agent

## Run
```bash
# Backend
git clone https://github.com/eyenpi/hAIre-core.git && cd hAIre-core
pip install -r requirements.txt
uvicorn app.main:app --reload
# Frontend
cd .. && git clone https://github.com/hoseinmrh/hAIre-Client.git && cd hAIre-Client
npm install
npm run dev
```
