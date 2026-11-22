const SQLI_PATTERNS = [
  /(\%27)|(\')|(\-\-)|(\%23)|(#)/i,
  /\b(OR|AND)\b.+[=><]/i,
  /\bUNION\b.+(SELECT|ALL)\b/i,
  /\bSELECT\b.+\bFROM\b/i,
  /\bINSERT\b.+\bINTO\b/i,
  /\bDROP\b.+\bTABLE\b/i,
  /\bWAITFOR\b.+\bDELAY\b/i,
  /SLEEP\(\d+\)/i
];

const XSS_PATTERNS = [
  /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
  /<img\b[^>]*\bonerror\s*=[^>]*>/gi,
  /<svg\b[^>]*\bonload\s*=[^>]*>/gi,
  /<iframe\b[^>]*>/gi,
  /javascript\s*:/gi,
  /on\w+\s*=\s*["'][^"']*["']/gi,
  /<body\b[^>]*\bonload\s*=[^>]*>/gi,
  /<input\b[^>]*\bautofocus\b[^>]*\bonfocus\s*=[^>]*>/gi
];

function detectSQLi(value) {
  if (typeof value !== 'string') return false;
  return SQLI_PATTERNS.some(pattern => pattern.test(value));
}

function detectXSS(value) {
  if (typeof value !== 'string') return false;
  return XSS_PATTERNS.some(pattern => pattern.test(value));
}

function escapeHTML(str) {
  if (typeof str !== 'string') return str;
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

module.exports = {
  detectSQLi,
  detectXSS,
  escapeHTML
};
