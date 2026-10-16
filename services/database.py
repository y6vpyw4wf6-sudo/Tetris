import psycopg


CONN_STR = "host=localhost dbname=tetris user=postgres password=postgres"

def get_connection():
    return psycopg.connect(CONN_STR)