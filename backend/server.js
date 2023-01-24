const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const bodyParser = require("body-parser");

require("dotenv").config({ path: "../.env" });
require("dotenv").config();
const PORT = process.env.PORT || 3000;

mongoose
  .connect(process.env.MONGO_URL, {
    dbName: process.env.MONGO_DB,
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then((conn) => {
    console.log(`MongoDB Connected: ${conn.connection.host}`);
    const app = express();

    // Configuration
    app.use(cors());
    app.use(bodyParser.urlencoded({ extended: true }));
    app.use(bodyParser.json());

    // Routes
    app.use("/", require("./routes"));

    app.listen(PORT, () => {
      console.log(`Server is running on port: ${PORT}`);
    });

   
  
  })
  .catch((err) => {
    console.log(err);
    process.exit(1);
  });
