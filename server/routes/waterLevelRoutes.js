import express from "express";
import { storeWaterLevelData } from "../controllers/waterlevelController.js";

const router = express.Router();

// Route to store water level data
router.post("/store", storeWaterLevelData);

export default router;
