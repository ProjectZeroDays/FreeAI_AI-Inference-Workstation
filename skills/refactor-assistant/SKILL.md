---
name: refactor-assistant
description: Smart refactoring: extract functions, rename, restructure, improve readability. Use when the user asks to refactor code, extract functions, rename variables, restructure modules, or improve code readability.
---

# Refactor Assistant

## Refactoring Principles

1. **Preserve behavior** — all tests must pass after every step
2. **Small incremental changes** — one refactor per commit
3. **Read-only first** — analyze before modifying
4. **Name intent** — rename to reveal purpose, not mechanics

## Refactor Catalog

### Extract Function

Identify a code block with a single responsibility and extract it.

```python
# BEFORE
def process_order(order):
    total = 0
    for item in order.items:
        price = item.price * item.quantity
        if order.coupon:
            price *= order.coupon.discount
        total += price
    if total > 100:
        total *= 0.9
    tax = total * order.tax_rate
    return total + tax

# AFTER
def process_order(order):
    subtotal = _calculate_subtotal(order)
    discount = _apply_volume_discount(subtotal)
    return subtotal - discount + _calculate_tax(subtotal - discount, order)

def _calculate_subtotal(order):
    total = 0
    for item in order.items:
        price = item.price * item.quantity
        if order.coupon:
            price *= order.coupon.discount
        total += price
    return total

def _apply_volume_discount(total):
    return total * 0.1 if total > 100 else 0

def _calculate_tax(amount, order):
    return amount * order.tax_rate
```

### Rename

Use when a name obscures intent.

```typescript
// BEFORE
const d = new Date();
const arr = getData();
let x = process(arr);

// AFTER
const createdAt = new Date();
const rawRecords = getData();
let processedResult = process(rawRecords);
```

### Extract Class

Use when a class handles multiple responsibilities.

```python
# BEFORE — God class
class OrderService:
    def create_order(self, data): ...
    def validate(self, data): ...
    def send_confirmation(self, order): ...
    def calculate_tax(self, order): ...
    def log_activity(self, msg): ...

# AFTER — Split by responsibility
class OrderService:
    def create_order(self, data):
        validated = self.validator.validate(data)
        order = self._persist(validated)
        self.confirmation_sender.send(order)
        self.logger.log(f"Order created: {order.id}")
        return order

class OrderValidator: ...
class OrderConfirmationSender: ...
class OrderTaxCalculator: ...
```

### Inline Method

Use when a wrapper adds no value.

```python
# BEFORE
def get_user_name(user):
    return user.name

def print_user(user):
    print(get_user_name(user))

# AFTER
def print_user(user):
    print(user.name)
```

### Replace Temp with Query

```python
# BEFORE
total = price * quantity
discount = total * 0.1
final = total - discount
tax = final * 0.08
grand_total = final + tax

# AFTER
def calculate_total(price, quantity):
    subtotal = price * quantity
    discount = subtotal * 0.1
    return subtotal - discount

def calculate_tax(amount):
    return amount * 0.08

grand_total = calculate_total(price, quantity) + calculate_tax(calculate_total(price, quantity))
```

### Split Loop

```javascript
// BEFORE
for (const item of items) {
    validate(item);
    total += item.price;
    log(item);
    save(item);
}

// AFTER
for (const item of items) {
    validate(item);
}
for (const item of items) {
    total += item.price;
}
for (const item of items) {
    log(item);
    save(item);
}
```

### Replace Conditional with Polymorphism

```python
# BEFORE
def get_price(item, customer):
    if customer.is_vip:
        return item.price * 0.8
    elif customer.is_wholesale:
        return item.price * 0.9
    else:
        return item.price

# AFTER
class PricingStrategy:
    def calculate(self, item, customer):
        raise NotImplementedError

class StandardPricing(PricingStrategy):
    def calculate(self, item, customer):
        return item.price

class VIPPricing(PricingStrategy):
    def calculate(self, item, customer):
        return item.price * 0.8
```

## Refactor Workflow

### Step 1: Identify Target

```
Look for:
- Functions longer than 20 lines
- Duplicate code blocks (copy-paste smell)
- Names that don't match usage
- Classes with more than 5 responsibilities
- Deep nesting (more than 3 levels)
- Magic numbers and strings
- Long parameter lists (> 4 params)
```

### Step 2: Verify Safety Net

```bash
# Ensure tests exist before refactoring
pytest tests/ -q
# or
npm test -- --passWithNoTests
```

If no tests exist, write a characterization test first:

```python
def test_order_processing_preserves_behavior():
    order = build_test_order()
    result = process_order(order)
    assert result.total == expected_total
    assert result.tax == expected_tax
```

### Step 3: Apply Single Refactor

Make one change, run tests, commit.

### Step 4: Verify

```bash
# Run full test suite
pytest tests/
# Run type checker
mypy src/
# Run linter
ruff check src/
```

## Common Refactoring Patterns

### Null Object Pattern

```python
# BEFORE
if user.role == 'admin':
    permissions = get_admin_permissions()
else:
    permissions = []

# AFTER
class NullUser:
    @property
    def role(self): return 'guest'
    def get_permissions(self): return []

# Then: user.get_permissions() always works
```

### Sentinel Pattern

```python
# BEFORE
def find_user(user_id):
    for u in users:
        if u.id == user_id:
            return u
    return None  # caller must check

# AFTER
class NotFound:
    def __repr__(self): return "<NotFound>"

NOT_FOUND = NotFound()

def find_user(user_id):
    for u in users:
        if u.id == user_id:
            return u
    return NOT_FOUND  # explicit, no None checks needed
```

### Strategy Pattern

```python
from enum import Enum

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    CRYPTO = "crypto"

class PaymentStrategy:
    def pay(self, amount: float) -> bool: ...

class CreditCardStrategy(PaymentStrategy): ...
class PayPalStrategy(PaymentStrategy): ...
class CryptoStrategy(PaymentStrategy): ...
```

## Safety Checklist

- [ ] Tests exist and pass before starting
- [ ] Each refactor is a separate commit
- [ ] No behavior changes (only structure)
- [ ] Linter passes after each step
- [ ] Type checker passes after each step
- [ ] No new dependencies introduced
- [ ] Public API surface unchanged (unless intentional)
