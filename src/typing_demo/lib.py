from typing import TYPE_CHECKING, TypeVar, Protocol, overload, Union, Any, Optional, cast, Type
from abc import abstractmethod
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


# class X: ...

# class Y: ...

# x = X()

# total = x + Y()

# x.hello()

# add(19, 'abc')


# def foo(items: list[int]) -> str:
#     for item in items:
#         items.append(items)
#     return item

# foo.startswith('bar')  # No error


add(7, 10.0)

x = Decimal("10.0")
y: int
add(10, x)


from typing import TypeVar, Generic


class Liquid:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    @abstractmethod
    def __add__(self, matter: "Liquid") -> "Liquid": ...


class Water(Liquid):
    @overload
    def __add__(self, matter: "Water") -> "Water": ...

    @overload
    def __add__(self, matter: "Beer") -> "Beer": ...

    @overload
    def __add__(self, matter: "Coke") -> "Coke": ...

    def __add__(self, matter: Any) -> Any:
        if isinstance(matter, Water):
            self.amount += matter.amount
            return self
        else:
            return matter.__class__(self.amount + matter.amount)


class Beer(Liquid):
    @overload
    def __add__(self, matter: "Beer | Water") -> "Beer": ...

    @overload
    def __add__(self, matter: "Coke") -> "Mixed": ...

    def __add__(self, matter: Any) -> Any:
        if isinstance(matter, Beer):
            self.amount += matter.amount
            return self
        else:
            return Mixed(self.amount + matter.amount)


class Coke(Liquid):
    @overload
    def __add__(self, matter: "Coke | Water") -> "Coke": ...

    @overload
    def __add__(self, matter: "Beer") -> "Mixed": ...

    def __add__(self, matter: Any) -> Any:
        if isinstance(matter, (Coke, Water)):
            self.amount += matter.amount
            return self
        else:
            return Mixed(self.amount + matter.amount)


class Mixed(Liquid):
    def __add__(self, matter: Liquid) -> "Mixed":
        self.amount += matter.amount
        return self


class Tea(Liquid):
    def __add__(self, matter: "Liquid") -> "Liquid":
        return super().__add__(matter)


Drink = TypeVar("Drink", Water, Coke, Beer)


class Base(Generic[Drink]): ...


class CupOverflowError(Exception): ...


class Cup(Generic[Drink]):
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.matter: Optional[Drink] = None

    def receive(self, x: Drink):
        if not self.matter:
            self.matter: Drink = self.__orig_class__.__args__[0](0)
        self.matter = cast(Drink, self.matter)
        self.matter += x  # type: ignore
        if self.matter.amount > self.capacity:
            self.matter.amount = self.capacity
            raise CupOverflowError()

    @overload
    def drank(self, amount: str) -> None: ...
    @overload
    def drank(self, amount: int) -> None: ...

    def drank(self, amount: int | str):
        if not self.matter:
            raise ValueError("Empty cup")
        if isinstance(amount, str):
            percentage = float(amount[:-1])
            _amount = int(self.matter.amount * percentage / 100)
        else:
            _amount = amount
        self.matter.amount -= _amount
