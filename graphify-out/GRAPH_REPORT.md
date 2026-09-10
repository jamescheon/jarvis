# Graph Report - jarvis  (2026-09-10)

## Corpus Check
- Corpus is ~4,798 words - fits in a single context window. You may not need a graph.

## Summary
- 72 nodes · 90 edges · 10 communities (6 shown, 4 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.8)
- Token cost: 0 input · 125,582 output

## Community Hubs (Navigation)
- Voice Command Dispatch (Frontend)
- PC-Task & Search Tools (Backend)
- Chat API Handler
- PWA Manifest
- JARVIS Core & Wake Word
- Vercel Deploy Config
- Naver Ads Search Volume
- Service Worker Cache
- App Icon
- Root

## God Nodes (most connected - your core abstractions)
1. `handler` - 6 edges
2. `JarvisHandler` - 6 edges
3. `speak()` - 6 edges
4. `handleCommand()` - 6 edges
5. `runPcTaskFlow()` - 6 edges
6. `sendToClaude()` - 6 edges
7. `finishTurn()` - 6 edges
8. `tryAppCommand()` - 4 edges
9. `trySearchCommand()` - 4 edges
10. `startListening()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `J.A.R.V.I.S. Voice Assistant` --conceptually_related_to--> `anthropic Python package dependency`  [INFERRED]
  index.html → requirements.txt
- `anthropic Python package dependency` --conceptually_related_to--> `/api/chat backend endpoint (Claude)`  [INFERRED]
  requirements.txt → index.html

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Voice Command Dispatch Chain** — index_handlecommand, index_tryappcommand, index_trysearchcommand, index_trypctask, index_sendtoclaude [EXTRACTED 1.00]
- **PC Task Execution Flow** — index_trypctask, index_runpctaskflow, index_api_pc_task_endpoint [EXTRACTED 0.95]
- **Wake Word Conversation Loop** — index_wake_word_detection, index_startlistening, index_finishturn [INFERRED 0.85]

## Communities (10 total, 4 thin omitted)

### Community 0 - "Voice Command Dispatch (Frontend)"
Cohesion: 0.16
Nodes (18): /api/pc-task backend endpoint, APP_LINKS map, Post-response listening continuity (skip re-saying wake word), finishTurn(), handleCommand(), Male neural voice selection heuristic, Post-TTS mic deaf window (echo avoidance), openApp() (+10 more)

### Community 1 - "PC-Task & Search Tools (Backend)"
Cohesion: 0.16
Nodes (9): local_search(), _strip_tags(), Run a natural-language instruction through the local Claude Code CLI, headless,…, run_task(), extract_reply(), find_pc_task_request(), JarvisHandler, BaseHTTPRequestHandler (+1 more)

### Community 2 - "Chat API Handler"
Cohesion: 0.31
Nodes (5): extract_reply(), find_pc_task_request(), handler, BaseHTTPRequestHandler, run_with_tools()

### Community 3 - "PWA Manifest"
Cohesion: 0.20
Nodes (9): background_color, description, display, icons, name, orientation, short_name, start_url (+1 more)

### Community 4 - "JARVIS Core & Wake Word"
Cohesion: 0.33
Nodes (6): /api/chat backend endpoint (Claude), J.A.R.V.I.S. Voice Assistant, SpeechRecognition (Web Speech API) Usage, startListening(), Wake Word Detection ("자비스"), anthropic Python package dependency

### Community 5 - "Vercel Deploy Config"
Cohesion: 0.50
Nodes (3): cleanUrls, $schema, trailingSlash

## Knowledge Gaps
- **18 isolated node(s):** `name`, `short_name`, `description`, `start_url`, `display` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 30 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `name`, `short_name`, `description` to the rest of the system?**
  _18 weakly-connected nodes found - possible documentation gaps or missing edges._