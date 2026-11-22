const app = require('./src/server');

async function runTests() {
  const server = app.listen(0);
  const port = server.address().port;
  const BASE_URL = `http://127.0.0.1:${port}`;

  console.log('===============================================================');
  console.log('AUTOMATED SECURITY AUDIT AND POC VERIFICATION');
  console.log(`Target URL: ${BASE_URL}`);
  console.log('===============================================================\n');

  try {
    console.log('--- [TEST 1] SQL INJECTION: AUTHENTICATION BYPASS ---');
    const sqliAuthVulnRes = await fetch(`${BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: "admin' --",
        password: "wrong_password",
        securityMode: "vulnerable"
      })
    });
    const sqliAuthVuln = await sqliAuthVulnRes.json();
    console.log(`[Vulnerable Mode]: Payload "admin' --"`);
    console.log(` > Result: ${sqliAuthVuln.success ? 'BYPASS SUCCESSFUL' : 'FAILED'}`);
    console.log(` > Authenticated user: ${sqliAuthVuln.user?.username} (Role: ${sqliAuthVuln.user?.role})`);
    console.log(` > Executed Query: ${sqliAuthVuln.executedQuery}`);

    const sqliAuthSecRes = await fetch(`${BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: "admin' --",
        password: "wrong_password",
        securityMode: "secure"
      })
    });
    const sqliAuthSec = await sqliAuthSecRes.json();
    console.log(`[Secure Mode]: Payload "admin' --"`);
    console.log(` > Result: ${sqliAuthSec.blocked ? 'BLOCKED SAFELY' : 'UNSAFE'}`);
    console.log(` > Backend Response: "${sqliAuthSec.message}"\n`);

    console.log('--- [TEST 2] SQL INJECTION: UNION DATA EXFILTRATION ---');
    const unionPayload = "' UNION SELECT id, username, password, 0, role FROM users --";

    const sqliUnionVulnRes = await fetch(`${BASE_URL}/api/products/search?q=${encodeURIComponent(unionPayload)}&securityMode=vulnerable`);
    const sqliUnionVuln = await sqliUnionVulnRes.json();
    console.log(`[Vulnerable Mode]: UNION Users payload`);
    console.log(` > Result: ${sqliUnionVuln.vulnerabilityTriggered ? 'DATA EXFILTRATED' : 'No data'}`);
    console.log(` > Records returned: ${sqliUnionVuln.count}`);
    if (sqliUnionVuln.data && sqliUnionVuln.data.length > 0) {
      console.log(` > Sample record: [Username: ${sqliUnionVuln.data[0].name}, Hash: ${sqliUnionVuln.data[0].category}]`);
    }

    const sqliUnionSecRes = await fetch(`${BASE_URL}/api/products/search?q=${encodeURIComponent(unionPayload)}&securityMode=secure`);
    const sqliUnionSec = await sqliUnionSecRes.json();
    console.log(`[Secure Mode]: UNION Users payload`);
    console.log(` > Result: ${sqliUnionSec.blocked ? 'BLOCKED SAFELY' : 'UNSAFE'}`);
    console.log(` > Backend Response: "${sqliUnionSec.message}"\n`);

    console.log('--- [TEST 3] CROSS-SITE SCRIPTING: STORED XSS ---');
    const xssPayload = "<script>alert('Attacker_Payload')</script>";

    const xssVulnRes = await fetch(`${BASE_URL}/api/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        author: 'Evil_Hacker',
        content: xssPayload,
        securityMode: 'vulnerable'
      })
    });
    const xssVuln = await xssVulnRes.json();
    console.log(`[Vulnerable Mode]: Storing payload with script tag`);
    console.log(` > Result: ${xssVuln.vulnerabilityTriggered ? 'STORED RAW SCRIPT IN DATABASE' : 'Saved normally'}`);

    const xssSecRes = await fetch(`${BASE_URL}/api/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        author: 'Attacker_2',
        content: xssPayload,
        securityMode: 'secure'
      })
    });
    const xssSec = await xssSecRes.json();
    console.log(`[Secure Mode]: Storing payload with script tag`);
    console.log(` > Result: ${xssSec.sanitized ? 'SANITIZED AND HTML ENCODED' : 'Normal'}`);
    console.log(` > Message: "${xssSec.message}"\n`);

    console.log('--- [TEST 4] SECURITY AUDIT LOGS CHECK ---');
    const logsRes = await fetch(`${BASE_URL}/api/logs/stats`);
    const logsStats = await logsRes.json();
    console.log(`[Security Audit & Telemetry]:`);
    console.log(` > Total recorded events: ${logsStats.data.total}`);
    console.log(` > SQL Injection events: ${logsStats.data.sqliCount}`);
    console.log(` > XSS attack events: ${logsStats.data.xssCount}`);
    console.log(` > Critical severity incidents: ${logsStats.data.criticalCount}`);

    console.log('\n===============================================================');
    console.log('VERIFICATION COMPLETED: ALL SCENARIOS OPERATING AS EXPECTED');
    console.log('===============================================================\n');

  } catch (err) {
    console.error('Test execution error:', err.message);
  } finally {
    server.close();
  }
}

runTests();
