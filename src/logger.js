const { db } = require('./db');
const fs = require('fs');
const path = require('path');

const logDir = path.join(__dirname, '..', 'logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}
const logFilePath = path.join(logDir, 'security.log');

function logSecurityEvent({ ip, eventType, severity, endpoint, payload, actionTaken }) {
  const timestamp = new Date().toISOString();
  
  try {
    const stmt = db.prepare(`
      INSERT INTO security_logs (ip, event_type, severity, endpoint, payload, action_taken)
      VALUES (?, ?, ?, ?, ?, ?)
    `);
    stmt.run(ip || '127.0.0.1', eventType, severity, endpoint, JSON.stringify(payload) || '', actionTaken);
  } catch (err) {
    console.error('Failed to log to database:', err.message);
  }

  const logLine = `[${timestamp}] [${severity}] [${eventType}] IP: ${ip} | Endpoint: ${endpoint} | Action: ${actionTaken} | Payload: ${JSON.stringify(payload)}\n`;
  try {
    fs.appendFileSync(logFilePath, logLine);
  } catch (err) {
    console.error('Failed to log to file:', err.message);
  }

  const colors = {
    CRITICAL: '\x1b[41m\x1b[37m',
    HIGH: '\x1b[31m',
    MEDIUM: '\x1b[33m',
    LOW: '\x1b[36m',
    RESET: '\x1b[0m'
  };
  const color = colors[severity] || colors.RESET;
  console.log(`${color}[SECURITY ALERT] [${severity}] ${eventType} on ${endpoint} from ${ip} - Action: ${actionTaken}${colors.RESET}`);
}

module.exports = { logSecurityEvent };
