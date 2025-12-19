require("dotenv").config();
const express = require("express");
const axios = require("axios");
const fs = require("fs").promises;
const path = require("path");

const app = express();
app.use(express.json());

// 🔐 Move these to .env in real deployment
const API_TOKEN = "1083b4b4-5e10-4bd6-afd8-f465d5bc3265";
const API_SECRET = "9e64a006584c1818189ab4cc32a376f7";

// 📁 Correct file path
const DATA_DIR = path.join(__dirname, "data");
const DATA_FILE = path.join(DATA_DIR, "CAR_UNIQUE_DATA.json");

// -----------------------------
// 1️⃣ Get JWT Token
// -----------------------------
async function getJwtToken() {
  const res = await axios.post(
    "https://carapi.app/api/auth/login",
    {
      api_token: API_TOKEN,
      api_secret: API_SECRET,
    },
    {
      headers: {
        Accept: "text/plain",
        "Content-Type": "application/json",
      },
    }
  );

  return res.data;
}

// -----------------------------
// 2️⃣ Fetch ALL pages + DEDUP BY MODEL
// -----------------------------
async function fetchAndDeduplicateInventory() {
  const jwt = await getJwtToken();

  let page = 1;
  let hasNext = true;

  // 🔥 key = model (case-insensitive)
  const uniqueModelMap = new Map();

  console.log("🚗 Starting CarAPI full sync (dedup by MODEL)...");

  while (hasNext) {
    console.log(`📄 Fetching page ${page}`);

    const resp = await axios.get("https://carapi.app/api/trims/v2", {
      params: { page },
      headers: { Authorization: `Bearer ${jwt}` },
    });

    const { data, collection } = resp.data;

    for (const car of data) {
      if (!car.model) continue;

      const modelKey = car.model.toLowerCase().trim();

      // ✅ Keep FIRST occurrence of each model
      if (!uniqueModelMap.has(modelKey)) {
        uniqueModelMap.set(modelKey, car); // 🔥 store FULL object
      }
    }

    if (!collection.next) {
      hasNext = false;
    } else {
      page++;
      await new Promise((r) => setTimeout(r, 150)); // rate-limit safety
    }
  }

  const uniqueCars = Array.from(uniqueModelMap.values());

  await fs.mkdir(DATA_DIR, { recursive: true });
  await fs.writeFile(DATA_FILE, JSON.stringify(uniqueCars, null, 2));

  console.log(`✅ Saved ${uniqueCars.length} UNIQUE MODELS`);
  return uniqueCars.length;
}

// -----------------------------
// 3️⃣ Refresh inventory (RUN ONCE)
// -----------------------------
app.post("/refresh-inventory", async (req, res) => {
  try {
    const total = await fetchAndDeduplicateInventory();
    res.json({
      status: "success",
      unique_models: total,
      file: "data/CAR_UNIQUE_DATA.json",
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({
      status: "error",
      message: err.message,
    });
  }
});

// -----------------------------
// 4️⃣ Return UNIQUE inventory (Python agents use this)
// -----------------------------
app.get("/all-cars", async (req, res) => {
  try {
    const fileData = await fs.readFile(DATA_FILE, "utf-8");
    const vehicles = JSON.parse(fileData);

    res.json({
      status: "success",
      total_unique_models: vehicles.length,
      data: vehicles,
    });
  } catch (err) {
    res.status(500).json({
      status: "error",
      message: "Run /refresh-inventory first.",
    });
  }
});

// -----------------------------
app.listen(3000, () => {
  console.log("🚀 Server running at http://localhost:3000");
});
