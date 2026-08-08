"""Demo data seeding.

Startup (`seed_demo_user` in lifespan) only creates the admin when `users` is empty.

Richer sample users + books are opt-in via:

    python -m app.seed
    make seed
"""

from __future__ import annotations

import asyncio

from app.auth.passwords import hash_password
from app.auth.seed import seed_demo_user
from app.auth.users import create_user, get_user_by_username
from app.db import books as books_repo
from app.db.connection import close_sqlite, connect_to_sqlite, get_connection

# Shared password for sample non-admin accounts (documented in README).
SAMPLE_PASSWORD = "demo123"

SAMPLE_USERS: list[tuple[str, str, str]] = [
    ("viewer", SAMPLE_PASSWORD, "viewer"),
    ("editor", SAMPLE_PASSWORD, "editor"),
]

# More than the UI default page size (10) so pagination is obvious (~3 pages).
SAMPLE_BOOKS: list[dict[str, object]] = [
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "year": 1813,
        "notes": "Classic novel of manners.",
    },
    {
        "title": "The Hobbit",
        "author": "J. R. R. Tolkien",
        "year": 1937,
        "notes": "There and back again.",
    },
    {
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "notes": "Desert planet politics and spice.",
    },
    {
        "title": "Neuromancer",
        "author": "William Gibson",
        "year": 1984,
        "notes": "Cyberpunk cornerstone.",
    },
    {
        "title": "The Left Hand of Darkness",
        "author": "Ursula K. Le Guin",
        "year": 1969,
        "notes": "Ambassador on a winter world.",
    },
    {
        "title": "Kindred",
        "author": "Octavia E. Butler",
        "year": 1979,
        "notes": "Time travel and American history.",
    },
    {
        "title": "The Name of the Rose",
        "author": "Umberto Eco",
        "year": 1980,
        "notes": "Monastery mystery.",
    },
    {
        "title": "Invisible Cities",
        "author": "Italo Calvino",
        "year": 1972,
        "notes": "Marco Polo describes cities to Kublai Khan.",
    },
    {
        "title": "Frankenstein",
        "author": "Mary Shelley",
        "year": 1818,
        "notes": "Creature and creator.",
    },
    {
        "title": "Dracula",
        "author": "Bram Stoker",
        "year": 1897,
        "notes": "Epistolary vampire novel.",
    },
    {
        "title": "Moby-Dick",
        "author": "Herman Melville",
        "year": 1851,
        "notes": "Obsession at sea.",
    },
    {
        "title": "Jane Eyre",
        "author": "Charlotte Brontë",
        "year": 1847,
        "notes": "Gothic bildungsroman.",
    },
    {
        "title": "Wuthering Heights",
        "author": "Emily Brontë",
        "year": 1847,
        "notes": "Stormy moorland passions.",
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "year": 1949,
        "notes": "Surveillance and Newspeak.",
    },
    {
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "year": 1932,
        "notes": "Engineered happiness.",
    },
    {
        "title": "Fahrenheit 451",
        "author": "Ray Bradbury",
        "year": 1953,
        "notes": "Firemen who burn books.",
    },
    {
        "title": "The Handmaid's Tale",
        "author": "Margaret Atwood",
        "year": 1985,
        "notes": "Gilead and resistance.",
    },
    {
        "title": "Beloved",
        "author": "Toni Morrison",
        "year": 1987,
        "notes": "Memory and haunting.",
    },
    {
        "title": "One Hundred Years of Solitude",
        "author": "Gabriel García Márquez",
        "year": 1967,
        "notes": "Macondo across generations.",
    },
    {
        "title": "The Stranger",
        "author": "Albert Camus",
        "year": 1942,
        "notes": "Absurdity in Algiers.",
    },
    {
        "title": "Crime and Punishment",
        "author": "Fyodor Dostoevsky",
        "year": 1866,
        "notes": "Guilt after a crime.",
    },
    {
        "title": "The Trial",
        "author": "Franz Kafka",
        "year": 1925,
        "notes": "Arrested without knowing why.",
    },
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "year": 1960,
        "notes": "Justice in Maycomb.",
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "year": 1925,
        "notes": "Jazz Age longing.",
    },
    {
        "title": "Mrs Dalloway",
        "author": "Virginia Woolf",
        "year": 1925,
        "notes": "One day in London.",
    },
    {
        "title": "Things Fall Apart",
        "author": "Chinua Achebe",
        "year": 1958,
        "notes": "Igbo life and colonial rupture.",
    },
    {
        "title": "The Dispossessed",
        "author": "Ursula K. Le Guin",
        "year": 1974,
        "notes": "Anarres and Urras.",
    },
    {
        "title": "Hyperion",
        "author": "Dan Simmons",
        "year": 1989,
        "notes": "Pilgrims to the Time Tombs.",
    },
]

async def seed_sample_users() -> list[str]:
    """Create sample role users if missing. Returns usernames created."""
    created: list[str] = []
    for username, password, role in SAMPLE_USERS:
        if await get_user_by_username(username) is not None:
            continue
        await create_user(username, hash_password(password), role=role)
        created.append(username)
    return created


async def _existing_book_titles() -> set[str]:
    conn = get_connection()
    async with conn.execute("SELECT title FROM books") as cursor:
        rows = await cursor.fetchall()
    return {row["title"] for row in rows}


async def seed_sample_books() -> int:
    """Insert sample books whose titles are not already present. Returns count inserted."""
    existing = await _existing_book_titles()
    added = 0
    for book in SAMPLE_BOOKS:
        title = str(book["title"])
        if title in existing:
            continue
        await books_repo.create_book(
            title=title,
            author=str(book["author"]),
            year=book["year"] if book["year"] is not None else None,  # type: ignore[arg-type]
            notes=str(book["notes"]) if book.get("notes") else None,
        )
        existing.add(title)
        added += 1
    return added


async def run_seed() -> None:
    """Connect, ensure demo admin, add sample users/books (idempotent), disconnect."""
    await connect_to_sqlite()
    try:
        await seed_demo_user()
        created_users = await seed_sample_users()
        books_added = await seed_sample_books()

        if created_users:
            print(
                f"✅ Seeded users: {', '.join(created_users)} "
                f"(password {SAMPLE_PASSWORD!r})"
            )
        else:
            print("ℹ️  Sample users already present (viewer, editor)")

        if books_added:
            print(
                f"✅ Seeded {books_added} books "
                f"({len(SAMPLE_BOOKS)} samples defined; UI page size is 10)"
            )
        else:
            print("ℹ️  All sample book titles already present")
    finally:
        await close_sqlite()


def main() -> None:
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()
