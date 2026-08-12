File	Job	Who's the authority
init.sql	Defines what actually exists in Postgres — tables, columns, constraints, triggers. The only place schema is created.	Postgres
models.py	Maps existing Postgres tables to Python classes so your code can read/write rows via SQLAlchemy instead of raw SQL strings. Describes storage.	SQLAlchemy (read/write only, never creates)
schemas.py	Defines what shape of JSON your API will accept in and send out — separate from storage shape, validated automatically by Pydantic/FastAPI. Describes the contract with a client.	Pydantic (per-request, in memory only)
docker run --name fdp-test -e POSTGRES_PASSWORD=test123 -e POSTGRES_DB=fdp -p 5432:5432 -v ${PWD}/db/init.sql:/docker-entrypoint-initdb.d/init.sql -d postgres