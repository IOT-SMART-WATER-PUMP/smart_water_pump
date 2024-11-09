const express = require('express');
const mysql = require('mysql2');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

// MySQL connection
const db = mysql.createConnection({
  host: '127.0.0.1',
  port: 3308,
  user: 'root', // your MySQL username
  password: '', // your MySQL password
  database: 'iot_project_water_pump' // your database name
});

db.connect(err => {
  if (err) throw err;
  console.log('Connected to MySQL');
});

// Middleware to parse JSON data
app.use(bodyParser.json());

// API endpoint to receive water level data
app.post('/data', (req, res) => {
  const { time, water_level } = req.body;

  // Convert timestamp to MySQL datetime format
  const date = new Date(time);
  console.log(date)
  if (isNaN(date.getTime())) {
    return res.status(400).json({ error: 'Invalid timestamp format' });
}
  const mysqlDate = date.toISOString().slice(0, 19).replace('T', ' '); // MySQL datetime format
  // Insert data into MySQL
  const query = 'INSERT INTO water_level_data (time, water_level) VALUES (?, ?)';
  db.query(query, [mysqlDate, water_level], (err, result) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.status(200).json({ message: 'Data stored successfully', result });
  });
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
