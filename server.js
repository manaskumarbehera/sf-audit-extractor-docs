const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.PORT || 3000);
const ROOT = __dirname;

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

function routeToFile(urlPath) {
  if (urlPath === '/' || urlPath === '') {
    return 'landing.html';
  }
  if (urlPath === '/docs' || urlPath === '/docs/') {
    return 'index.html';
  }
  return urlPath;
}

const server = http.createServer((req, res) => {
  const rawPath = routeToFile(req.url || '/');
  const target = safeResolve(rawPath);

  if (!target) {
    res.writeHead(400, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Bad request');
    return;
  }

  fs.stat(target, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }
    sendFile(target, res);
  });
});

server.listen(PORT, () => {
  console.log('TrackForcePro web server running on port ' + PORT);
});

