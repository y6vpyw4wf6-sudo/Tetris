from services.database import get_connection


def save_score(score, lines, level):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO scores (score, lines, level)
                VALUES (%s, %s, %s)
                """,
                (score, lines, level)
            )