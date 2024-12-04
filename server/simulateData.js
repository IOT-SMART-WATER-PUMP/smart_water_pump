const axios = require("axios");
const moment = require("moment-timezone"); // Import moment-timezone for handling time zones

// Tank configuration
const TANK_CAPACITY = 1000; // in liters
const REFILL_THRESHOLD = 100; // Refill when below this level
const DAILY_CONSUMPTION = 2000; // liters/day
const BASE_CONSUMPTION_RATE = DAILY_CONSUMPTION / 86400; // Mean liters per second
const CONSUMPTION_RATE_SD = BASE_CONSUMPTION_RATE * 0.1; // 10% of the mean as standard deviation
const API_URL = "http://127.0.0.1:7000/store_data";

// Peak times for increased consumption
const PEAK_TIMES = [
  moment.tz("08:00:00", "HH:mm:ss", "Asia/Kolkata"),
  moment.tz("12:00:00", "HH:mm:ss", "Asia/Kolkata"),
  moment.tz("18:00:00", "HH:mm:ss", "Asia/Kolkata"),
  moment.tz("21:00:00", "HH:mm:ss", "Asia/Kolkata"),
];

// Refill rate when below threshold
const REFILL_RATE = 0.35; // Liters per second

function generateNormal(mean, stdDev) {
  let u1 = Math.random();
  let u2 = Math.random();
  let z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
  return z0 * stdDev + mean;
}

// Initialize water level
let waterLevel = TANK_CAPACITY;

// Boolean flag to track whether the pump is on (refilling)
let pumpOn = false;

// Calculate the time-dependent multiplier based on proximity to peak times
function getTimeMultiplier(currentTime) {
  const currentSeconds = currentTime.diff(moment("00:00:00", "HH:mm:ss"), "seconds");

  // Gaussian bell curve parameters
  const PEAK_EFFECT_RADIUS = 600; // 10 minutes on either side (600 seconds)
  const PEAK_INTENSITY = 4; // Multiplier at the peak time

  let multiplier = 1; // Base multiplier

  PEAK_TIMES.forEach((peakTime) => {
    const peakSeconds = peakTime.diff(moment("00:00:00", "HH:mm:ss"), "seconds");
    const distance = Math.abs(currentSeconds - peakSeconds);

    if (distance <= PEAK_EFFECT_RADIUS) {
      // Calculate the Gaussian multiplier
      const normalizedDistance = distance / PEAK_EFFECT_RADIUS;
      const gaussianEffect = PEAK_INTENSITY * Math.exp(-Math.pow(normalizedDistance, 2));
      multiplier += gaussianEffect;
    }
  });

  return multiplier;
}

// Generate a random consumption rate adjusted by time multiplier
function getRandomConsumptionRate(currentTime) {
  const baseRate = generateNormal(BASE_CONSUMPTION_RATE, CONSUMPTION_RATE_SD);
  const timeMultiplier = getTimeMultiplier(currentTime);

  // Adjust rate to have peak consumption at noon, lower at 8 AM, 6 PM, 9 PM
  const timeOfDay = currentTime.format("HH:mm:ss");
  let peakAdjustedRate = baseRate * timeMultiplier;

  if (timeOfDay === "12:00:00") {
    peakAdjustedRate *= 2; // Max consumption at 12 PM
  } else if (["08:00:00", "18:00:00", "21:00:00"].includes(timeOfDay)) {
    peakAdjustedRate *= 0.5; // Min consumption at 8 AM, 6 PM, and 9 PM
  }

  return Math.max(0, peakAdjustedRate); // Ensure non-negative rates
}

function formatTime(momentObj) {
  return momentObj.tz("Asia/Kolkata").toISOString(); // Convert to IST before formatting
}

// Simulate one second of water level
function simulateSecond(currentTime) {
  if (waterLevel < REFILL_THRESHOLD && !pumpOn) {
    // Start refilling if water level is below threshold and pump is off
    pumpOn = true;
    console.log("Pump is ON, refilling...");
  }

  if (pumpOn) {
    // Refill the tank at a fixed rate when water level is below the threshold
    waterLevel += REFILL_RATE; // Refilling at 0.35 liters per second
    if (waterLevel >= TANK_CAPACITY) {
      waterLevel = TANK_CAPACITY; // Stop refilling when water reaches threshold
      pumpOn = false; // Turn the pump off when the threshold is reached
      console.log("Pump is OFF, threshold reached.");
    }
  } else {
    // If the pump is off, reduce the water level using a time-dependent consumption rate
    waterLevel -= getRandomConsumptionRate(currentTime);
    if (waterLevel < 0) waterLevel = 0; // Prevent negative water level
  }

  return {
    time: formatTime(currentTime),
    water_level: parseFloat(waterLevel.toFixed(2)),
  };
}

// Post data to the backend
async function postData(data) {
  try {
    const response = await axios.post(API_URL, data);
    console.log(`Data stored: ${JSON.stringify(data)} | Response: ${response.status}`);
  } catch (error) {
    console.error(`Error storing data: ${error.message}`);
  }
}

// Simulate water level data for one day (per second)
async function simulateDay() {
    const startOfDay = moment("00:00:00", "HH:mm:ss").tz("Asia/Kolkata", true); // IST Start Time
    const endOfDay = moment("23:59:59", "HH:mm:ss").tz("Asia/Kolkata", true); // IST End Time

  let currentTime = startOfDay;

  while (currentTime.isSameOrBefore(endOfDay)) {
    const simulatedData = simulateSecond(currentTime);
    await postData(simulatedData);
    currentTime.add(1, "second"); // Move to the next second
  }
}

// Start simulation
simulateDay();
