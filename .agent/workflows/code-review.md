---
description: How to use Jarvis for code reviews
---

# Code Review Workflow with Jarvis

## Quick Start

Simply invoke Jarvis with any of these phrases:
- "Jarvis, review this code"
- "@Jarvis please check [file/function/class]"
- "Hey Jarvis, analyze this implementation"

## Step-by-Step Review Process

### 1. Identify Code to Review
Specify what you want reviewed:
- A specific file: "Jarvis, review src/analysis/technical/analyzer.py"
- A function or class: "Jarvis, check the TechnicalAnalyzer class"
- Recent changes: "Jarvis, review my latest changes"
- Entire module: "Jarvis, analyze the sentiment analysis module"

### 2. Jarvis Performs Analysis
Jarvis will automatically:
- Read and understand the code
- Check for critical issues (security, logic errors)
- Identify important improvements (performance, error handling)
- Suggest enhancements (style, documentation)
- Acknowledge what's done well

### 3. Review Feedback
Jarvis provides structured feedback:
- **Critical Issues** 🔴 - Fix immediately
- **Important Improvements** 🟡 - Address soon
- **Suggestions** 🟢 - Consider for enhancement
- **What's Done Well** ✅ - Keep doing this
- **Recommended Next Steps** - Prioritized action items

### 4. Implement Changes
Based on Jarvis's feedback:
- Address critical issues first
- Work through important improvements
- Consider suggestions based on time/priority

### 5. Re-review (Optional)
After making changes:
- "Jarvis, review the updated code"
- Verify improvements were implemented correctly

## Example Invocations

**Review a specific file:**
```
Jarvis, review src/orchestrator.py
```

**Check a new feature:**
```
@Jarvis, I just added a new indicator calculator. Can you review the implementation?
```

**Security check:**
```
Hey Jarvis, please do a security review of the data fetching module
```

**Performance analysis:**
```
Jarvis, check if there are any performance issues in the decision engine
```

## Tips for Best Results

1. **Be specific**: Tell Jarvis what aspect to focus on if needed
2. **Provide context**: Mention if code is experimental, production-ready, etc.
3. **Ask questions**: "Jarvis, is this the best way to handle errors here?"
4. **Iterative reviews**: Review small chunks rather than entire codebase at once

## Integration with Development

- Use Jarvis before committing code
- Request reviews during pull request preparation
- Get second opinions on architectural decisions
- Validate refactoring efforts
