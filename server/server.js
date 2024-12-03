import express from "express";
import dotenv from "dotenv";
import bodyParser from "body-parser";
import colors from "colors";
import connectDB from "./config/db.js";
import waterLevelRoutes from "./routes/waterLevelRoutes.js";

// Load environment variables
dotenv.config();

// Connect to MongoDB
connectDB();

const app = express();

// Middleware
app.use(bodyParser.json()); // Parse incoming JSON requests

// Routes
app.use("/api/water-level", waterLevelRoutes);

// Server setup
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`.yellow.bold);
});
