from typing import Protocol, TypeVar, overload, Any, Optional, cast, Generic
from abc import abstractmethod, ABC


TLiquid = TypeVar("TLiquid", bound="Liquid")


class Liquid(ABC):
    def __init__(self, amount: int) -> None:
        self.amount = amount

    @abstractmethod
    def __add__(self: TLiquid, matter: "Liquid") -> TLiquid: ...


class PLiquid(Protocol):
    amount: int

    # protocols can have concrete methods
    def __init__(self, amount: int) -> None:
        self.amount = amount

    # @abstractmethod
    def __add__(self, matter: "PLiquid") -> "PLiquid": ...


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
    def __add__(self, matter: Liquid):
        if isinstance(matter, (Beer, Water)):
            self.amount += matter.amount
            return self
        raise ValueError()


class Coke(Liquid):
    def __add__(self, matter: Liquid):
        if isinstance(matter, (Coke, Water)):
            self.amount += matter.amount
            return self
        raise ValueError()


class Mixed(Liquid):
    # unable to detect missing implementation of abstract methods
    pass


class Tea(PLiquid):
    # inheriting from protocol needed to implement all attributes/methods
    pass


class Coffee(PLiquid):
    def __add__(self, matter: "PLiquid") -> "PLiquid":
        # error on super call to abtract method
        return super().__add__(matter)


Drink = TypeVar("Drink", Water, Coke, Beer)


class CupOverflowError(Exception): ...


class Cup(Generic[Drink]):
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._matter: Optional[Drink] = None

    @property
    def matter(self):
        if not self._matter:
            self._matter = self.__orig_class__.__args__[0](0)  # type: ignore
        return cast(Drink, self._matter)  # type: ignore

    @matter.setter
    def matter(self, value: Drink):
        self._matter = value

    def receive(self, x: Drink):
        self.matter += x
        if self.matter.amount > self.capacity:
            self.matter.amount = self.capacity
            raise CupOverflowError()

    def drank(self, amount: int | str):
        if not self.matter:
            raise ValueError("Empty cup")
        if isinstance(amount, str):
            percentage = float(amount[:-1])
            _amount = int(self.matter.amount * percentage / 100)
        else:
            _amount = amount
        self.matter.amount -= _amount


if __name__ == "__main__":
    mycup = Cup[Water](100)

    mycup.receive(Water(100))
    mycup.receive(Beer(100))
