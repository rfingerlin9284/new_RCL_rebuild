# Code Examples: Clean vs. Messy

This document provides side-by-side examples of clean code following RCL standards versus messy code that violates our principles.

## Example 1: Ghost Code

### ❌ Messy (With Ghost Code)
```javascript
function calculateTotal(items) {
  let total = 0;
  
  // Old calculation method
  // for (let i = 0; i < items.length; i++) {
  //   total += items[i].price;
  // }
  
  // New method with discount
  items.forEach(item => {
    total += item.price * (1 - item.discount);
  });
  
  // const tax = total * 0.08; // removed tax
  return total;
}
```

### ✅ Clean (No Ghost Code)
```javascript
function calculateTotal(items) {
  return items.reduce((total, item) => {
    return total + item.price * (1 - item.discount);
  }, 0);
}
```

## Example 2: Conflicting Logic and Feature Flags

### ❌ Messy (Scattered Feature Flags)
```javascript
function processOrder(order) {
  if (FEATURE_NEW_PAYMENT && !LEGACY_MODE) {
    return newPaymentProcessor(order);
  } else if (BETA_USERS || FEATURE_FLAG_X) {
    return betaPaymentProcessor(order);
  } else {
    return oldPaymentProcessor(order);
  }
}

function validateOrder(order) {
  if (FEATURE_NEW_PAYMENT) {
    return newValidation(order);
  }
  return oldValidation(order);
}
```

### ✅ Clean (Strategy Pattern)
```javascript
// config/payment-config.js
export const getPaymentStrategy = (config) => {
  if (config.features.modernPayment) {
    return new ModernPaymentProcessor();
  }
  return new LegacyPaymentProcessor();
};

// src/services/order-service.js
export class OrderService {
  constructor(paymentProcessor) {
    this.paymentProcessor = paymentProcessor;
  }
  
  processOrder(order) {
    return this.paymentProcessor.process(order);
  }
  
  validateOrder(order) {
    return this.paymentProcessor.validate(order);
  }
}
```

## Example 3: Poor Code Extraction

### ❌ Messy (Duplicated Code)
```javascript
function createUser(data) {
  const email = data.email.toLowerCase().trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error('Invalid email');
  }
  
  return {
    email: email,
    name: data.name,
    createdAt: new Date().toISOString(),
  };
}

function updateUser(id, data) {
  const email = data.email.toLowerCase().trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error('Invalid email');
  }
  
  return {
    id: id,
    email: email,
    name: data.name,
    updatedAt: new Date().toISOString(),
  };
}
```

### ✅ Clean (Extracted Utilities)
```javascript
// src/utils/validators.js
export const validateEmail = (email) => {
  const normalized = email.toLowerCase().trim();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!emailRegex.test(normalized)) {
    throw new Error('Invalid email');
  }
  
  return normalized;
};

// src/services/user-service.js
export const createUser = (data) => {
  return {
    email: validateEmail(data.email),
    name: data.name,
    createdAt: new Date().toISOString(),
  };
};

export const updateUser = (id, data) => {
  return {
    id,
    email: validateEmail(data.email),
    name: data.name,
    updatedAt: new Date().toISOString(),
  };
};
```

## Example 4: Unclear Comments and Prompts

### ❌ Messy (Embedded Prompts)
```javascript
function processData(data) {
  // TODO: fix this later
  // HACK: temporary solution
  // ???: not sure why this works
  const result = data.map(item => {
    // need to handle edge case
    if (item.value) {
      // do something
      return item.value * 2;
    }
    return 0;
  });
  
  // FIXME: this is broken
  return result;
}
```

### ✅ Clean (Clear Documentation)
```javascript
/**
 * Process data items by doubling their values
 * Issue #123: Add null handling for missing values
 * 
 * @param {Array} data - Array of data items
 * @returns {Array} Processed values
 */
function processData(data) {
  return data.map(item => {
    // Default to 0 for items without value property
    return (item.value || 0) * 2;
  });
}
```

## Example 5: Mixed Concerns

### ❌ Messy (Everything in One Place)
```javascript
function handleUserRegistration(req, res) {
  // Validation
  if (!req.body.email) return res.status(400).send('Missing email');
  
  // Business logic
  const user = {
    email: req.body.email,
    password: hashPassword(req.body.password),
    createdAt: Date.now(),
  };
  
  // Database
  db.users.insert(user);
  
  // Email
  sendEmail(user.email, 'Welcome!');
  
  // Logging
  console.log('User registered:', user.email);
  
  // Response
  res.status(201).json({ id: user.id });
}
```

### ✅ Clean (Separated Concerns)
```javascript
// src/api/controllers/user-controller.js
export class UserController {
  constructor(userService, emailService, logger) {
    this.userService = userService;
    this.emailService = emailService;
    this.logger = logger;
  }
  
  async register(req, res) {
    try {
      const userData = req.body;
      const user = await this.userService.createUser(userData);
      
      await this.emailService.sendWelcome(user.email);
      this.logger.info('User registered', { userId: user.id });
      
      res.status(201).json({ id: user.id });
    } catch (error) {
      this.logger.error('Registration failed', { error });
      res.status(400).json({ error: error.message });
    }
  }
}

// src/services/user-service.js
export class UserService {
  constructor(userRepository, passwordHasher) {
    this.userRepository = userRepository;
    this.passwordHasher = passwordHasher;
  }
  
  async createUser(userData) {
    this.validateUserData(userData);
    
    const user = {
      email: userData.email,
      password: await this.passwordHasher.hash(userData.password),
      createdAt: new Date(),
    };
    
    return await this.userRepository.create(user);
  }
  
  validateUserData(userData) {
    if (!userData.email) {
      throw new Error('Email is required');
    }
    if (!userData.password) {
      throw new Error('Password is required');
    }
  }
}
```

## Key Takeaways

1. **Delete** commented code instead of keeping it around
2. **Extract** common logic into reusable functions
3. **Separate** concerns (API, business logic, data access)
4. **Centralize** configuration and feature flags
5. **Document** with purpose, not noise
6. **Use** dependency injection for testability
7. **Keep** functions small and focused

Following these patterns makes code:
- Easier to test
- Easier to understand
- Easier to maintain
- Easier to extend
