from typing import Generic, TypeVar, List, Optional
from app.schemas.base import CamelModel

T = TypeVar("T")

class ApiResponse(CamelModel, Generic[T]):
    data: T
    message: Optional[str] = None
    error: Optional[str] = None

class PaginatedResponse(CamelModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
