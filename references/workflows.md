# Common Workflows

This document provides detailed workflows for common tasks with the GitHub Knowledge Base skill.

## Workflow 1: Starting a New Learning Project

**Scenario**: You want to learn about GraphQL and need to explore relevant repositories.

**Steps**:

1. **Search for repositories**
   ```bash
   python kb_search.py github "graphql server" --stars ">5000" --language javascript
   ```

2. **Add promising ones**
   ```bash
   python kb.py add graphql/graphql-js
   python kb.py add apollographql/apollo-server
   ```

3. **Tag for organization**
   ```bash
   python kb.py tag graphql/graphql-js graphql backend learning
   python kb.py tag apollographql/apollo-server graphql backend learning
   ```

4. **Find related repositories**
   ```bash
   python kb_search.py related graphql/graphql-js --limit 10
   ```

5. **Clone for deep exploration**
   ```bash
   python kb_explore.py clone graphql/graphql-js
   python kb_explore.py clone apollographql/apollo-server
   ```

6. **Analyze structure**
   ```bash
   python kb_explore.py analyze graphql/graphql-js
   python kb_explore.py tree graphql/graphql-js --depth 2
   ```

7. **Add notes as you learn**
   ```bash
   python kb.py note graphql/graphql-js "Reference implementation - start here for core concepts"
   python kb.py note apollographql/apollo-server "Production-ready server - good for real-world patterns"
   ```

8. **Update status as you progress**
   ```bash
   python kb.py status graphql/graphql-js exploring
   # Later...
   python kb.py status graphql/graphql-js explored
   ```

## Workflow 2: Solving a Specific Problem

**Scenario**: You need to implement rate limiting in your API.

**Steps**:

1. **Search for solutions**
   ```bash
   python kb_search.py github "rate limiting api" --stars ">1000"
   ```

2. **Add top candidates**
   ```bash
   python kb.py add express-rate-limit/express-rate-limit
   python kb.py add animir/node-rate-limiter-flexible
   ```

3. **Quick exploration without full clone**
   ```bash
   python kb_explore.py clone express-rate-limit/express-rate-limit --depth 1
   ```

4. **Find usage examples**
   ```bash
   python kb_explore.py readme express-rate-limit/express-rate-limit
   python kb_explore.py find-tests express-rate-limit/express-rate-limit
   ```

5. **Search for specific implementation**
   ```bash
   python kb_search.py code "redis.*rate" --repo express-rate-limit/express-rate-limit
   ```

6. **Compare different approaches**
   ```bash
   python kb_search.py compare express-rate-limit/express-rate-limit animir/node-rate-limiter-flexible "limit"
   ```

7. **Make decision and document**
   ```bash
   python kb.py note express-rate-limit/express-rate-limit "Chose this - simpler API, good Express integration"
   python kb.py status express-rate-limit/express-rate-limit explored
   python kb.py tag express-rate-limit/express-rate-limit express middleware rate-limiting
   ```

## Workflow 3: Building Domain Expertise

**Scenario**: You want to become expert in React ecosystem.

**Steps**:

1. **Add core repository**
   ```bash
   python kb.py add facebook/react
   ```

2. **Find ecosystem libraries**
   ```bash
   python kb_search.py related facebook/react --limit 20
   ```

3. **Add key ecosystem repos**
   ```bash
   python kb.py add facebook/react
   python kb.py add redux-toolkit/redux-toolkit
   python kb.py add remix-run/react-router
   python kb.py add tanstack/query
   python kb.py add pmndrs/zustand
   ```

4. **Organize with tags**
   ```bash
   python kb.py tag facebook/react react core library
   python kb.py tag redux-toolkit/redux-toolkit react state-management
   python kb.py tag remix-run/react-router react routing
   python kb.py tag tanstack/query react data-fetching
   python kb.py tag pmndrs/zustand react state-management
   ```

5. **Clone and analyze core library**
   ```bash
   python kb_explore.py clone facebook/react
   python kb_explore.py analyze facebook/react
   python kb_explore.py entry-points facebook/react
   ```

6. **Study specific features across repos**
   ```bash
   python kb_search.py code "useState" --tag react
   python kb_search.py code "createSlice" --repo redux-toolkit/redux-toolkit
   ```

7. **Compare state management approaches**
   ```bash
   python kb_search.py compare redux-toolkit/redux-toolkit pmndrs/zustand "store"
   ```

8. **Document learnings**
   ```bash
   python kb.py note facebook/react "Hooks architecture in packages/react/src/ReactHooks.js"
   python kb.py note redux-toolkit/redux-toolkit "Immer integration for immutable updates"
   ```

9. **Track progress**
   ```bash
   python kb.py status facebook/react explored
   python kb.py status redux-toolkit/redux-toolkit exploring
   python kb.py stats
   ```

## Workflow 4: Researching Best Practices

**Scenario**: How do top repos handle error handling?

**Steps**:

1. **Check existing repos**
   ```bash
   python kb.py list --status explored
   ```

2. **Search error handling patterns**
   ```bash
   python kb_search.py code "try.*catch|error.*handler" --tag backend
   ```

3. **If needed, add more examples**
   ```bash
   python kb_search.py github "error handling nodejs" --stars ">10000"
   python kb.py add nestjs/nest
   python kb_explore.py clone nestjs/nest
   ```

4. **Compare approaches**
   ```bash
   python kb_search.py compare express nestjs/nest "error"
   ```

5. **Find centralized error handling**
   ```bash
   python kb_search.py code "errorHandler|ErrorHandler" --tag backend
   ```

6. **Document findings**
   ```bash
   python kb.py note express "Centralized error handling via middleware"
   python kb.py note nestjs/nest "Exception filters with decorators"
   ```

## Workflow 5: Maintaining Your Knowledge Base

**Regular maintenance tasks**:

1. **Review your collection**
   ```bash
   python kb.py stats
   python kb.py list
   ```

2. **Sync cloned repositories**
   ```bash
   # Create a script to sync all:
   for repo in $(python kb.py list | grep "💾" | awk '{print $3}'); do
       python kb_explore.py sync "$repo"
   done
   ```

3. **Archive old or unused repos**
   ```bash
   python kb.py status old-repo/archived archived
   ```

4. **Clean up tags**
   ```bash
   python kb.py list --tag old-tag
   # Re-tag as needed
   ```

5. **Export your notes**
   ```bash
   # Notes are in ~/.config/github-kb/notes/
   cat ~/.config/github-kb/notes/*.md > my-knowledge-export.md
   ```

## Workflow 6: Quick Reference Lookup

**Scenario**: You remember seeing a pattern but can't recall where.

**Steps**:

1. **Search across all repos**
   ```bash
   python kb_search.py code "specific.*pattern"
   ```

2. **If too many results, filter**
   ```bash
   python kb_search.py code "specific.*pattern" --tag frontend
   ```

3. **Check specific repo**
   ```bash
   python kb_search.py code "specific.*pattern" --repo owner/repo
   ```

## Workflow 7: Code Review Preparation

**Scenario**: Reviewing a PR that uses a library you want to understand better.

**Steps**:

1. **Add the library**
   ```bash
   python kb.py add library/repo
   ```

2. **Quick clone (shallow)**
   ```bash
   python kb_explore.py clone library/repo --depth 1
   ```

3. **Find relevant code**
   ```bash
   python kb_search.py code "methodFromPR" --repo library/repo
   ```

4. **Check tests for usage**
   ```bash
   python kb_explore.py find-tests library/repo
   # Then read specific test files
   ```

5. **Add quick note**
   ```bash
   python kb.py note library/repo "Used in PR #123 - method X does Y"
   ```

## Tips for Effective Workflows

1. **Start broad, then narrow** - Search GitHub first, clone only what you need
2. **Use shallow clones** - Save disk space with `--depth 1` for reference repos
3. **Tag consistently** - Establish your tagging system early
4. **Document as you learn** - Add notes immediately, not later
5. **Update status** - Track your exploration progress
6. **Regular review** - Weekly review of your KB keeps it organized
7. **Connect the dots** - Use related searches to build context

## Advanced Patterns

### Pattern 1: Framework Comparison Matrix

Compare multiple frameworks systematically:

```bash
# Add all candidates
python kb.py add express fastify koa nestjs/nest

# Tag them
for repo in express fastify koa nestjs/nest; do
    python kb.py tag "$repo" nodejs framework backend comparison
done

# Clone all
for repo in express fastify koa nestjs/nest; do
    python kb_explore.py clone "$repo"
done

# Compare specific features
python kb_search.py code "middleware" --tag comparison
python kb_search.py code "routing" --tag comparison
python kb_search.py code "validation" --tag comparison
```

### Pattern 2: Learning Path

Create structured learning paths:

```bash
# Beginner repos
python kb.py tag simple-repo beginner learning-path-1

# Intermediate repos
python kb.py tag medium-repo intermediate learning-path-1

# Advanced repos
python kb.py tag complex-repo advanced learning-path-1

# View by difficulty
python kb.py list --tag beginner
python kb.py list --tag intermediate
```

### Pattern 3: Architecture Study

Study architectural patterns:

```bash
# Add repos with different architectures
python kb.py add microservices-example
python kb.py add monolith-example
python kb.py add serverless-example

# Tag by architecture
python kb.py tag microservices-example architecture microservices
python kb.py tag monolith-example architecture monolith

# Compare patterns
python kb_search.py code "service.*communication" --tag microservices
python kb_search.py code "module.*structure" --tag monolith
```

## Troubleshooting Common Issues

**Issue**: Too many search results

**Solution**: Use more specific patterns or filter by tag/repo
```bash
python kb_search.py code "error" --tag backend --repo express
```

**Issue**: Can't find a specific implementation

**Solution**: Clone the repo first, then search
```bash
python kb_explore.py clone owner/repo
python kb_search.py code "specific.*code" --repo owner/repo
```

**Issue**: Disk space running low

**Solution**: Remove unused clones, keep KB entries
```bash
# Remove clone but keep in KB
rm -rf ~/.config/github-kb/repos/owner__repo

# Update index
python kb.py info owner/repo  # Will show not cloned
```

**Issue**: API rate limit hit

**Solution**: Set GITHUB_TOKEN
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

**Issue**: Lost track of what you added

**Solution**: Use stats and notes
```bash
python kb.py stats
python kb.py list
cat ~/.config/github-kb/notes/*.md
```
