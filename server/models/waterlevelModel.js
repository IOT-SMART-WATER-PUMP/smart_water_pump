import mongoose from "mongoose";
const waterLevelSchema = new mongoose.Schema({
    time: {
      type: String, // Storing timestamp as a string
      required: true,
    },
    water_level: {
      type: Number, // Storing the water level as a number
      required: true,
    },
  });
  
const WaterLevel = mongoose.model("WaterLevel", waterLevelSchema);
export default WaterLevel;