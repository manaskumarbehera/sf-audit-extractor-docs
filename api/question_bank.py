"""
TrackForcePro — Adaptive Question Bank
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each question has:
  - id: unique identifier
  - topic: category for spaced-repetition grouping
  - difficulty: 1 (easy) / 2 (medium) / 3 (hard)
  - mode: which game mode(s) it suits
  - q: question text
  - opts: answer options (list)
  - answer: index of correct answer
  - explanation: HTML explanation shown after answering
  - tags: fine-grained tags for weakness tracking
"""

TOPICS = {
    "sidebar": "TF Sidebar & Navigation",
    "graphql": "GraphQL Builder",
    "soql": "SOQL Builder",
    "data_explorer": "Data Explorer & Record Scanner",
    "security": "Security Manager",
    "org_tools": "Org Tools",
    "platform_events": "Platform Events & LMS",
    "architecture": "Extension Architecture",
    "user_manager": "User Manager",
    "general": "General Knowledge",
}

# fmt: off
QUESTIONS = [
    # ═══════════════════════════════════════════════
    #  SIDEBAR & NAVIGATION  (topic: sidebar)
    # ═══════════════════════════════════════════════
    {
        "id": "sb-001",
        "topic": "sidebar",
        "difficulty": 1,
        "mode": ["quiz", "truefalse", "speed"],
        "q": "Where is the TF Sidebar button located on a Salesforce page?",
        "opts": ["Top-left corner", "Browser toolbar only", "Bottom-right corner of the page", "Inside Salesforce Setup menu"],
        "answer": 2,
        "explanation": "The TF Sidebar appears as a <strong>floating button at the bottom-right</strong> of every Salesforce page.",
        "tags": ["sidebar", "location", "basics"],
    },
    {
        "id": "sb-002",
        "topic": "sidebar",
        "difficulty": 1,
        "mode": ["quiz", "speed"],
        "q": "What happens when you click a shortcut in the TF Sidebar?",
        "opts": ["Opens a new browser tab with Setup", "Opens TrackForcePro directly to that tool", "Shows a tooltip", "Does nothing"],
        "answer": 1,
        "explanation": "Clicking a sidebar shortcut <strong>opens TrackForcePro directly to that tool</strong>.",
        "tags": ["sidebar", "shortcuts", "navigation"],
    },
    {
        "id": "sb-003",
        "topic": "sidebar",
        "difficulty": 2,
        "mode": ["quiz", "scenario"],
        "q": "What Quick Tools are built into the TF Sidebar?",
        "opts": ["Only search", "Login As, Language Switcher, Clear Cache", "Only Login As and Logout", "Calculator and notepad"],
        "answer": 1,
        "explanation": "Three Quick Tools: <strong>Login As</strong> (3 modes), <strong>Language Switcher</strong>, and <strong>Clear Cache</strong>.",
        "tags": ["sidebar", "quick-tools"],
    },
    {
        "id": "sb-004",
        "topic": "sidebar",
        "difficulty": 2,
        "mode": ["quiz", "speed"],
        "q": "How many login modes does the TF Sidebar's Login As support?",
        "opts": ["1 — current tab only", "2 — tab and window", "3 — tab, window, and incognito", "4 — tab, window, incognito, popup"],
        "answer": 2,
        "explanation": "Three modes: <strong>Login</strong> (current tab), <strong>Window</strong> (new window), <strong>Incognito</strong> (private window).",
        "tags": ["sidebar", "login-as"],
    },
    {
        "id": "sb-005",
        "topic": "sidebar",
        "difficulty": 1,
        "mode": ["quiz", "truefalse"],
        "q": "How do you open TrackForcePro as a standalone window?",
        "opts": ["Right-click extension icon", "Shift + click the pop button", "Press Ctrl+Shift+T", "Use Chrome menu"],
        "answer": 1,
        "explanation": "Hold <strong>Shift + click the pop button (⧉)</strong> to open as a standalone window.",
        "tags": ["sidebar", "window-mode"],
    },

    # ═══════════════════════════════════════════════
    #  GRAPHQL BUILDER  (topic: graphql)
    # ═══════════════════════════════════════════════
    {
        "id": "gql-001",
        "topic": "graphql",
        "difficulty": 2,
        "mode": ["quiz", "speed"],
        "q": "What editor does TrackForcePro use for the GraphQL builder?",
        "opts": ["Monaco Editor", "Ace Editor", "CodeMirror 6", "VS Code Embedded"],
        "answer": 2,
        "explanation": "TrackForcePro uses <strong>CodeMirror 6</strong> for syntax highlighting and autocomplete.",
        "tags": ["graphql", "editor", "codemirror"],
    },
    {
        "id": "gql-002",
        "topic": "graphql",
        "difficulty": 3,
        "mode": ["quiz", "scenario"],
        "q": "How are child records exported to CSV in the GraphQL Builder?",
        "opts": ["JSON in a single cell", "Skipped", "Expanded into separate rows with parent fields repeated", "Separate CSV file"],
        "answer": 2,
        "explanation": "Child records are <strong>expanded into rows</strong> with parent fields repeated.",
        "tags": ["graphql", "csv", "export"],
    },
    {
        "id": "gql-003",
        "topic": "graphql",
        "difficulty": 2,
        "mode": ["quiz"],
        "q": "Which Salesforce API does the GraphQL Builder query?",
        "opts": ["REST API", "Bulk API", "UI API (GraphQL)", "Metadata API"],
        "answer": 2,
        "explanation": "The GraphQL Builder targets Salesforce's <strong>UI API GraphQL endpoint</strong>.",
        "tags": ["graphql", "api"],
    },

    # ═══════════════════════════════════════════════
    #  SOQL BUILDER  (topic: soql)
    # ═══════════════════════════════════════════════
    {
        "id": "soql-001",
        "topic": "soql",
        "difficulty": 2,
        "mode": ["quiz", "speed"],
        "q": "What is the SOQL Builder's inline edit feature?",
        "opts": ["Raw text editor", "Edit results directly in the table — saved via API", "Drag-and-drop designer", "CSV import tool"],
        "answer": 1,
        "explanation": "Inline edit lets you <strong>edit query results directly</strong> — changes saved to Salesforce via REST API.",
        "tags": ["soql", "inline-edit"],
    },
    {
        "id": "soql-002",
        "topic": "soql",
        "difficulty": 1,
        "mode": ["quiz", "truefalse"],
        "q": "What does the SOQL Builder's query history feature do?",
        "opts": ["Deletes old queries", "Saves and replays previous queries", "Shows Salesforce query log", "Exports execution plans"],
        "answer": 1,
        "explanation": "Query History <strong>saves your previously executed queries</strong> for quick recall.",
        "tags": ["soql", "history"],
    },
    {
        "id": "soql-003",
        "topic": "soql",
        "difficulty": 3,
        "mode": ["quiz"],
        "q": "What visual aid does the SOQL Guidance Engine provide?",
        "opts": ["Auto-formatting only", "Real-time rule-based tips and best practices while building queries", "Only error messages", "Schema diagrams"],
        "answer": 1,
        "explanation": "The <strong>SOQL Guidance Engine</strong> provides real-time tips and best practices as you build queries.",
        "tags": ["soql", "guidance"],
    },
    {
        "id": "soql-004",
        "topic": "soql",
        "difficulty": 1,
        "mode": ["quiz", "truefalse"],
        "q": "How does the SOQL Builder's SObject selector help you find objects?",
        "opts": ["Only shows 10 objects at a time", "Searchable combobox with substring filtering and keyboard navigation", "Requires exact object name typed in full", "Alphabetical scrolling only"],
        "answer": 1,
        "explanation": "The SObject selector is a <strong>searchable combobox</strong> — type any part of an object name to filter, use arrow keys to navigate, and Enter to select.",
        "tags": ["soql", "combobox", "search"],
    },

    # ═══════════════════════════════════════════════
    #  DATA EXPLORER & RECORD SCANNER  (topic: data_explorer)
    # ═══════════════════════════════════════════════
    {
        "id": "de-001",
        "topic": "data_explorer",
        "difficulty": 2,
        "mode": ["quiz", "scenario"],
        "q": "What does the Record Scanner's Compare mode do?",
        "opts": ["Compares SOQL queries", "Side-by-side field comparison with diff highlighting", "Compares API versions", "Compares permissions"],
        "answer": 1,
        "explanation": "Compare mode shows <strong>side-by-side fields with diff highlighting</strong> — green matching, red different.",
        "tags": ["data-explorer", "compare", "record-scanner"],
    },
    {
        "id": "de-002",
        "topic": "data_explorer",
        "difficulty": 1,
        "mode": ["quiz", "speed"],
        "q": "What does the Favicon Manager do?",
        "opts": ["Changes TFP icon", "Custom favicons to distinguish Salesforce orgs", "Downloads page icons", "Manages bookmarks"],
        "answer": 1,
        "explanation": "The Favicon Manager lets you assign <strong>custom colors, shapes, and labels</strong> per org.",
        "tags": ["data-explorer", "favicon"],
    },
    {
        "id": "de-003",
        "topic": "data_explorer",
        "difficulty": 2,
        "mode": ["quiz"],
        "q": "How many shapes are available for custom org favicons?",
        "opts": ["3", "8 (circle, square, rounded, cloud, sfcloud, diamond, hexagon, shield)", "2", "Unlimited SVG"],
        "answer": 1,
        "explanation": "<strong>Eight shapes:</strong> circle, square, rounded, cloud, sfcloud, diamond, hexagon, shield.",
        "tags": ["data-explorer", "favicon", "shapes"],
    },
    {
        "id": "de-004",
        "topic": "data_explorer",
        "difficulty": 3,
        "mode": ["quiz", "scenario"],
        "q": "What does the Metadata Explorer do?",
        "opts": ["Exports to XML", "Browse metadata types, components, and dependencies", "Deploys packages", "Only shows custom objects"],
        "answer": 1,
        "explanation": "Browse and inspect <strong>metadata types, components, and dependencies</strong>.",
        "tags": ["data-explorer", "metadata"],
    },
    {
        "id": "de-005",
        "topic": "data_explorer",
        "difficulty": 2,
        "mode": ["quiz"],
        "q": "What does the Schema Visualizer show?",
        "opts": ["DB table schemas", "Visual relationship diagrams between objects", "Only field types", "SQL plans"],
        "answer": 1,
        "explanation": "Shows <strong>visual relationship diagrams</strong> between Salesforce objects.",
        "tags": ["data-explorer", "schema"],
    },
    {
        "id": "de-006",
        "topic": "data_explorer",
        "difficulty": 3,
        "mode": ["quiz"],
        "q": "What does the Automation Inspector analyze?",
        "opts": ["Only Apex triggers", "Flows, Process Builders, Workflow Rules, and all automation", "Only scheduled jobs", "Email alerts only"],
        "answer": 1,
        "explanation": "Comprehensive view of <strong>all automation</strong> — Flows, PBs, Workflow Rules, Triggers, etc.",
        "tags": ["data-explorer", "automation"],
    },

    # ═══════════════════════════════════════════════
    #  SECURITY MANAGER  (topic: security)
    # ═══════════════════════════════════════════════
    {
        "id": "sec-001",
        "topic": "security",
        "difficulty": 2,
        "mode": ["quiz", "scenario"],
        "q": "What does the Security Manager allow you to browse?",
        "opts": ["User passwords", "Profiles, Permission Sets, and Permission Set Groups", "Login history only", "Encryption keys"],
        "answer": 1,
        "explanation": "Split-pane browser for <strong>Profiles, Permission Sets, and PS Groups</strong>.",
        "tags": ["security", "profiles", "permission-sets"],
    },

    # ═══════════════════════════════════════════════
    #  ORG TOOLS  (topic: org_tools)
    # ═══════════════════════════════════════════════
    {
        "id": "org-001",
        "topic": "org_tools",
        "difficulty": 2,
        "mode": ["quiz", "scenario"],
        "q": "What can you do with Custom Labels in Org Tools?",
        "opts": ["Only view", "Search, inline-edit, translate, and bulk import/export", "Only export", "Only create new ones"],
        "answer": 1,
        "explanation": "Custom Labels supports <strong>search, inline editing, 20-language translation, bulk import/export</strong>.",
        "tags": ["org-tools", "custom-labels"],
    },
    {
        "id": "org-002",
        "topic": "org_tools",
        "difficulty": 1,
        "mode": ["quiz"],
        "q": "What does the Org Limits tool display?",
        "opts": ["Only storage", "API calls, storage, and all governor limits with usage %", "Only Apex limits", "License count only"],
        "answer": 1,
        "explanation": "Shows <strong>all governor limits</strong> with current usage percentages.",
        "tags": ["org-tools", "limits"],
    },
    {
        "id": "org-003",
        "topic": "org_tools",
        "difficulty": 2,
        "mode": ["quiz"],
        "q": "What can you do with Debug Logs in Org Tools?",
        "opts": ["Only view logs", "View, create, and manage trace flags for users", "Only delete logs", "Download Apex source"],
        "answer": 1,
        "explanation": "View trace flags, create new ones, and <strong>manage debug logging</strong> per user.",
        "tags": ["org-tools", "debug-logs"],
    },
    {
        "id": "org-004",
        "topic": "org_tools",
        "difficulty": 2,
        "mode": ["quiz", "scenario"],
        "q": "What does the Deployment tracker show?",
        "opts": ["Only past deploys", "Active, queued, and completed status with component details", "Only failed deploys", "Code coverage only"],
        "answer": 1,
        "explanation": "Shows <strong>active, queued, and completed deployments</strong> with status and error details.",
        "tags": ["org-tools", "deployments"],
    },

    # ═══════════════════════════════════════════════
    #  PLATFORM EVENTS & LMS  (topic: platform_events)
    # ═══════════════════════════════════════════════
    {
        "id": "pe-001",
        "topic": "platform_events",
        "difficulty": 2,
        "mode": ["quiz", "speed"],
        "q": "What streaming protocol does TrackForcePro use for Platform Events?",
        "opts": ["WebSocket", "Server-Sent Events", "CometD", "gRPC"],
        "answer": 2,
        "explanation": "Uses <strong>CometD</strong> (Salesforce's Bayeux-based streaming protocol).",
        "tags": ["platform-events", "cometd", "streaming"],
    },

    # ═══════════════════════════════════════════════
    #  USER MANAGER  (topic: user_manager)
    # ═══════════════════════════════════════════════
    {
        "id": "um-001",
        "topic": "user_manager",
        "difficulty": 2,
        "mode": ["quiz", "scenario"],
        "q": "What does the Permission Matrix in User Manager show?",
        "opts": ["User passwords", "All permissions across Profile, PSets, and PS Groups", "Login attempts", "DB schema perms"],
        "answer": 1,
        "explanation": "Shows a <strong>comprehensive grid of all permissions</strong> traced across Profile, PSets, PS Groups.",
        "tags": ["user-manager", "permissions"],
    },
    {
        "id": "um-002",
        "topic": "user_manager",
        "difficulty": 2,
        "mode": ["quiz"],
        "q": "What does Freeze/Unfreeze in User Manager do?",
        "opts": ["Locks browser", "Temporarily prevents login without deactivating", "Deletes account", "Pauses emails"],
        "answer": 1,
        "explanation": "<strong>Temporarily prevents login</strong> without deactivating the account.",
        "tags": ["user-manager", "freeze"],
    },
    {
        "id": "um-003",
        "topic": "user_manager",
        "difficulty": 2,
        "mode": ["quiz"],
        "q": "What is the Access Summary in User Manager?",
        "opts": ["Record access log", "Comprehensive view of object, field, and record-level access", "Login history", "IP whitelist"],
        "answer": 1,
        "explanation": "Shows <strong>all object-level, field-level, and record-level access</strong> for a user.",
        "tags": ["user-manager", "access"],
    },

    # ═══════════════════════════════════════════════
    #  ARCHITECTURE  (topic: architecture)
    # ═══════════════════════════════════════════════
    {
        "id": "arch-001",
        "topic": "architecture",
        "difficulty": 2,
        "mode": ["quiz"],
        "q": "How does TrackForcePro prevent cross-org data leakage?",
        "opts": ["No caching", "Server-side storage", "Cache keys scoped by org ID", "Clears on every load"],
        "answer": 2,
        "explanation": "Cache keys are <strong>scoped by org ID</strong> to prevent cross-org data leaks.",
        "tags": ["architecture", "cache", "security"],
    },
    {
        "id": "arch-002",
        "topic": "architecture",
        "difficulty": 2,
        "mode": ["quiz"],
        "q": "How does the extension handle multiple Salesforce orgs?",
        "opts": ["One at a time", "Isolated session per org with cache scoping", "Must reinstall", "No multi-org support"],
        "answer": 1,
        "explanation": "Supports <strong>multi-org workflows</strong> with session isolation and org-scoped caching.",
        "tags": ["architecture", "multi-org"],
    },
    {
        "id": "arch-003",
        "topic": "architecture",
        "difficulty": 1,
        "mode": ["quiz", "truefalse"],
        "q": "How does TrackForcePro detect your Salesforce session?",
        "opts": ["Manual credentials", "OAuth popup", "Content script auto-detects", "Reads saved passwords"],
        "answer": 2,
        "explanation": "A <strong>content script</strong> on Salesforce pages auto-detects the session.",
        "tags": ["architecture", "content-script", "session"],
    },
    {
        "id": "arch-004",
        "topic": "architecture",
        "difficulty": 2,
        "mode": ["quiz"],
        "q": "What does single-instance enforcement mean?",
        "opts": ["One user total", "One TFP window per org", "One computer only", "One API call at a time"],
        "answer": 1,
        "explanation": "Enforces <strong>one window per org</strong> — duplicate attempts focus the existing window.",
        "tags": ["architecture", "single-instance"],
    },
    {
        "id": "arch-005",
        "topic": "architecture",
        "difficulty": 1,
        "mode": ["quiz", "truefalse"],
        "q": "Which browsers does TrackForcePro support?",
        "opts": ["Chrome only", "Chrome and Firefox", "Chrome, Edge, and Chromium-based browsers", "All including Safari"],
        "answer": 2,
        "explanation": "Works on <strong>Chrome, Edge, Brave, Opera</strong> and other Chromium browsers.",
        "tags": ["architecture", "browsers"],
    },

    # ═══════════════════════════════════════════════
    #  GENERAL / MISC  (topic: general)
    # ═══════════════════════════════════════════════
    {
        "id": "gen-001",
        "topic": "general",
        "difficulty": 1,
        "mode": ["quiz", "speed"],
        "q": "What is the Login As feature?",
        "opts": ["Creates new user", "Opens a session as another user for troubleshooting", "Changes username", "Shares credentials"],
        "answer": 1,
        "explanation": "Login As lets you <strong>open a session as another user</strong> to troubleshoot.",
        "tags": ["general", "login-as"],
    },
    {
        "id": "gen-002",
        "topic": "general",
        "difficulty": 1,
        "mode": ["quiz"],
        "q": "What keyboard shortcut opens the Command Palette?",
        "opts": ["Ctrl+P", "Ctrl+K / Cmd+K", "Ctrl+Shift+P", "Alt+Space"],
        "answer": 1,
        "explanation": "<strong>Ctrl+K / Cmd+K</strong> opens the command palette with 13+ built-in commands.",
        "tags": ["general", "command-palette", "shortcuts"],
    },
    {
        "id": "gen-003",
        "topic": "general",
        "difficulty": 2,
        "mode": ["quiz", "truefalse"],
        "q": "What context menu items does TrackForcePro add when you right-click on SF pages?",
        "opts": ["Only Copy Record ID", "Show All Data, Field History, Sharing, SOQL Builder, Copy Record ID", "Only SOQL Builder", "No context menu"],
        "answer": 1,
        "explanation": "Five items: <strong>Show All Data, Field History, Sharing, SOQL Builder, Copy Record ID</strong>.",
        "tags": ["general", "context-menu"],
    },
    {
        "id": "gen-004",
        "topic": "general",
        "difficulty": 2,
        "mode": ["quiz"],
        "q": "What does 'Show All Data' do on a Salesforce record page?",
        "opts": ["Shows raw JSON", "Floating inspector with field explorer, search, and lookup navigation", "Opens Developer Console", "Exports record as CSV"],
        "answer": 1,
        "explanation": "Injects a <strong>floating panel with full field explorer</strong>, search/filter, and breadcrumb navigation.",
        "tags": ["general", "show-all-data"],
    },
    {
        "id": "gen-005",
        "topic": "general",
        "difficulty": 3,
        "mode": ["quiz"],
        "q": "How does inline field editing work in the All Fields inspector and Show All Data panel?",
        "opts": ["Single-click any field", "Double-click an updateable field — type-aware inputs, Enter to save", "Right-click to edit", "Edit button per field"],
        "answer": 1,
        "explanation": "<strong>Double-click any updateable field</strong> — text, boolean, textarea inputs. Enter to save, Escape to cancel. Works in both the Data Explorer All Fields table and the Show All Data panel on record pages.",
        "tags": ["general", "inline-edit", "data-explorer", "show-all-data"],
    },
    {
        "id": "gen-006",
        "topic": "general",
        "difficulty": 1,
        "mode": ["quiz", "truefalse"],
        "q": "What keyboard shortcut toggles the Show All Data panel on a Salesforce record page?",
        "opts": ["Ctrl+Shift+S / Cmd+Shift+S", "Ctrl+Shift+X / ⌘+Shift+X", "Ctrl+K / Cmd+K", "Ctrl+D / Cmd+D"],
        "answer": 1,
        "explanation": "<strong>Ctrl+Shift+X / ⌘+Shift+X</strong> toggles Show All Data. Ctrl+Shift+S is for the TF Sidebar, and Ctrl+K is for the Command Palette.",
        "tags": ["general", "show-all-data", "shortcuts"],
    },
]
# fmt: on


def get_questions_by_topic(topic: str) -> list:
    """Get all questions for a specific topic."""
    return [q for q in QUESTIONS if q["topic"] == topic]


def get_questions_by_difficulty(difficulty: int) -> list:
    """Get all questions at a specific difficulty level."""
    return [q for q in QUESTIONS if q["difficulty"] == difficulty]


def get_questions_by_mode(mode: str) -> list:
    """Get all questions compatible with a game mode."""
    return [q for q in QUESTIONS if mode in q["mode"]]


def get_question_by_id(qid: str):
    """Get a single question by ID."""
    for q in QUESTIONS:
        if q["id"] == qid:
            return q
    return None
