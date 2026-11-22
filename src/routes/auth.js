const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const { db } = require('../db');
const { logSecurityEvent } = require('../logger');
const { detectSQLi } = require('../detectors');

router.post('/login', (req, res) => {
  const { username, password, securityMode } = req.body;
  const isSecure = securityMode === 'secure';
  const clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress || '127.0.0.1';

  if (!username || !password) {
    return res.status(400).json({ success: false, message: 'Username and password are required.' });
  }

  const hasSQLi = detectSQLi(username) || detectSQLi(password);

  if (!isSecure) {
    const vulnerableQuery = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
    console.log(`[SQL EXEC - VULNERABLE]: ${vulnerableQuery}`);

    try {
      const user = db.prepare(vulnerableQuery).get();

      if (user) {
        if (hasSQLi) {
          logSecurityEvent({
            ip: clientIp,
            eventType: 'SQLI_AUTH_BYPASS_SUCCESSFUL',
            severity: 'CRITICAL',
            endpoint: '/api/auth/login',
            payload: { username, password, executedQuery: vulnerableQuery },
            actionTaken: 'EXPLOITED'
          });
        }

        res.cookie('session_token', `token_user_${user.id}_${user.username}`, {
          httpOnly: false,
          sameSite: 'lax'
        });

        return res.json({
          success: true,
          message: `Login successful with role [${user.role}].`,
          user: { id: user.id, username: user.username, role: user.role, fullName: user.full_name },
          executedQuery: vulnerableQuery,
          vulnerabilityTriggered: hasSQLi
        });
      } else {
        return res.status(401).json({
          success: false,
          message: 'Invalid username or password.',
          executedQuery: vulnerableQuery
        });
      }
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
        eventType: 'SQLI_ATTACK_BLOCKED',
        severity: 'CRITICAL',
        endpoint: '/api/auth/login',
        payload: { username, password },
        actionTaken: 'BLOCKED'
      });
      return res.status(400).json({
        success: false,
        message: 'SQL Injection payload detected. Request blocked.',
        blocked: true
      });
    }

    try {
      const stmt = db.prepare('SELECT * FROM users WHERE username = ?');
      const user = stmt.get(username);

      if (user && bcrypt.compareSync(password, user.password)) {
        res.cookie('session_token', `secure_token_${user.id}_${Date.now()}`, {
          httpOnly: true,
          sameSite: 'strict',
          secure: false
        });

        return res.json({
          success: true,
          message: `Login successful as [${user.role}].`,
          user: { id: user.id, username: user.username, role: user.role, fullName: user.full_name }
        });
      } else {
        logSecurityEvent({
          ip: clientIp,
          eventType: 'LOGIN_FAILED',
          severity: 'LOW',
          endpoint: '/api/auth/login',
          payload: { username },
          actionTaken: 'REJECTED'
        });

        return res.status(401).json({
          success: false,
          message: 'Invalid username or password.'
        });
      }
    } catch (err) {
      return res.status(500).json({ success: false, message: 'Internal server error.' });
    }
  }
});

module.exports = router;
