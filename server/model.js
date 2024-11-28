// Load environment variables from .env file
require("dotenv").config();

const express = require("express");
const mysql = require("mysql2");
const bodyParser = require("body-parser");
const cors = require('cors'); 

const app = express();

const port = process.env.PORT || 7000;
const ip = process.env.IP || "127.0.0.1"; 

const dbHost = process.env.DB_HOST;
const dbPort = process.env.DB_PORT;
const dbUser = process.env.DB_USER;
const dbPassword = process.env.DB_PASSWORD;
const dbName = process.env.DB_NAME;

// MySQL connection
const db = mysql.createConnection({
  host: dbHost,
  port: dbPort,
  user:dbUser,
  password: dbPassword,
  database: dbName,
});

db.connect((err) => {
  if (err) throw err;
  console.log("Connected to MySQL");
});

app.use(cors());
// Middleware to parse JSON data
app.use(bodyParser.json());

// API endpoint to insert water level data
app.post("/store_data", (req, res) => {
  const { time, water_level } = req.body;

  console.log(time);
console.log(water_level);
  // Insert data into MySQL
  const query = "INSERT INTO water_level_data (time, water_level) VALUES (?, ?)";
  db.query(query, [time, water_level], (err, result) => {
    if (err) {
        console.log(err.message);
      return res.status(500).json({ error: err.message });
    }
    res.status(200).json({ message: "Data stored successfully", result });
  });
});

// API endpoint to retrieve water level data
//http://127.0.0.1:7000/get_data
app.get("/get_data", (req, res) => {
  const query = "SELECT * FROM water_level_data";
  db.query(query, (err, result) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.status(200).json(result);
  });
});

// API endpoint to retrieve water level data in time range
//http://127.0.0.1:7000/get_data_time_range?start_time=2023-01-01T00:00:00&end_time=2025-01-01T23:59:59
app.get("/get_data_time_range", (req, res) => {
  const { start_time, end_time } = req.query;
  const query = "SELECT * FROM water_level_data WHERE time BETWEEN ? AND ?";
  db.query(query, [start_time, end_time], (err, result) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.status(200).json(result);
  });
})

// Start the server
app.listen(port, ip, () => {
  console.log(`Server running on port ${ip}:${port}`);
});

