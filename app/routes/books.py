"""JSON CRUD for SQLite-backed books (mounted at /api/books)."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.deps import require_editor, require_user
from app.db import books as books_repo
from app.models.book import BookCreate, BookResponse, BookUpdate, PaginatedBooks

router = APIRouter()


def _parse_response(row: dict) -> BookResponse:
    return BookResponse(
        id=row["id"],
        title=row["title"],
        author=row["author"],
        year=row["year"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.post(
    "/",
    response_model=BookResponse,
    status_code=201,
    summary="Create a book",
)
async def create_book(
    book: BookCreate,
    _user: dict = Depends(require_editor),
) -> BookResponse:
    row = await books_repo.create_book(
        book.title, book.author, year=book.year, notes=book.notes
    )
    return _parse_response(row)


@router.get(
    "/",
    response_model=PaginatedBooks,
    summary="List books",
)
async def list_books(
    _user: dict = Depends(require_user),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    q: str | None = Query(None, description="Search title or author"),
) -> PaginatedBooks:
    rows, total = await books_repo.list_books(page=page, size=size, q=q)
    return PaginatedBooks(
        items=[_parse_response(r) for r in rows],
        total_count=total,
        page=page,
        size=size,
        total_pages=books_repo.total_pages(total, size),
    )


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Get a book",
)
async def get_book(
    book_id: str,
    _user: dict = Depends(require_user),
) -> BookResponse:
    row = await books_repo.get_book(book_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    return _parse_response(row)


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="Update a book",
)
async def update_book(
    book_id: str,
    book_update: BookUpdate,
    _user: dict = Depends(require_editor),
) -> BookResponse:
    data = book_update.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    row = await books_repo.update_book(
        book_id,
        title=data.get("title"),
        author=data.get("author"),
        year=data.get("year"),
        year_set="year" in data,
        notes=data.get("notes"),
        notes_set="notes" in data,
    )
    if row is None:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    return _parse_response(row)


@router.delete(
    "/{book_id}",
    status_code=204,
    summary="Delete a book",
)
async def delete_book(
    book_id: str,
    _user: dict = Depends(require_editor),
) -> None:
    deleted = await books_repo.delete_book(book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
