var chai = require('chai');
var expect = chai.expect;
let core = require("./static/scripts/core");

describe('Core', function()
{
  let validIds = ["ersf", "zzzz", "urie   ", "  iqiw   "];
  let invalidIds = ["", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "#@%^%#$@#$@#", "@domain.com", "com", "ail.", "d2oa", "1238", "aabbccdd", 0];

  describe('IsValidGameID returns true for valid ids', function() {
    validIds.forEach(function(id) {
      it(id + "", function()
      {
        expect(core.IsValidGameID(id)).to.equal(true);
      });
    });
  });

  describe('IsValidGameID returns false for invalid ids', function() {
    invalidIds.forEach(function(id) {
      it(id + "", function()
      {
        expect(core.IsValidGameID(id)).to.equal(false);
      });
    });
  });

  let queries = [["?id=edqs", "id", "edqs" ], ["?id=edqs", "name", undefined], ["?fb=jqwjqw90h2&name=2312f&seven=7", "name", "2312f"], ["?yeb=BS8%201BU", "yeb", "BS8 1BU"]];

  describe('GetQueryParam gets the correct data', function() {
    queries.forEach(function(query) {
      it(query[0] + " => " + query[2], function()
      {
        document = {};
        document.location = {};
        document.location.search = query[0];
        expect(core.GetQueryParam(query[1])).to.equal(query[2]);
      });
    });
  });
});
