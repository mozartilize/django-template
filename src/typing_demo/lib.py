from typing import TYPE_CHECKING, TypeVar, overload, Any
from decimal import Decimal
if TYPE_CHECKING:
    from _typeshed import SupportsAdd


T_contra = TypeVar("T_contra", contravariant=True)
T_co = TypeVar("T_co", covariant=True)


@overload
def add(x: "SupportsAdd[T_contra, T_co]", y: T_contra) -> T_co: ...

@overload
def add(x: T_contra, y: "SupportsAdd[T_contra, T_co]") -> T_co: ...

def add(x: Any, y: Any) -> Any:
    return x + y


if __name__ == "__main__":
    result = add(7, 10.0)

    x = Decimal("10.0")
    y = add(10, x)

    add(19, "abc")
