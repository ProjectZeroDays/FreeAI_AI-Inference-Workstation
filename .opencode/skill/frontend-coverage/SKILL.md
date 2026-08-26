---
name: frontend-coverage
description: Compare backend modules/APIs with frontend usage to find backend functionality that is NOT reachable from the current frontend (orphan endpoints, unreferenced exports, broken calls). Suggests concrete wiring (React/Vue/Svelte + fetch/React Query) to connect them so the frontend can actually exercise the backend. Use when the user says "wire up the backend", "what endpoints aren't used", "frontend backend mismatch", "find dead API routes", "connect X to the frontend", "audit API coverage".
---

# Frontend coverage — find and wire the orphan backend

Compares the backend's reachable surface against what the frontend actually
calls. Produces a coverage matrix plus concrete code suggestions to wire up the
gaps. Read-only detection; suggestions are proposed, edits require user
confirmation.

## 0. Detect the two stacks

Don't assume — sniff:
- **Backend**: a `main.py`/`app.py` (FastAPI/Flask/Django), a `server/` folder
  (Express/Nest/Fastify), `src/main.ts` (NestJS), `cmd/` (Go), `pom.xml`
  (Spring), or a `routes/` dir. MCP tools live in a `tools/` or `mcp/` folder.
- **Frontend**: `src/App.{tsx,jsx,vue,svelte}`, `pages/` (Next/Nuxt), `app/`
  (Next App Router), `src/components/`, `index.html`. SPA build tools
  (`vite.config.ts`, `next.config.js`, `webpack.config.js`).

If either side is absent, STOP — there's nothing to compare.

## 1. Inventory the backend surface (per stack)

The goal is a list of `(name, type, signature, file:line, route?)` entries.

| backend               | extract                                                      |
|-----------------------|--------------------------------------------------------------|
| FastAPI               | `@app.{get,post,put,patch,delete}` decorators → path+method; handlers' signature becomes the payload schema. |
| Flask                 | `@app.route` / Blueprints → path+methods.                    |
| Django REST           | `urlpatterns` + ViewSet `@action`s → path+method.           |
| Express / Fastify     | `app.{get,post,...}('/path', ...)` / `fastify.route(...)`.    |
| NestJS                | `@Controller('x')` + `@Get/@Post/...` → path+method.        |
| Spring                | `@RestController @RequestMapping` → path+method.             |
| Go net/http           | `mux.HandleFunc("METHOD /path", ...)` / `http.Method = ...`. |
| exported functions    | TS/JS `export function`, Python non-underscore module-level function, Go exported func with doc comment. |
| CLI commands          | commander/clipanion/yargs/argparse/cobra option blocks.      |
| MCP tools (server SDK)| `server.tool('name', schema, handler)` / `@McpServer.tool`.  |

Use `ripgrep` for the decorators/keywords, then read the enclosing function for
the signature. Store `(name, kind, file:line, route, signature)`.

## 2. Inventory the frontend usage

Search for every place the front end could call the backend:

- `fetch('...')`, `axios.{get,post,...}('...')`, `$fetch('...')` (ofetch/nuxt),
  `wx.request`, `useFetch`, `useSwr`, `useQuery`, `react-query`/`@tanstack/
  query`. Capture the URL pattern(s).
- Typed clients: generated clients (`openapi-typescript`, `orval`,
  `swagger-typescript-api`), hand-written `api/*.ts` wrapper files, GraphQL
  documents (`useQuery(...)`, `gql\`...\``).
- Vue/Svelte/swr: `<script>` import of an `api/` symbol, `useApi(...)` hooks.
- Direct router imports for SSR endpoints (Next/Nuxt server actions).
- WebSocket/SSE subscriptions (`new WebSocket`, `EventSource`) — different
  transport, often exposes different surface than REST.

Capture each call site as `(urlPattern, file:line, namedHandler?)`.

## 3. Normalize and match

Make both inventories comparable:
- Replace path params (`:id`, `{id}`, `[id]`) with `:param` for matching.
- Drop query strings — they're call-site details, not route identity.
- Reconcile against the server's path-prefix (`/api/v1/...`? prefix may live in
  the client `baseURL`, not the route decorator).

Now classify every backend entry into one of:

| class              | meaning                                                       |
|--------------------|---------------------------------------------------------------|
| `wired`            | ≥1 frontend call site matches the normalized route.           |
| `orphan-endpoint`  | backend route exists, no frontend caller. likely orphan.       |
| `partial`          | frontend calls a `POST` but ignores the typed response shape. |
| `broken-call`      | frontend calls a route that doesn't exist on the backend.     |
| `signature-mismatch` | frontend passes `{x,y}` but backend's body is `{x,y,z}` required. |

And classify frontend call sites as `frontend-only` if they target a route the
backend never declared (these are bugs, not orphans).

## 4. Suggest concrete wiring

For every `orphan-endpoint`, propose a **minimal** frontend wiring in the user's
stack. Examples (adapt):

- React + `fetch`:
  ```ts
  export async function deleteWidget(id: string): Promise<void> {
    const r = await fetch(`/api/widgets/${id}`, { method: "DELETE" });
    if (!r.ok) throw new Error(`delete failed: ${r.status}`);
  }
  // Caller:
  //   await deleteWidget(id); refetch();
  ```
- React + TanStack Query:
  ```ts
  const qc = useQueryClient();
  const m = useMutation({
    mutationFn: (id: string) =>
      fetch(`/api/widgets/${id}`, { method: "DELETE" }).then((r) => {
        if (!r.ok) throw new Error(`${r.status}`);
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["widgets"] }),
  });
  ```
- Vue 3 + `ofetch` / `$fetch` (Nuxt):
  ```ts
  async function remove(id: string) {
    await $fetch(`/api/widgets/${id}`, { method: "DELETE" });
    await refresh();
  }
  ```

For `signature-mismatch`: show the backend's required shape and the corrected
client. Don't rewrite unrelated calls.

For `broken-call`: flag the file:line; usually a typo or a deleted route — let
the user decide whether to delete the call or restore the route.

If the frontend doesn't have an `api/` shim yet and would benefit from one,
propose one — but in a SEPARATE PR so the orphan-wiring edits stay minimal.

## 5. Output format

```
FRONTEND COVERAGE — wired = 18, orphan-endpoint = 9, broken-call = 3,
signature-mismatch = 2.

ORPHAN ENDPOINTS (backend present, frontend absent):
  [1] DELETE /api/widgets/{id}        · widgets.py:42 · deleteWidget suggestion (React + fetch)
  [2] GET    /api/metrics/summary     · metrics.py:18 · hover card on dashboard? (React Query useQuery)
  ...

BROKEN CALLS (frontend calls a route the backend never declared):
  [3] src/components/Todo.tsx:88 calls `PUT /api/todos/{id}/pin` — backend has no such route.
  [4] pages/users/[id].tsx:52 references `useUserSettings` which now requires `id`.
  ...

SIGNATURE MISMATCHES:
  [5] src/api/createWidget.ts sends {name, kind}; backend requires {name, kind, owner}.
      ← require("owner") on backend? Or default it server-side?

PROPOSED WIRING:
  [1] deleteWidget(id) — see snippet above.
  [2] useMetricsSummary() — React Query useQuery(['metrics-summary'], ...).

NEXT: reply `wire [n]` to apply that wiring as an isolated edit. Each
proposed wiring is a separate commit for safe review.
```

## 6. Hard rules

- Don't run the frontend's dev server or browser. Pure static analysis.
- Don't edit frontend code until the user replies `wire [n]`.
- Don't summarize if an `orphan` is actually `wired` via a generated typed
  client — check the client file (often `api/*.ts` or `src/generated/`) before
  flagging. Generated clients are wired *en masse* by the API spec; if they're
  regenerated, "orphan" status flips, so prefer regeneration over a hand-written
  patch when a generator exists.
- A backend route protected by authz that the frontend only calls behind a
  login wall is NOT broken — that's `wired`.
- Don't propose deleting an orphan endpoint — deleting backend functionality is
  a `coder`/`reviewer` decision, not this skill's call. This skill only wires
  them. Deletions belong to `project-audit`.
- For large gaps (>15 orphans), don't dump them all — top 10 by user-impact, with
  a one-line "(N more; ask)" pointer to the full list.