import pytest


def test_equal_or_not_equal():
    assert 1 + 1 == 2
    assert 2 * 2 != 5
    
def test_is_instance():
    assert isinstance("hello", str)
    assert not isinstance(123, str)
    
def  test_boolean():
    validate = True
    assert validate is True
    assert ('hello' == 'world') is False
    
def test_type():
    assert type('hello' is str)
    assert type('world' is not int)
def test_greater_and_less_than():
    assert 5 > 3
    assert 2 < 4
    assert 10 >= 10
    assert 3 <= 5
    
def test_list():
    num_list = [1, 2, 3, 4, 5]
    any_list =[False, False]
    assert 3 in num_list
    assert 6 not in num_list
    assert all(num_list)
    assert not any(any_list)


class student:
    def __init__(self, first_name:str, last_name:str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years

@pytest.fixture
def default_employee():  
    return student("John", "Doe", "Computer Science", 3)
     
    
    
        
def test_student_instance(default_employee):
    assert default_employee.first_name == "John", 'First name should be John'
    assert  default_employee.last_name == "Doe", 'Last name should be Doe'
    assert   default_employee.major == "Computer Science"
    assert  default_employee.years == 3