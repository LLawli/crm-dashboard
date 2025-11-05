import duckdb

con = duckdb.connect(database=':memory:', read_only=False)
db = duckdb.connect(database="data/persisten.db", read_only=False)

def init_db():
    con.execute('''
CREATE TABLE leads (
                id INTEGER PRIMARY KEY,
                lead INTEGER,
                price DOUBLE,
                status_id INTEGER,
                pipeline_id INTEGER,
                closed_at TIMESTAMP,
                created_at TIMESTAMP,
                utm_source VARCHAR,
                utm_medium VARCHAR,
                utm_campaign VARCHAR,
                utm_content VARCHAR,
                utm_term VARCHAR
                );
''')
    
    db.execute('''
CREATE TABLE IF NOT EXISTS campaigns (
               id INTEGER PRIMARY KEY,
               name VARCHAR); INSERT OR IGNORE INTO campaigns (id, name) VALUES (1, ?), (2, ?);
''', ["emagrecimento-0710-leads", "emagrecimento-3110-leads"])