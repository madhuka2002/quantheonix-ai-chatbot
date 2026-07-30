import asyncio

from sqlalchemy import text

from app.db.session import AsyncSessionFactory


async def main() -> None:
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            text("""
                SELECT
                    c.id,
                    c.user_id,
                    u.email
                FROM conversations c
                JOIN users u
                    ON c.user_id = u.id
                ORDER BY c.created_at;
            """)
        )

        rows = result.fetchall()

        print(f"\nFound {len(rows)} conversations\n")

        for row in rows:
            print(
                f"Conversation: {row.id}\n"
                f"User ID     : {row.user_id}\n"
                f"Email       : {row.email}\n"
            )


if __name__ == "__main__":
    asyncio.run(main())