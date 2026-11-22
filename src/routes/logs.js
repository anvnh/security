const express = require('express');
const router = express.Router();
const { db } = require('../db');

router.get('/', (req, res) => {
  try {
    const page = Math.max(1, parseInt(req.query.page, 10) || 1);
    const limit = Math.max(1, Math.min(100, parseInt(req.query.limit, 10) || 15));
    const offset = (page - 1) * limit;

    const total = db.prepare('SELECT COUNT(*) as count FROM security_logs').get().count;
    const totalPages = Math.ceil(total / limit) || 1;

    const stmt = db.prepare('SELECT * FROM security_logs ORDER BY id DESC LIMIT ? OFFSET ?');
    const logs = stmt.all(limit, offset);

    res.json({
      success: true,
      data: logs,
      pagination: {
        total,
        page,
        limit,
        totalPages
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

router.get('/stats', (req, res) => {
  try {
    const total = db.prepare('SELECT COUNT(*) as count FROM security_logs').get().count;
    const sqliCount = db.prepare("SELECT COUNT(*) as count FROM security_logs WHERE event_type LIKE '%SQLI%'").get().count;
    const xssCount = db.prepare("SELECT COUNT(*) as count FROM security_logs WHERE event_type LIKE '%XSS%'").get().count;
    const criticalCount = db.prepare("SELECT COUNT(*) as count FROM security_logs WHERE severity = 'CRITICAL'").get().count;

    res.json({
      success: true,
      data: {
        total,
        sqliCount,
        xssCount,
        criticalCount
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

router.delete('/', (req, res) => {
  try {
    db.prepare('DELETE FROM security_logs').run();
    res.json({ success: true, message: 'Security logs cleared successfully.' });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

module.exports = router;
