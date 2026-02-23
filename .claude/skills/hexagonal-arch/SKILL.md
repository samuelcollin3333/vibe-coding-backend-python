---
name: hexagonal-arch
description: Hexagonal/DDD architecture patterns for Python. Use when creating entities, rules, use cases, repositories, or any domain code. Keywords: entity, rule, usecase, handler, command, repository, domain, aggregate.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Hexagonal Architecture for AI-Assisted Development

## Philosophy

This architecture is optimized for AI-assisted development (vibe coding). Core principles:

1. **Visible factorization**: Business rules are pure functions, explicitly imported
2. **Local understanding**: One file = complete understanding (no hidden inheritance)
3. **Predictable patterns**: Same structure everywhere = pattern matching for AI
4. **Grep-friendly**: `grep "canBeCancelled"` finds the rule AND all usages

## Layer Responsibilities

### Domain Layer (`src/domain/`)
- **Entities**: Immutable data structures representing business concepts
- **Rules**: Pure static functions containing ALL business logic
- **Repository interfaces**: Protocols defining data access contracts
- **Value Objects**: Immutable typed values (Money, Email, OrderId)

### Application Layer (`src/application/`)
- **Commands**: Immutable DTOs carrying intent
- **Handlers**: Orchestrate the flow, import rules explicitly
- **NEVER contains business logic** - delegates to Rules

### Infrastructure Layer (`src/infrastructure/`)
- **Repository implementations**: Concrete data access
- **External services**: APIs, messaging, etc.
- **NEVER imported by Domain or Application**

### Shared (`src/shared/`)
- **Errors**: Domain exceptions hierarchy
- **Types**: Common type definitions
- **Events**: Domain event definitions

## File Structure Pattern

```
src/
├── domain/
│   └── {entity}/
│       ├── __init__.py
│       ├── {entity}.py              # Entity + Value Objects
│       ├── {entity}_rules.py        # Pure business rules
│       └── {entity}_repository.py   # Protocol interface
├── application/
│   └── {entity}/
│       └── {action}_{entity}/
│           ├── __init__.py
│           ├── command.py           # Input DTO
│           └── handler.py           # Use case orchestration
├── infrastructure/
│   └── persistence/
│       └── {entity}_repository_impl.py
└── shared/
    ├── errors.py
    ├── types.py
    └── events.py

tests/
├── unit/
│   └── domain/
│       └── {entity}/
│           └── test_{entity}_rules.py
└── integration/
    └── application/
        └── {entity}/
            └── test_{action}_{entity}_handler.py
```

## Complete Example: Order Entity

### 1. Entity (`src/domain/order/order.py`)

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NewType
from uuid import UUID

# Value Objects
OrderId = NewType("OrderId", UUID)
CustomerId = NewType("CustomerId", UUID)


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class OrderLine:
    product_id: str
    quantity: int
    unit_price_cents: int

    @property
    def total_cents(self) -> int:
        return self.quantity * self.unit_price_cents


@dataclass(frozen=True)
class Order:
    id: OrderId
    customer_id: CustomerId
    lines: tuple[OrderLine, ...]
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    @property
    def total_cents(self) -> int:
        return sum(line.total_cents for line in self.lines)

    def with_status(self, new_status: OrderStatus) -> "Order":
        """Return a new Order with updated status."""
        return Order(
            id=self.id,
            customer_id=self.customer_id,
            lines=self.lines,
            status=new_status,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )
```

### 2. Rules (`src/domain/order/order_rules.py`)

```python
"""
Business rules for Order entity.

All rules are pure static functions:
- No side effects
- No external dependencies
- Easily testable in isolation
- Grep-friendly: find rule + all usages
"""

from datetime import datetime, timedelta

from src.domain.order.order import Order, OrderStatus


class OrderRules:
    """Pure business rules for Order operations."""

    CANCELLATION_WINDOW_HOURS = 24
    MINIMUM_ORDER_CENTS = 1000  # 10.00 in cents

    @staticmethod
    def can_be_cancelled(order: Order) -> bool:
        """
        Order can be cancelled if:
        - Status is PENDING or CONFIRMED
        - Less than 24 hours since creation
        """
        if order.status not in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
            return False

        hours_since_creation = (
            datetime.utcnow() - order.created_at
        ).total_seconds() / 3600

        return hours_since_creation < OrderRules.CANCELLATION_WINDOW_HOURS

    @staticmethod
    def can_be_confirmed(order: Order) -> bool:
        """Order can be confirmed only if PENDING."""
        return order.status == OrderStatus.PENDING

    @staticmethod
    def validate_minimum_amount(order: Order) -> bool:
        """Order must meet minimum amount requirement."""
        return order.total_cents >= OrderRules.MINIMUM_ORDER_CENTS

    @staticmethod
    def get_cancellation_reason_if_forbidden(order: Order) -> str | None:
        """
        Returns the reason why cancellation is forbidden, or None if allowed.
        Useful for error messages.
        """
        if order.status == OrderStatus.SHIPPED:
            return "Cannot cancel: order already shipped"
        if order.status == OrderStatus.DELIVERED:
            return "Cannot cancel: order already delivered"
        if order.status == OrderStatus.CANCELLED:
            return "Order is already cancelled"

        hours_since_creation = (
            datetime.utcnow() - order.created_at
        ).total_seconds() / 3600

        if hours_since_creation >= OrderRules.CANCELLATION_WINDOW_HOURS:
            return f"Cannot cancel: order is older than {OrderRules.CANCELLATION_WINDOW_HOURS} hours"

        return None
```

### 3. Repository Interface (`src/domain/order/order_repository.py`)

```python
from typing import Protocol

from src.domain.order.order import Order, OrderId


class OrderRepository(Protocol):
    """Interface for Order persistence. Implemented in infrastructure."""

    def find_by_id(self, order_id: OrderId) -> Order | None:
        """Find order by ID, returns None if not found."""
        ...

    def save(self, order: Order) -> None:
        """Persist order (create or update)."""
        ...

    def delete(self, order_id: OrderId) -> None:
        """Delete order by ID."""
        ...
```

### 4. Command (`src/application/order/cancel_order/command.py`)

```python
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CancelOrderCommand:
    """Command to cancel an existing order."""

    order_id: UUID
    cancelled_by_user_id: UUID
    reason: str | None = None
```

### 5. Handler (`src/application/order/cancel_order/handler.py`)

```python
"""
Cancel Order Use Case.

Flow (5 steps - ALWAYS follow this pattern):
1. VALIDATE: Check command is well-formed
2. FETCH: Get required entities from repositories
3. RULES: Apply business rules (import from Rules classes)
4. PERSIST: Save changes
5. EVENTS: Emit domain events (if any)
"""

from dataclasses import dataclass

from src.domain.order.order import OrderId, OrderStatus
from src.domain.order.order_repository import OrderRepository
from src.domain.order.order_rules import OrderRules  # Explicit import!
from src.shared.errors import NotFoundError, BusinessRuleViolation


@dataclass
class CancelOrderResult:
    success: bool
    order_id: OrderId
    message: str


class CancelOrderHandler:
    """Handler for CancelOrderCommand."""

    def __init__(self, order_repository: OrderRepository) -> None:
        self._order_repository = order_repository

    def handle(self, command: "CancelOrderCommand") -> CancelOrderResult:
        """
        Execute the cancel order use case.

        All logic is VISIBLE here - no hidden base class methods.
        """
        # 1. VALIDATE - Command validation
        order_id = OrderId(command.order_id)

        # 2. FETCH - Get entities
        order = self._order_repository.find_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order {order_id} not found")

        # 3. RULES - Apply business rules (explicit import, visible logic)
        if not OrderRules.can_be_cancelled(order):
            reason = OrderRules.get_cancellation_reason_if_forbidden(order)
            raise BusinessRuleViolation(reason or "Order cannot be cancelled")

        # 4. PERSIST - Save changes
        cancelled_order = order.with_status(OrderStatus.CANCELLED)
        self._order_repository.save(cancelled_order)

        # 5. EVENTS - (emit domain events here if needed)
        # self._event_bus.publish(OrderCancelledEvent(order_id=order_id, ...))

        return CancelOrderResult(
            success=True,
            order_id=order_id,
            message="Order successfully cancelled",
        )
```

### 6. Shared Errors (`src/shared/errors.py`)

```python
"""Domain exceptions hierarchy."""


class DomainError(Exception):
    """Base class for all domain errors."""

    pass


class NotFoundError(DomainError):
    """Entity not found."""

    pass


class BusinessRuleViolation(DomainError):
    """Business rule was violated."""

    pass


class ValidationError(DomainError):
    """Input validation failed."""

    pass
```

### 7. Tests (`tests/unit/domain/order/test_order_rules.py`)

```python
"""
Unit tests for OrderRules.

Naming: test_{method}_should_{behavior}_when_{condition}
- Maps directly to the rule being tested
- Grep-friendly: find test for any rule
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from src.domain.order.order import (
    Order,
    OrderId,
    CustomerId,
    OrderLine,
    OrderStatus,
)
from src.domain.order.order_rules import OrderRules


def make_order(
    status: OrderStatus = OrderStatus.PENDING,
    created_at: datetime | None = None,
    total_cents: int = 5000,
) -> Order:
    """Factory for test orders."""
    return Order(
        id=OrderId(uuid4()),
        customer_id=CustomerId(uuid4()),
        lines=(OrderLine(product_id="PROD-1", quantity=1, unit_price_cents=total_cents),),
        status=status,
        created_at=created_at or datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


class TestOrderRulesCanBeCancelled:
    """Tests for OrderRules.can_be_cancelled"""

    def test_can_be_cancelled_should_return_true_when_pending_and_recent(self):
        order = make_order(status=OrderStatus.PENDING)
        assert OrderRules.can_be_cancelled(order) is True

    def test_can_be_cancelled_should_return_true_when_confirmed_and_recent(self):
        order = make_order(status=OrderStatus.CONFIRMED)
        assert OrderRules.can_be_cancelled(order) is True

    def test_can_be_cancelled_should_return_false_when_shipped(self):
        order = make_order(status=OrderStatus.SHIPPED)
        assert OrderRules.can_be_cancelled(order) is False

    def test_can_be_cancelled_should_return_false_when_older_than_24_hours(self):
        old_date = datetime.utcnow() - timedelta(hours=25)
        order = make_order(status=OrderStatus.PENDING, created_at=old_date)
        assert OrderRules.can_be_cancelled(order) is False


class TestOrderRulesValidateMinimumAmount:
    """Tests for OrderRules.validate_minimum_amount"""

    def test_validate_minimum_amount_should_return_true_when_above_minimum(self):
        order = make_order(total_cents=2000)  # 20.00
        assert OrderRules.validate_minimum_amount(order) is True

    def test_validate_minimum_amount_should_return_false_when_below_minimum(self):
        order = make_order(total_cents=500)  # 5.00
        assert OrderRules.validate_minimum_amount(order) is False

    def test_validate_minimum_amount_should_return_true_when_exactly_minimum(self):
        order = make_order(total_cents=OrderRules.MINIMUM_ORDER_CENTS)
        assert OrderRules.validate_minimum_amount(order) is True
```

## Checklist for New Code

### New Entity
- [ ] Create `src/domain/{entity}/{entity}.py` with frozen dataclass
- [ ] Create `src/domain/{entity}/{entity}_rules.py` with static methods
- [ ] Create `src/domain/{entity}/{entity}_repository.py` with Protocol
- [ ] Create `tests/unit/domain/{entity}/test_{entity}_rules.py`
- [ ] Add `__init__.py` files with exports

### New Use Case
- [ ] Create `src/application/{entity}/{action}_{entity}/command.py`
- [ ] Create `src/application/{entity}/{action}_{entity}/handler.py`
- [ ] Handler follows 5-step flow
- [ ] Rules imported explicitly from `{Entity}Rules`
- [ ] Create `tests/integration/application/{entity}/test_{action}_{entity}_handler.py`

### New Rule
- [ ] Add static method to `{Entity}Rules`
- [ ] Pure function (no side effects)
- [ ] Add corresponding test
- [ ] Import in handlers that need it

## Anti-Patterns to AVOID

```python
# ❌ BAD: Abstract base class with hidden logic
class BaseHandler(ABC):
    def handle(self, command):
        self.validate(command)  # Hidden in base class
        return self._execute(command)  # Where is the logic?

# ✅ GOOD: All logic visible in handler
class CancelOrderHandler:
    def handle(self, command):
        # Every step visible here
        order = self._repo.find_by_id(command.order_id)
        if not OrderRules.can_be_cancelled(order):
            raise BusinessRuleViolation(...)
        ...
```

```python
# ❌ BAD: Business logic in entity
@dataclass
class Order:
    def cancel(self):
        if self.status == OrderStatus.SHIPPED:
            raise Error("Cannot cancel")
        self.status = OrderStatus.CANCELLED  # Mutation!

# ✅ GOOD: Immutable entity + external rules
@dataclass(frozen=True)
class Order:
    def with_status(self, new_status) -> "Order":
        return Order(..., status=new_status)

# Rules separate
class OrderRules:
    @staticmethod
    def can_be_cancelled(order: Order) -> bool:
        return order.status not in (SHIPPED, DELIVERED)
```

```python
# ❌ BAD: Domain imports infrastructure
from src.infrastructure.persistence.order_repo import OrderRepoImpl

# ✅ GOOD: Domain defines interface, infrastructure implements
# In domain:
class OrderRepository(Protocol):
    def find_by_id(self, id: OrderId) -> Order | None: ...

# In infrastructure:
class OrderRepositoryImpl:
    def find_by_id(self, id: OrderId) -> Order | None:
        # Actual implementation
```
