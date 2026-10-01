// Run only this repository's script in an isolated VM with synthetic responses.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const script = fs.readFileSync(path.join(__dirname, "TikTokAds.js"), "utf8");
function filter(body) {
  const results = [];
  vm.runInNewContext(script, { $response: { body }, $done: value => results.push(value) }, { timeout: 1000 });
  assert.equal(results.length, 1);
  return results[0];
}

const response = '{"aweme_list":[{"is_ads":true},{"is_ads":1},{"is_ads":false,"aweme_id":1234567890123456789,"text":"1234567890123456789"},{"live":true}],"cursor":-1234567890123456789,"ratio":1.2345678901234567}';
const result = filter(response);
assert.equal(JSON.parse(result.body).aweme_list.length, 2);
assert.ok(result.body.includes('"aweme_id":1234567890123456789'));
assert.ok(result.body.includes('"cursor":-1234567890123456789'));
assert.ok(result.body.includes('"text":"1234567890123456789"'));
assert.equal(JSON.parse(result.body).aweme_list[1].live, true);

const follow = JSON.parse(filter('{"data":[{"aweme":{"is_ads":"true"}},{"aweme":{"is_ads":false},"other":"keep"}]}').body);
assert.equal(follow.data.length, 1);
assert.equal(follow.data[0].other, "keep");
for (const input of [undefined, "", "<html>error</html>", "null", '{"aweme_list":[{"live":true}]}', '{"data":{"result":"keep"}}']) {
  assert.equal(Object.keys(filter(input)).length, 0);
}
console.log("TikTokAds: ad filtering, live preservation, integer IDs and pass-through checks passed");
