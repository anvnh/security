const express = require('express');
const router = express.Router();
const { db } = require('../db');
const { logSecurityEvent } = require('../logger');
const { detectSQLi } = require('../detectors');

router.get('/search', (req, res) => {
  const q = req.query.q || '';
  const isSecure = req.query.securityMode === 'secure';
  const clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress || '127.0.0.1';

  const hasSQLi = detectSQLi(q);

  if (!isSecure) {
    const vulnerableQuery = `SELECT id, name, category, price, description FROM products WHERE name LIKE '%${q}%'`;
    console.log(`[SQL SEARCH EXEC - VULNERABLE]: ${vulnerableQuery}`);

    try {
      const results = db.prepare(vulnerableQuery).all();

      if (hasSQLi) {
        logSecurityEvent({
          ip: clientIp,
          eventType: 'SQLI_UNION_EXPLOITED',
          severity: 'HIGH',
          endpoint: '/api/products/search',
          payload: { queryParam: q, executedQuery: vulnerableQuery },
          actionTaken: 'DATA_EXFILTRATED'
        });
      }

      return res.json({
        success: true,
        count: results.length,
        data: results,
        executedQuery: vulnerableQuery,
        vulnerabilityTriggered: hasSQLi
      });
    } catch (err) {
      return res.status(500).json({
        success: false,
        message: 'Database error: ' + err.message,
        executedQuery: vulnerableQuery
      });
    }

  } else {
    if (hasSQLi) {
      logSecurityEvent({
        ip: clientIp,
        eventType: 'SQLI_SEARCH_ATTACK_BLOCKED',
        severity: 'HIGH',
        endpoint: '/api/products/search',
        payload: { queryParam: q },
        actionTaken: 'BLOCKED'
      });
      return res.status(400).json({
        success: false,
        message: 'SQL Injection payload detected in search query. Request blocked.',
        blocked: true
      });
    }

    try {
      const stmt = db.prepare('SELECT id, name, category, price, description FROM products WHERE name LIKE ?');
      const results = stmt.all(`%${q}%`);

      return res.json({
        success: true,
        count: results.length,
        data: results
      });
    } catch (err) {
      return res.status(500).json({ success: false, message: 'Internal server error.' });
    }
  }
});

router.get('/', (req, res) => {
  try {
    const products = db.prepare('SELECT id, name, category, price, description FROM products').all();
    res.json({ success: true, data: products });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

module.exports = router;
