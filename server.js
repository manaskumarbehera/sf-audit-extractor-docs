const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.PORT || 3000);
const ROOT = __dirname;

/* ── Leaderboard data file ── */
const LB_FILE = path.join(ROOT, 'data', 'leaderboard.json');

// Ensure data directory exists
(function ensureDataDir() {
    const dir = path.dirname(LB_FILE);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
    if (!fs.existsSync(LB_FILE)) {
        fs.writeFileSync(LB_FILE, '[]', 'utf-8');
    }
})();

function readLeaderboard() {
    try {
        const raw = fs.readFileSync(LB_FILE, 'utf-8');
        return JSON.parse(raw);
    } catch (e) {
        return [];
    }
}

function writeLeaderboard(entries) {
    fs.writeFileSync(LB_FILE, JSON.stringify(entries), 'utf-8');
}

/* ── Uninstall feedback data file ── */
// Lazily created on first write (keeps module import side-effect-free for tests)
// and mirrors the leaderboard read/append/write/size-cap pattern.
const UF_FILE = path.join(ROOT, 'data', 'uninstall-feedback.json');

function readUninstallFeedback() {
    try {
        const raw = fs.readFileSync(UF_FILE, 'utf-8');
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
        return [];
    }
}

function writeUninstallFeedback(entries) {
    const dir = path.dirname(UF_FILE);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(UF_FILE, JSON.stringify(entries), 'utf-8');
}

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.txt': 'text/plain; charset=utf-8'
};

function safeResolve(requestPath) {
  const clean = decodeURIComponent(requestPath.split('?')[0]);
  const normalized = path.normalize(clean).replace(/^\/+/, '');
  const resolved = path.resolve(ROOT, normalized);
  if (!resolved.startsWith(ROOT)) {
    return null;
  }
  return resolved;
}

function sendFile(filePath, res) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
}

function routeToFile(rawUrl) {
  // Strip the query string before matching. The extension's uninstall URL always
  // carries `?v=<version>` (e.g. /uninstall-feedback?v=2.10.0), so equality
  // checks must compare the path only — otherwise the alias never matches.
  const urlPath = String(rawUrl).split('?')[0];
  if (urlPath === '/' || urlPath === '') {
    // Keep root stable for Heroku/GitHub Pages even if landing.html is removed.
    return 'index.html';
  }
  if (urlPath === '/docs' || urlPath === '/docs/') {
    return 'index.html';
  }
  // Extensionless alias: the published uninstall URL has no `.html` suffix.
  if (urlPath === '/uninstall-feedback' || urlPath === '/uninstall-feedback/') {
    return 'uninstall-feedback.html';
  }
  return urlPath;
}

/* ── CORS headers for API endpoints ── */
function setCorsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function sendJson(res, statusCode, data) {
    setCorsHeaders(res);
    res.writeHead(statusCode, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify(data));
}

function readBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => { body += chunk; if (body.length > 1e6) { req.destroy(); reject(new Error('Payload too large')); } });
        req.on('end', () => resolve(body));
        req.on('error', reject);
    });
}

/* ── API route handler ── */
async function handleApi(req, res) {
    const urlPath = req.url.split('?')[0];
    const method = req.method;

    // CORS preflight
    if (method === 'OPTIONS') {
        setCorsHeaders(res);
        res.writeHead(204);
        res.end();
        return true;
    }

    // GET /api/leaderboard — return all entries
    if (urlPath === '/api/leaderboard' && method === 'GET') {
        const entries = readLeaderboard();
        sendJson(res, 200, { ok: true, entries: entries });
        return true;
    }

    // POST /api/leaderboard — add a score entry
    if (urlPath === '/api/leaderboard' && method === 'POST') {
        try {
            const raw = await readBody(req);
            const entry = JSON.parse(raw);

            // Validate required fields
            if (!entry.name || !entry.mode || typeof entry.score !== 'number') {
                sendJson(res, 400, { ok: false, error: 'Missing required fields: name, mode, score' });
                return true;
            }

            // Sanitize & build entry
            const sanitized = {
                name: String(entry.name).substring(0, 50),
                email: String(entry.email || '').substring(0, 100),
                score: Number(entry.score) || 0,
                mode: String(entry.mode).substring(0, 20),
                correct: Number(entry.correct) || 0,
                total: Number(entry.total) || 0,
                pct: Number(entry.pct) || 0,
                date: new Date().toISOString()
            };

            const lb = readLeaderboard();
            lb.push(sanitized);

            // Keep top 500, sorted by score descending
            lb.sort((a, b) => b.score - a.score);
            const trimmed = lb.slice(0, 500);
            writeLeaderboard(trimmed);

            sendJson(res, 201, { ok: true, entry: sanitized, total: trimmed.length });
            return true;
        } catch (e) {
            sendJson(res, 400, { ok: false, error: 'Invalid JSON body' });
            return true;
        }
    }

    // DELETE /api/leaderboard — clear all entries (or by email query param)
    if (urlPath === '/api/leaderboard' && method === 'DELETE') {
        try {
            const raw = await readBody(req);
            let email = null;
            try { email = JSON.parse(raw).email; } catch (e) {}

            if (email) {
                // Delete only this player's entries
                const lb = readLeaderboard();
                const filtered = lb.filter(e => e.email !== email);
                writeLeaderboard(filtered);
                sendJson(res, 200, { ok: true, removed: lb.length - filtered.length });
            } else {
                // Clear all
                writeLeaderboard([]);
                sendJson(res, 200, { ok: true, removed: 'all' });
            }
            return true;
        } catch (e) {
            sendJson(res, 400, { ok: false, error: 'Invalid request' });
            return true;
        }
    }

    // POST /api/uninstall-feedback — record why a user uninstalled
    if (urlPath === '/api/uninstall-feedback' && method === 'POST') {
        try {
            const raw = await readBody(req);
            let entry = {};
            try { entry = JSON.parse(raw) || {}; } catch (e) { entry = {}; }

            // Normalize reasons to a capped array of short strings.
            let reasons = entry.reasons;
            if (typeof reasons === 'string') { reasons = [reasons]; }
            if (!Array.isArray(reasons)) { reasons = []; }
            reasons = reasons
                .filter(r => typeof r === 'string' && r.trim())
                .slice(0, 12)
                .map(r => String(r).substring(0, 60));

            const sanitized = {
                reasons: reasons,
                comment: String(entry.comment || '').substring(0, 2000),
                email: String(entry.email || '').substring(0, 100),
                version: String(entry.version || '').substring(0, 20),
                date: new Date().toISOString()
            };

            const all = readUninstallFeedback();
            all.push(sanitized);
            // Keep the most recent 2000 submissions to bound the file size.
            const trimmed = all.slice(-2000);
            writeUninstallFeedback(trimmed);

            sendJson(res, 201, { ok: true });
            return true;
        } catch (e) {
            sendJson(res, 400, { ok: false, error: 'Invalid request' });
            return true;
        }
    }

    return false; // Not an API route
}

const server = http.createServer(async (req, res) => {
  const urlPath = req.url.split('?')[0];

  // Handle API routes first
  if (urlPath.startsWith('/api/')) {
      try {
          const handled = await handleApi(req, res);
          if (handled) return;
      } catch (e) {
          sendJson(res, 500, { ok: false, error: 'Internal server error' });
          return;
      }
      sendJson(res, 404, { ok: false, error: 'API endpoint not found' });
      return;
  }

  // Block direct access to /data/ directory (leaderboard data)
  if (urlPath.startsWith('/data/') || urlPath === '/data') {
      res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Forbidden');
      return;
  }

  // Static file serving
  const filePath = safeResolve(routeToFile(req.url));

  if (!filePath) {
    res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Forbidden');
    return;
  }

  fs.stat(filePath, (err, stats) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }
    if (stats.isDirectory()) {
      const indexPath = path.join(filePath, 'index.html');
      sendFile(indexPath, res);
    } else {
      sendFile(filePath, res);
    }
  });
});

// Only start listening when run directly (`node server.js`, as the Procfile
// does). When required from a test, expose the pure helpers without binding a
// port so the import has no side effects.
if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`TrackForcePro Web Hub running on http://localhost:${PORT}`);
    console.log(`Leaderboard API: http://localhost:${PORT}/api/leaderboard`);
  });
}

module.exports = { routeToFile, safeResolve };

