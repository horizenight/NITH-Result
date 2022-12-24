const express = require("express");
const controller = require("./controller");

const router = express.Router();

router.get("/results", controller.getResults);
router.get("/results/:studentID", controller.getByID);

module.exports = router;
