const express = require('express');
const router = express.Router();
const { db } = require('../db');
const { logSecurityEvent } = require('../logger');
const { detectXSS, escapeHTML } = require('../detectors');

router.get('/', (req, res) => {
  const isSecure = req.query.securityMode === 'secure';

  try {
    const comments = db.prepare('SELECT id, author, content, created_at FROM comments ORDER BY id DESC').all();

    if (isSecure) {
      const sanitized = comments.map(c => ({
        ...c,
        author: escapeHTML(c.author),
        content: escapeHTML(c.content)
      }));
      return res.json({ success: true, data: sanitized, mode: 'secure' });
    } else {
      return res.json({ success: true, data: comments, mode: 'vulnerable' });
    }
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

router.post('/', (req, res) => {
  const { author, content, securityMode } = req.body;
  const isSecure = securityMode === 'secure';
  const clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress || '127.0.0.1';

  if (!author || !content) {
    return res.status(400).json({ success: false, message: 'Author and content cannot be empty.' });
  }

  const hasXSS = detectXSS(author) || detectXSS(content);

  if (!isSecure) {
    try {
      const stmt = db.prepare('INSERT INTO comments (author, content) VALUES (?, ?)');
      const info = stmt.run(author, content);

      if (hasXSS) {
        logSecurityEvent({
          ip: clientIp,
          eventType: 'STORED_XSS_PAYLOAD_SAVED',
          severity: 'HIGH',
          endpoint: '/api/comments [POST]',
          payload: { author, content },
          actionTaken: 'STORED'
        });
      }

      return res.json({
        success: true,
        message: 'Comment posted successfully.',
        id: info.lastInsertRowid,
        vulnerabilityTriggered: hasXSS
      });
    } catch (err) {
      return res.status(500).json({ success: false, message: err.message });
    }

  } else {
    if (hasXSS) {
      logSecurityEvent({
        ip: clientIp,
        eventType: 'STORED_XSS_ATTACK_DETECTED',
        severity: 'HIGH',
        endpoint: '/api/comments [POST]',
        payload: { author, content },
        actionTaken: 'SANITIZED'
      });
    }

    try {
      const safeAuthor = escapeHTML(author);
      const safeContent = escapeHTML(content);

      const stmt = db.prepare('INSERT INTO comments (author, content) VALUES (?, ?)');
      const info = stmt.run(safeAuthor, safeContent);

      return res.json({
        success: true,
        message: hasXSS 
          ? 'Comment sanitized and stored securely.' 
          : 'Comment posted securely.',
        id: info.lastInsertRowid,
        sanitized: hasXSS
      });
    } catch (err) {
      return res.status(500).json({ success: false, message: err.message });
    }
  }
});

router.post('/reset', (req, res) => {
  try {
    db.prepare('DELETE FROM comments').run();
    const insert = db.prepare('INSERT INTO comments (author, content) VALUES (?, ?)');
    insert.run('Alice', 'The Dell XPS 15 performs exceptionally well.');
    insert.run('John Doe', 'Great keyboard, very comfortable for typing.');
    res.json({ success: true, message: 'Sample comments reset successfully.' });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

module.exports = router;
