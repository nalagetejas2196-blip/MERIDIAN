# Python Object-Oriented Programming Fundamentals

## Classes and Encapsulation
In Python, classes provide a means of bundling data and functionality together. Creating a new class creates a new type of object, allowing new instances of that type to be made. Each class instance can have attributes attached to it for maintaining its state.

Classes are defined using the `class` keyword. The `__init__` constructor method initializes instance attributes upon instantiation.
Encapsulation allows attributes to be protected from unintended direct external modification using conventions like leading underscores (`_protected_attr`).

## Inheritance and Polymorphism
Inheritance enables a new class (derived or child class) to inherit attributes and methods from an existing parent class.
This promotes code reuse and architectural modularity. Polymorphism allows methods in child classes to share the same interface while providing specialized implementations.

```python
class Animal:
    def __init__(self, name: str):
        self.name = name
    def speak(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says Woof!"
```

## Abstract Base Classes and Typing
Using Python's `abc` module and type hints (`typing.List`, `typing.Optional`, `typing.Dict`) ensures explicit contracts and static type safety across large modular applications such as FastAPI and Pydantic validation models.
