const express = require('express');
const router = express.Router();
const { logSecurityEvent } = require('../logger');
const { detectXSS, escapeHTML } = require('../detectors');

router.get('/reflected', (req, res) => {
  const q = req.query.q || '';
  const isSecure = req.query.securityMode === 'secure';
  const clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress || '127.0.0.1';

  const hasXSS = detectXSS(q);

  if (!isSecure) {
    if (hasXSS) {
      logSecurityEvent({
        ip: clientIp,
        eventType: 'REFLECTED_XSS_ATTACK_EXECUTED',
        severity: 'MEDIUM',
        endpoint: '/api/search/reflected',
        payload: { queryParam: q },
        actionTaken: 'REFLECTED_UNESCAPED'
      });
    }

    return res.json({
      success: true,
      query: q,
      htmlSnippet: `<div class="search-result-banner">Search results for: <strong>${q}</strong></div>`,
      mode: 'vulnerable',
      vulnerabilityTriggered: hasXSS
    });

  } else {
    if (hasXSS) {
      logSecurityEvent({
        ip: clientIp,
        eventType: 'REFLECTED_XSS_ATTACK_NEUTRALIZED',
        severity: 'MEDIUM',
        endpoint: '/api/search/reflected',
        payload: { queryParam: q },
        actionTaken: 'ENCODED'
      });
    }

    const safeQ = escapeHTML(q);

    return res.json({
      success: true,
      query: safeQ,
      htmlSnippet: `<div class="search-result-banner">Search results for: <strong>${safeQ}</strong></div>`,
      mode: 'secure',
      sanitized: hasXSS
    });
  }
});

module.exports = router;
