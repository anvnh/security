const Database = require('better-sqlite3');
const path = require('path');
const bcrypt = require('bcryptjs');

const dbPath = path.join(__dirname, '..', 'security_demo.db');
const db = new Database(dbPath);

db.pragma('foreign_keys = ON');

function initDatabase() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'user',
      full_name TEXT NOT NULL
    );
  `);

  db.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      category TEXT NOT NULL,
      price REAL NOT NULL,
      description TEXT NOT NULL
    );
  `);

  db.exec(`
    CREATE TABLE IF NOT EXISTS comments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      author TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
  `);

  db.exec(`
    CREATE TABLE IF NOT EXISTS security_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      ip TEXT NOT NULL,
      event_type TEXT NOT NULL,
      severity TEXT NOT NULL,
      endpoint TEXT NOT NULL,
      payload TEXT,
      action_taken TEXT NOT NULL
    );
  `);

  const userCount = db.prepare('SELECT COUNT(*) as count FROM users').get().count;
  if (userCount === 0) {
    const salt = bcrypt.genSaltSync(10);
    const hashAdmin = bcrypt.hashSync('Admin@123456', salt);
    const hashUser = bcrypt.hashSync('user123', salt);

    const insertUser = db.prepare(`
      INSERT INTO users (username, password, role, full_name)
      VALUES (?, ?, ?, ?)
    `);

    insertUser.run('admin', hashAdmin, 'admin', 'System Administrator');
    insertUser.run('victim_user', hashUser, 'user', 'John Doe');
    insertUser.run('alice', hashUser, 'user', 'Alice Wonderland');
  }

  const prodCount = db.prepare('SELECT COUNT(*) as count FROM products').get().count;
  if (prodCount === 0) {
    const insertProd = db.prepare(`
      INSERT INTO products (name, category, price, description)
      VALUES (?, ?, ?, ?)
    `);

    insertProd.run('Dell XPS 15 Laptop', 'Electronics', 1500, 'High performance developer laptop');
    insertProd.run('MacBook Pro 16', 'Electronics', 2400, 'Apple silicon workstation');
    insertProd.run('Keychron Mechanical Keyboard', 'Accessories', 120, 'Wireless mechanical keyboard with Brown switches');
    insertProd.run('Logitech MX Master 3S', 'Accessories', 99, 'Ergonomic precision mouse');
    insertProd.run('LG 27-inch 4K Monitor', 'Monitors', 450, 'Ultra HD IPS display');
  }

  const commentCount = db.prepare('SELECT COUNT(*) as count FROM comments').get().count;
  if (commentCount === 0) {
    const insertComment = db.prepare(`
      INSERT INTO comments (author, content)
      VALUES (?, ?)
    `);
    insertComment.run('Alice', 'The Dell XPS 15 performs exceptionally well.');
    insertComment.run('John Doe', 'Great keyboard, very comfortable for typing.');
  }

  console.log('Database initialized and seeded successfully.');
}

module.exports = { db, initDatabase };
