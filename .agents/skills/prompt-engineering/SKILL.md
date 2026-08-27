---
name: prompt-engineering
description: LLM prompt engineering techniques for code generation, analysis, and automation. Use when the user asks about crafting better prompts, getting better AI responses, chain-of-thought prompting, few-shot examples, system prompts, or prompt templates.
---

# Prompt Engineering

## Core Techniques

### Be Specific and Structured
```
BAD: "Fix this code"
GOOD: "Review this Python function for:
1. Security vulnerabilities
2. Performance issues
3. Error handling gaps
Return findings as a numbered list with file:line references."
```

### Provide Context
```
BAD: "Write a REST API"
GOOD: "Create a Express.js REST API for a todo app with:
- TypeScript
- PostgreSQL via Prisma
- JWT authentication
- CRUD endpoints for todos
- Input validation with Zod"
```

### Chain-of-Thought
```
Think step by step:
1. Analyze the requirements
2. Identify edge cases
3. Design the solution
4. Implement the code
5. Verify correctness
```

## Prompt Templates

### Code Review
```
Review the following code for:
- Bugs and logic errors
- Security vulnerabilities
- Performance bottlenecks
- Code style and readability
- Missing error handling

Provide specific line references and concrete fix suggestions.

Code:
```

### Refactoring
```
Refactor this code to:
- Improve readability
- Reduce duplication
- Follow SOLID principles
- Add type safety

Maintain the same public API and behavior.
Show the refactored code with a brief explanation of changes.

Code:
```

### Test Generation
```
Generate comprehensive tests for this function:
- Cover happy path
- Cover edge cases (empty input, null, boundary values)
- Cover error cases
- Use the same testing framework as the project
- Include descriptive test names

Function:
```

### Debugging
```
I'm getting this error: [ERROR MESSAGE]

Context:
- Language/framework: [LANGUAGE]
- What I expected: [EXPECTED]
- What actually happens: [ACTUAL]
- Relevant code: [CODE]

Help me identify the root cause and fix it.
```

### Documentation
```
Generate documentation for this code:
- Brief summary of what it does
- Parameters/arguments with types
- Return value
- Usage example
- Any important notes or caveats

Code:
```

## Few-Shot Examples

```
Convert these function calls to SQL:

Input: getUser(123)
Output: SELECT * FROM users WHERE id = 123;

Input: getPostsByAuthor(authorId=456, limit=10)
Output: SELECT * FROM posts WHERE author_id = 456 LIMIT 10;

Input: updateUserEmail(userId=789, email="new@example.com")
Output: UPDATE users SET email = 'new@example.com' WHERE id = 789;

Now convert:
Input: searchProducts(category="electronics", minPrice=100, maxPrice=500)
Output:
```

## System Prompt Patterns

### Role Assignment
```
You are a senior software engineer with expertise in Python and system design.
You write clean, well-documented code following PEP 8.
You consider edge cases and error handling in every solution.
```

### Output Format Control
```
Always respond in this format:
## Analysis
[Brief analysis of the problem]

## Solution
[Code implementation]

## Explanation
[1-3 sentences explaining the approach]

## Alternatives
[Other valid approaches, if any]
```

### Constraint Setting
```
Constraints:
- Use only standard library (no external dependencies)
- Target Python 3.10+
- Keep functions under 20 lines
- Include type hints
- No comments explaining obvious code
```

## Advanced Patterns

### Self-Consistency
Ask the same question multiple times, take the majority answer.

### Tree of Thought
```
Consider three different approaches to solve this:
Approach 1: [describe]
Approach 2: [describe]
Approach 3: [describe]

For each, evaluate:
- Pros and cons
- Complexity
- Maintainability

Then recommend the best approach.
```

### Reflection
```
Review your previous answer. Check for:
1. Correctness - are there any bugs?
2. Completeness - did you miss any requirements?
3. Efficiency - can it be optimized?
Provide a corrected version if needed.
```

## Anti-Patterns

| Don't | Do |
|-------|-----|
| "Make it good" | Specify what "good" means |
| Dump code without context | Explain the goal and constraints |
| One giant prompt | Break into steps |
| Assume the model knows your project | Provide relevant code/context |
| Ignore output format | Specify exact format needed |

## Token Optimization

- Put the most important instructions first
- Use concise language without losing meaning
- Reference code by file path, don't paste entire files
- For large codebases, specify which files to focus on
- Use structured formats (lists, tables) for clarity
