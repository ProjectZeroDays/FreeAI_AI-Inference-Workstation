---
name: refactoring-patterns
description: Code refactoring techniques, design patterns, code smell detection, and safe transformation strategies. Use when the user asks about improving code quality, applying design patterns, detecting code smells, extracting functions, renaming, or restructuring code.
---

# Refactoring Patterns

## Code Smells → Refactoring

| Smell | Refactoring |
|-------|-------------|
| Long Method | Extract Function |
| Large Class | Extract Class |
| Duplicated Code | Pull Up Method / Extract Function |
| Long Parameter List | Introduce Parameter Object |
| Feature Envy | Move Method |
| Data Clumps | Extract Class |
| Primitive Obsession | Replace Primitive with Value Object |
| Switch Statements | Replace Conditional with Polymorphism |
| Speculative Generality | Remove Unused Code |
| Dead Code | Delete |

## Extract Function

```python
# Before
def print_owing(invoice):
    outstanding = 0
    print("***********************")
    print("**** Customer Owes ****")
    print("***********************")
    for item in invoice.items:
        outstanding += item.amount
    print(f"name: {invoice.customer}")
    print(f"amount: {outstanding}")

# After
def print_owing(invoice):
    outstanding = 0
    print_banner()
    outstanding = calculate_outstanding(invoice)
    print_details(invoice, outstanding)

def print_banner():
    print("***********************")
    print("**** Customer Owes ****")
    print("***********************")

def calculate_outstanding(invoice):
    return sum(item.amount for item in invoice.items)

def print_details(invoice, outstanding):
    print(f"name: {invoice.customer}")
    print(f"amount: {outstanding}")
```

## Replace Conditional with Polymorphism

```python
# Before
class Bird:
    def __init__(self, type):
        self.type = type

    def plumage(self):
        if self.type == "european":
            return "average"
        elif self.type == "north_russian":
            return "beautiful"
        elif self.type == "african":
            return "poor"

# After
class Bird:
    @property
    def plumage(self):
        return self._plumage

class EuropeanSwallow(Bird):
    @property
    def plumage(self):
        return "average"

class NorthRussianSwallow(Bird):
    @property
    def plumage(self):
        return "beautiful"

class AfricanSwallow(Bird):
    @property
    def plumage(self):
        return "poor"
```

## Introduce Parameter Object

```python
# Before
def create_booking(start_date, end_date, start_time, end_time):
    ...

# After
class DateRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        if start > end:
            raise ValueError("Start must be before end")

    @property
    def duration_days(self):
        return (self.end - self.start).days

def create_booking(dates: DateRange, times: TimeRange):
    ...
```

## Extract Class

```python
# Before
class Person:
    def __init__(self, name, office_area_code, office_number):
        self.name = name
        self.office_area_code = office_area_code
        self.office_number = office_number

    def get_telephone_number(self):
        return f"({self.office_area_code}) {self.office_number}"

# After
class TelephoneNumber:
    def __init__(self, area_code, number):
        self.area_code = area_code
        self.number = number

    def __str__(self):
        return f"({self.area_code}) {self.number}"

class Person:
    def __init__(self, name, area_code, number):
        self.name = name
        self.office_telephone = TelephoneNumber(area_code, number)

    def get_telephone_number(self):
        return str(self.office_telephone)
```

## Replace Temp with Query

```python
# Before
def price(self):
    base_price = self.quantity * self.item_price
    if base_price > 1000:
        return base_price * 0.95
    return base_price

# After
def price(self):
    if self.base_price > 1000:
        return self.base_price * 0.95
    return self.base_price

@property
def base_price(self):
    return self.quantity * self.item_price
```

## Decompose Conditional

```python
# Before
if date.before(SUMMER_START) or date.after(SUMMER_END):
    charge = quantity * winter_rate + winter_service_charge
else:
    charge = quantity * summer_rate

# After
if is_winter(date):
    charge = winter_charge(quantity)
else:
    charge = summer_charge(quantity)
```

## Consolidate Duplicate Conditional Fragments

```python
# Before
if is_special_deal():
    total = price * 0.9
    send_special_offer_email()
else:
    total = price * 0.95
    send常规_email()

# After
total = calculate_total()
send_email()
```

## Safe Refactoring Checklist

1. Ensure tests pass before refactoring
2. Make small changes, test after each
3. Never mix refactoring with feature changes
4. Use version control — commit before each refactor step
5. If tests don't exist, write characterization tests first
6. Use IDE refactoring tools when available (rename, extract)
7. Review each step — does behavior remain identical?
