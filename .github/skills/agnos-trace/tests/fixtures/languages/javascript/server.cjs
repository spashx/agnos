// Call-graph fixture, JavaScript (Node.js, CommonJS): a function given to a member of exports.

// RQ-DEM-001
exports.load = function () {
    const fs = require("fs");
    return fs.readFileSync("x");
};
