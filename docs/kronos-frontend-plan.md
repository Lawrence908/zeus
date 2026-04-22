# Kronos Dashboard: `/jobs` Page (Frontend Plan)

## Context

Frontend surface for the Kronos scheduler. See `kronos-backend-plan.md` for the API contract this page consumes. New first-class route in the existing Vite + React + TypeScript SPA at `zeus/frontend/`, alongside Chat, Agents, Settings, Viz.

Goal: the user can see every scheduled job at a glance, drill into any one of them, run one manually, toggle enabled state, edit schedules, and watch executions happen in near real time.

## Route

`/jobs`. Added to React Router v6 in `App.tsx` and to the top nav alongside the existing routes. Icon suggestion: clock or calendar (lucide-react `Clock` or `CalendarClock`).

## File layout

```text
zeus/frontend/src/
  pages/
    JobsPage.tsx              # route root, layout shell
  components/
    jobs/
      JobsTable.tsx           # tabular view with sortable columns
      JobsTableRow.tsx
      JobFilters.tsx          # category, status, search
      JobDetailDrawer.tsx     # slide-out drawer with tabbed detail
      JobExecutionFeed.tsx    # recent runs, auto-refreshing
      JobForm.tsx             # create + edit
      CronBuilder.tsx         # preset dropdown plus raw expression
      CronPreview.tsx         # next N fire times
      JobStatusBadge.tsx      # enabled/disabled/failed/running
      JobCategoryBadge.tsx    # colour-coded per category
      UpcomingTimeline.tsx    # optional, v1.1
  store/
    kronosStore.ts            # Zustand store for jobs, runs, filters
  hooks/
    useKronosJobs.ts          # fetch + auto-refresh jobs
    useKronosRuns.ts          # poll recent runs
    useKronosHealth.ts        # scheduler health indicator
  api/
    kronos.ts                 # thin fetch wrappers over /kronos/*
  types/
    kronos.ts                 # mirror of backend Pydantic models
```

## State (Zustand)

Single `kronosStore` covering jobs, runs, filters, selection. Shape:

```typescript
type KronosStore = {
  jobs: JobDefinition[];
  runs: JobRun[];
  upcoming: ScheduledRun[];
  health: { ok: boolean; lastTickAgeMs: number } | null;
  filters: {
    category: JobCategory | "all";
    status: "all" | "enabled" | "disabled" | "failed" | "overdue";
    search: string;
  };
  selectedJobId: string | null;
  isLoading: boolean;

  setSelectedJob: (id: string | null) => void;
  setFilter: <K extends keyof Filters>(key: K, value: Filters[K]) => void;
  refreshJobs: () => Promise<void>;
  refreshRuns: () => Promise<void>;
  createJob: (def: Partial<JobDefinition>) => Promise<JobDefinition>;
  updateJob: (id: string, patch: Partial<JobDefinition>) => Promise<void>;
  deleteJob: (id: string) => Promise<void>;
  runJobNow: (id: string) => Promise<{ correlation_id: string }>;
  toggleEnabled: (id: string) => Promise<void>;
};
```

## Page layout

```
┌────────────────────────────────────────────────────────────────┐
│ Jobs  [scheduler ● ok]                      [+ New Job]        │
├────────────────────────────────────────────────────────────────┤
│ [All Categories ▼] [All Status ▼] [Search_____] [Timeline view]│
├────────────────────────────────────────────────────────────────┤
│ Name  | Category | Schedule | Next | Last | Enabled | Actions  │
│ ─────────────────────────────────────────────────────────────  │
│ ... rows ...                                                   │
├────────────────────────────────────────────────────────────────┤
│ Recent executions (collapsible)                                │
│ ● newsletter-morning-digest  success  2m ago  4.2s             │
│ ● nightly-knowledge-ingest   running  now     ...              │
│ ● weekly-memory-review       failed   1h ago  TimeoutError     │
└────────────────────────────────────────────────────────────────┘
```

The header carries a small scheduler-health indicator pulled from `GET /kronos/health` (green dot = ok, red dot + tooltip on failure).

Clicking a row opens `JobDetailDrawer` as a slide-in from the right; route does not change, selection is stored in Zustand and reflected in the URL via a `?job=<id>` query param for shareability.

## Table columns

| Column | Behaviour |
|--------|-----------|
| Name | bold, click opens detail drawer |
| Category | `JobCategoryBadge`, coloured |
| Schedule | human-readable cron (e.g. "Daily at 9:00 AM PT"); tooltip shows raw expression and timezone |
| Next run | relative ("in 3h 12m"); tooltip absolute time |
| Last run | status icon + duration ("success, 2.4s"); click jumps to that run in the detail drawer History tab |
| Enabled | toggle switch, optimistic update with rollback on API error |
| Actions | kebab menu: Run Now, Edit, Duplicate, Delete |

Sortable by any column. Persist sort order + filter state in `localStorage` under a single key (`kronos.table.prefs`).

## Job detail drawer

Four tabs:

1. **Overview**: full definition (name, description, category, schedule, executor, agent, safety policy, timeout, retries, tags), next 5 fire times from `CronPreview`, `Enabled` toggle, `Run Now` button.
2. **History**: table of last 20 runs (status, started_at, duration, output summary preview). Rows expand inline to show full output and error.
3. **Output**: full text of the last run's output; copy button; link to correlation id / logs.
4. **Edit**: `JobForm` in edit mode. Save calls `PATCH /kronos/jobs/{id}`.

Danger zone at the bottom of the Edit tab: delete with a confirm modal.

## Create / Edit form (`JobForm`)

Shared component for both flows. Fields:

- Name (required)
- Description (textarea, optional)
- Category (dropdown, populated from `GET /kronos/categories`)
- Schedule:
  - Radio: Recurring vs One-off
  - If Recurring: `CronBuilder` (preset dropdown: Every hour / Daily 9am / Weekdays 9am / Weekly Monday / Monthly 1st / Custom) plus a raw cron text field; timezone select (default user's browser TZ)
  - If One-off: datetime picker, single fire
- Executor (dropdown from `GET /kronos/executors`, or freeform dotted path)
- Agent (optional dropdown from `GET /admin/agents`)
- Params (JSON editor; v1 can be a plain textarea with JSON validation, upgrade later)
- Safety policy (dropdown)
- Timeout seconds (number, default 600)
- Max retries (number, default 1)
- Tags (chip input)
- Enabled toggle

Below the schedule fields, a live `CronPreview` shows the next 5 fire times as the user types. Use `cron-parser` (tiny dep) for client-side validation and preview.

## Cron builder

For v1, keep narrow:

- Preset dropdown sets the raw field
- User can edit the raw field directly
- Client-side validate via `cron-parser`
- Show preview of next 5 times, re-computed on any change
- Timezone select next to the expression; the preview respects it

No visual "every [N] [unit]" builder in v1; users who need that can pick a preset or write raw cron.

## Execution feed

Below the table, a collapsible panel polling `GET /kronos/runs?limit=20` every 5 seconds while the page is visible. Row format:

```
● [status dot] [job name]  [status]  [relative started]  [duration]
```

Pulsing dot for `running`, solid for `success`, red for `failed` / `timeout`. Click a row to open the parent job's detail drawer on the Output tab for that specific run.

Pause polling when the browser tab is hidden (use `document.visibilitychange`).

## Status visuals

- Enabled rows: default text colour
- Disabled rows: 50% dimmed
- Failed last run: red left border on the row
- Currently running: pulsing dot in the status cell
- Overdue (should have fired, hasn't): orange badge in the Next Run column

## Upcoming timeline (deferred)

Horizontal 24h or 7d timeline with rows by category and blocks for each scheduled run. Nice-to-have; skip in Phase 1, add once the core table works.

## API client

`src/api/kronos.ts` thin wrapper over `fetch`:

```typescript
export const kronosApi = {
  listJobs: (filters?) => ...,
  getJob: (id) => ...,
  createJob: (def) => ...,
  updateJob: (id, patch) => ...,
  deleteJob: (id) => ...,
  runNow: (id) => ...,
  enable: (id) => ...,
  disable: (id) => ...,
  listRuns: (params?) => ...,
  getRun: (id) => ...,
  upcoming: (limit) => ...,
  health: () => ...,
  executors: () => ...,
  categories: () => ...,
};
```

All routes relative (`/kronos/...`), rely on the existing Vite dev proxy to FastAPI on 8203.

## Types

`src/types/kronos.ts` mirrors the backend Pydantic models. Keep this file in strict sync with `zeus/kronos/models.py`. Consider generating from OpenAPI in a later pass; hand-written is fine for v1.

## Styling

Reuse existing Tailwind tokens and the Zeus dark theme. Badges inherit the colour system used elsewhere (agent cards, Aegis policy badges).

Suggested category colour map (Tailwind classes in parens):

- briefing: blue (`bg-blue-500/20 text-blue-300`)
- ingest: green
- memory_review: purple
- maintenance: gray
- research: orange
- job_search: pink
- health: cyan
- custom: white/neutral

## Linear ticket structure

Under new Project 11 (Kronos), frontend parent tickets:

- Jobs Page Scaffold: route, nav entry, layout shell, Zustand store, API client, types
- Jobs Table + Filters: table, sorting, filter bar, localStorage persistence
- Job Detail Drawer: tabbed drawer with Overview, History, Output, Edit
- Job Form + Cron Builder: create + edit form, preview, client-side validation
- Execution Feed: polling feed, pause on hidden tab, click-through to run detail
- Upcoming Timeline (deferred to v1.1)

## Dependencies on backend

Needs the following endpoints live before full wire-up, in priority order:

1. `GET /kronos/jobs`, `GET /kronos/jobs/{id}`
2. `GET /kronos/runs`, `GET /kronos/runs/{id}`
3. `POST /kronos/jobs/{id}/run`, `POST /kronos/jobs/{id}/enable`, `POST /kronos/jobs/{id}/disable`
4. `POST /kronos/jobs`, `PATCH /kronos/jobs/{id}`, `DELETE /kronos/jobs/{id}`
5. `GET /kronos/health`, `GET /kronos/executors`, `GET /kronos/categories`, `GET /kronos/schedule/upcoming`

Parallel development is fine: stub with fixtures until each endpoint lands.

## Phase 1 deliverable

`/jobs` route ships with:

- Sortable filterable table of seed jobs from the API
- Scheduler health indicator in the header
- Detail drawer with Overview and History tabs
- Enable/disable toggle, Run Now action
- Execution feed (read-only, polling)

Create/Edit form, cron builder, and timeline view land in Phase 2.
