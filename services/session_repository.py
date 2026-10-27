from services.database import get_connection


def save_session(
    started_at,
    ended_at,
    duration_seconds,
    score,
    lines,
    level,
    end_reason,
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sessions (
                    started_at,
                    ended_at,
                    duration_seconds,
                    score,
                    lines,
                    level,
                    end_reason
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    started_at,
                    ended_at,
                    duration_seconds,
                    score,
                    lines,
                    level,
                    end_reason,
                ),
            )