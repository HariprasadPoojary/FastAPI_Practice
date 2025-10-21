from typing import Iterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/stream", tags=["v2: stream"])


def generate_csv(rows: int = 1000) -> Iterator[bytes]:
    yield b"id,name\n"
    for i in range(1, rows + 1):
        line = f"{i},Item {i}\n"
        yield line.encode("utf-8")


@router.get("/items.csv", summary="Stream a CSV export.")
def stream_items_csv() -> StreamingResponse:
    return StreamingResponse(
        generate_csv(rows=10000),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="items.csv"'},
    )


@router.get("/items.txt", summary="Stream a plain text export.")
def stream_items_txt() -> StreamingResponse:
    return StreamingResponse(
        generate_csv(rows=10000),
        media_type="text/plain",
        headers={"Content-Disposition": 'attachment; filename="items.txt"'},
    )


@router.get("/items.json", summary="Stream a JSON export.")
def stream_items_json() -> StreamingResponse:
    def generate_json(rows: int = 1000) -> Iterator[bytes]:
        yield b"[\n"
        for i in range(1, rows + 1):
            line = f'  {{"id": {i}, "name": "Item {i}"}}'
            if i < rows:
                line += ","
            line += "\n"
            yield line.encode("utf-8")
        yield b"]\n"

    return StreamingResponse(
        generate_json(rows=10000),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="items.json"'},
    )


# Note: In production, consider using proper CSV/JSON libraries and handle errors.
# Also, for large datasets, consider using database cursors or pagination to fetch data in chunks.