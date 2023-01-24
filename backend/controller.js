const { json } = require("body-parser");

const ResultLong = require("./models").ResultLong;
const ResultShort = require("./models").ResultShort;

module.exports.getResults = async function (req, res) {
  const { page = 1, limit = 25, sort = "desc", sortf = "cgpi", search=null } = req.query;
  let searchParam = {};
  if (search) {
    searchParam = {
      $or: [
        { name: { $regex: search, $options: "i" } },
        { _id: { $regex: search, $options: "i" } },
      ],
    };
  }
  let data = await ResultShort.find(searchParam)
    .sort({ [sortf == "cgpi" ? "cgpi" : "sgpi"]: sort == "desc" ? -1 : 1 })
    .limit(limit * 1)
    .skip((page - 1) * limit)
    .exec();

  if (data) return res.status(200).json(data);
  return res.status(404).json({
    message: "Requested data not found",
  });
};


module.exports.getByID = async function (req, res) {

 
  // console.log( req.params.studentID)
  let data = await ResultLong.findOne(
    {
      "_id" :  req.params.studentID
    }
  )

  console.log(data["results"]);
  if (data) return res.status(200).json(data);
  return res.status(404).json({
    message: "Requested data not found",
  });
};
