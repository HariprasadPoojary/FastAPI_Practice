from typing import Annotated

from fastapi import APIRouter, Query, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import PlainTextResponse

router = APIRouter()


def cpu_heavy(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@router.get("/compute", summary="Run blocking work safely in a thread (v2).")
async def compute(
    n: Annotated[int, Query(ge=1, le=40, description="Fibonacci position.")],
) -> dict[str, int]:
    result = await run_in_threadpool(cpu_heavy, n)
    return {"fib": result}


@router.get(
    "/health",
    response_class=PlainTextResponse,
    summary="Plain-text health check with headers.",
)
def health_check(response: Response) -> str:
    response.headers["Cache-Control"] = "no-store"
    response.set_cookie("app", "fastapi", httponly=True)
    return "ok"
