-- Seed predictable initial data for demonstrations
-- Primary Demo Accounts:
--   admin: admin123
--   alice: alice123
--   bob:   bob123
--
-- Additional Random Accounts (with cryptographically random passwords):
--   john:  H3FDWr_WgR7p6LVC
--   sarah: iUXPrZ00FLZCfVzI
--   david: KFwzi5tZyl1RsYu0
--   emily: IAcRKMR-D-FKtyyJ
--   alex:  BhGAFzQZOXKF39Ch

INSERT INTO users (username, password_hash, bio) VALUES
('admin', '$argon2id$v=19$m=65536,t=3,p=4$39V+TiFs0CcAJEaa6x0Tbg$kv1LHDouK/FbBcJdVfsuB2xbZJg0d9wXoTPUL7iu6WM', 'System Administrator with elevated privileges.'),
('alice', '$argon2id$v=19$m=65536,t=3,p=4$CybpehaWkjxVGsYwGwEa1g$xNzdGL3u1GLhwYV4a+VL6a5yHc4tf6hGsPoqpxGKOCA', 'Security analyst and technical blogger.'),
('bob', '$argon2id$v=19$m=65536,t=3,p=4$cQLjFtFQ62bS+HmJMipnuQ$CpNRRMprK7JoOuLvZi5M0EaujL9b9arG+zdhULJya8s', 'Full-stack software engineer testing defenses.'),
('john', '$argon2id$v=19$m=65536,t=3,p=4$0pT/EztrPRiXh/f9VLML/g$R/wr98owummRsFoUZ/pV1jW2YlszDrOuGHzRXkhSOVw', 'Passionate about backend architectures and distributed systems.'),
('sarah', '$argon2id$v=19$m=65536,t=3,p=4$OJH1ul9ypMW6ud6wBq8T2w$XWhxMrouf5ps/8qZr9kZBrtLOrulek6iyZ8wQAQqyVE', 'UI/UX enthusiast and frontend developer who loves clean CSS.'),
('david', '$argon2id$v=19$m=65536,t=3,p=4$TQnqbJ6YNIjQYNBpHU4s/A$Nxtiz802bOObd9veNW5/yDvf6BHA8qp6kNsL3510acU', 'DevOps engineer tinkering with CI/CD and container security.'),
('emily', '$argon2id$v=19$m=65536,t=3,p=4$ltJSirz2GmFW13Oj1RuKtQ$7PN9YrE16yYQia6H7+U8Ek2TxwX4MWExvyY/k6y6x20', 'Data scientist fascinated by open-source intelligence and NLP.'),
('alex', '$argon2id$v=19$m=65536,t=3,p=4$nkEcPXz4FIlbZWIxmAwK6A$jHeRCX1TmLeKEJ0wrYDhhOIOxQadOrAuDeYpav4vQhc', 'Computer science student exploring web app security and cryptography.');

INSERT INTO posts (user_id, title, content) VALUES
(1, 'Welcome to the Web Security Lab', 'This minimal blog simulates core application features while illustrating fundamental web security vulnerabilities: SQL Injection (SQLi) and Stored Cross-Site Scripting (XSS). Use the floating security toggle to test both vulnerable and secure modes.'),
(2, 'Understanding SQL Injection in Modern Apps', 'SQL Injection happens when untrusted user input is directly concatenated into SQL statements rather than passed as parameters. Parameterized queries instruct the database engine to treat inputs strictly as literal values, rendering SQL injection impossible.'),
(3, 'Defending Against Cross-Site Scripting (XSS)', 'Cross-site scripting occurs when unvalidated user inputs are rendered directly in the HTML document. Context-aware output encoding ensures that characters such as <, >, and & are translated into HTML entities rather than executed by the browser engine.');

INSERT INTO comments (post_id, user_id, author_name, content) VALUES
(1, 2, 'alice', 'Great platform for testing! Notice how the security switch preserves state across requests.'),
(1, 3, 'bob', 'Looking forward to testing the search and comment endpoints.'),
(2, 4, 'john', 'The difference between string formatting and parameter binding is night and day.'),
(2, 5, 'sarah', 'Clean syntax makes defense much easier to audit in code reviews.'),
(3, 6, 'david', 'Escaping at the template layer is essential for preventing stored script execution.'),
(3, 1, 'admin', 'Make sure to inspect the lab guide at /lab/guide for reproducible demonstration steps.');
