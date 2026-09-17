import initSqlJs from 'sql.js';

export async function initializeDatabase() {
  const SQL = await initSqlJs({
    locateFile: file => `https://sql.js.org/dist/${file}`
  });
  
  const db = new SQL.Database();
  
  // Создание таблиц
  db.run(`
    CREATE TABLE IF NOT EXISTS tasks (
      id INTEGER PRIMARY KEY,
      title TEXT,
      url TEXT,
      amount REAL
    );
    
    CREATE TABLE IF NOT EXISTS record (
      id INTEGER PRIMARY KEY,
      clicks INTEGER,
      babkaname TEXT
    );
    
    // ... остальные CREATE TABLE
  `);
  
  return db;
}