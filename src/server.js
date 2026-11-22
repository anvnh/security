const express = require('express');
const cookieParser = require('cookie-parser');
const path = require('path');
const { initDatabase } = require('./db');

const authRoutes = require('./routes/auth');
const productRoutes = require('./routes/products');
const commentRoutes = require('./routes/comments');
const searchRoutes = require('./routes/search');
const logRoutes = require('./routes/logs');

const app = express();
const PORT = process.env.PORT || 3000;

initDatabase();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

app.use((req, res, next) => {
  const isSecure = req.query.securityMode === 'secure' || 
                   req.body?.securityMode === 'secure' || 
                   req.headers['x-security-mode'] === 'secure';

  if (isSecure) {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    res.setHeader('Content-Security-Policy', "default-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com;");
  }
  next();
});

app.use(express.static(path.join(__dirname, '..', 'public')));

app.use('/api/auth', authRoutes);
app.use('/api/products', productRoutes);
app.use('/api/comments', commentRoutes);
app.use('/api/search', searchRoutes);
app.use('/api/logs', logRoutes);

app.use((req, res) => {
  res.status(404).json({ success: false, message: 'Endpoint not found' });
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
    console.log(`Local URL: http://localhost:${PORT}`);
  });
}

module.exports = app;
