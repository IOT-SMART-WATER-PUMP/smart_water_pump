import asyncHandler from "express-async-handler";
import WaterLevel from "../models/waterLevelModel.js";
// @desc    Store water level data
// @route   POST /api/water-level/store
// @access  Public

const storeWaterLevelData = asyncHandler(async (req, res) => {
  const { time, water_level } = req.body;

  if (!time || water_level == null) {
    return res.status(400).json({ message: "Invalid data format" });
  }

  try {
    const newRecord = new WaterLevel({ time, water_level });
    await newRecord.save();
    res.status(200).json({ message: "Data successfully stored" });
  } catch (error) {
    console.error(`Database Error: ${error.message}`.red.bold);
    res.status(500).json({ message: "Server error" });
  }
});

export { storeWaterLevelData };
