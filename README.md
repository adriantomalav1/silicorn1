## Initial setup

### Create virtual environment
    python -m venv venv

### Activate virtual env
    source venv/bin/activate

### Intall dependencies
    pip install -r requirements.txt

### Apply migrations
    alembic upgrade head

### Run dev
    python -m uvicorn main:app --reload


## Changes in the models
    alembic revision --autogenerate -m "Description of the migration"
    alembic upgrade head
