from psycopg.types.json import Jsonb

from services.database import get_connection


def save_game(name, state, save_id=None): 
    """Creates a new save or updates the existing one."""
    score = state["score"]
    lines = state["lines"]
    level = lines // 10 + 1

    with get_connection() as conn:
        with conn.cursor() as cur:
            if save_id is None:
                # Creates a new save.
                cur.execute(
                    """
                    INSERT INTO game_saves
                        (name, score, lines, level, game_state)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (name, score, lines, level, Jsonb(state)),
                )
            else:
                # We are updating the existing save.
                cur.execute(
                    """
                    UPDATE game_saves
                    SET name = %s,
                        score = %s,
                        lines = %s,
                        level = %s,
                        game_state = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    RETURNING id
                    """,
                    (name, score, lines, level, Jsonb(state), save_id),
                )

            row = cur.fetchone()

            if row is None:
                raise ValueError(
                    f"Сохранение с ID {save_id} не найдено"
                )

            return row[0]

def get_save(save_id): 
    """Returns one save by ID or None if it doesn’t exist."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, game_state
                FROM game_saves
                WHERE id = %s
                """,
                (save_id,),
            )
            row = cur.fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "name": row[1],
                "game_state": row[2],
            }
            
def list_saves(): 
    """Returns a list of saves, starting with the most recent ones."""
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, score, lines, level,
                    created_at, updated_at
                FROM game_saves
                ORDER BY updated_at DESC, id DESC
                """
            )

            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "score": row[2],
                    "lines": row[3],
                    "level": row[4],
                    "created_at": row[5],
                    "updated_at": row[6],
                }
                for row in rows
            ]

def delete_save(save_id): 
    """Deletes the save. Returns True if it existed."""
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM game_saves
                WHERE id = %s
                RETURNING id
                """,
                (save_id,),
            )

            return cur.fetchone() is not None
        
def get_latest_save(): 
    """Returns the last saved state or None."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, game_state
                FROM game_saves
                ORDER BY updated_at DESC, id DESC
                LIMIT 1
                """
            )

            row = cur.fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "name": row[1],
                "game_state": row[2],
            }
