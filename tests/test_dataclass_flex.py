import pytest
from dataclass_flex import create_dataclass_wrapper
from dataclasses import dataclass

# Define some dataclasses for testing
@dataclass
class A:
    x: int

@dataclass
class B:
    y: str

# Define a conversion function for testing
def a_to_b(a: A) -> B:
    return B(str(a.x))

def b_to_a(b: B) -> A:
    return A(int(b.y))

# Create a wrapper with our conversion functions
wrapper = create_dataclass_wrapper({(A, B): a_to_b, (B, A): b_to_a})

# Define a function to test
@wrapper
def test_func(a: A) -> str:
    return a.x

def test_wrapper():
    # Test conversion from A to A
    a = A(1)
    assert test_func(a) == 1

    # Test conversion from B to A
    b = B('2')
    assert test_func(b) == 2

    # # Test conversion from incompatible type
    # with pytest.raises(ValueError):
    #     test_func('3')
