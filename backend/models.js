const mongoose = require("mongoose");

const ResultShort = new mongoose.Schema({
  _id: String,
  name: String,
  sgpi: Number,
  cgpi: Number,
});

const ResultLong = new mongoose.Schema({
  _id: String,
  result: Object,
});

ResultShort.index({ name: "text" });

module.exports.ResultLong = mongoose.model(
  "ResultLong",
  ResultLong,
  "RESULT_LONG"
);

module.exports.ResultShort = mongoose.model(
  "ResultShort",
  ResultShort,
  "RESULT_SHORT"
);
