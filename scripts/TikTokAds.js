// Maxworkinghard/module: conservative JSON feed ad filtering.
// Endpoint reference: Jard1n/VPN_Tool, Scripts/TikTok/TikTok_remove_watermark.js.
// Only explicit is_ads flags are removed; other items and permissions stay intact.

(() => {
  try {
    const original = $response.body;
    if (typeof original !== "string" || !original.trim()) return $done({});

    // Keep integer IDs intact across JSON.parse/stringify on JavaScript engines.
    let prefix = "__max_module_integer_";
    while (original.includes(prefix)) prefix += "_";
    const integers = [];
    const protectedBody = original.replace(
      /"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/g,
      token => {
        if (!/^-?\d{16,}$/.test(token)) return token;
        const index = integers.push(token) - 1;
        return JSON.stringify(prefix + index);
      }
    );
    const payload = JSON.parse(protectedBody);
    if (!payload || typeof payload !== "object") return $done({});
    let removed = 0;
    const isAd = item => {
      const flag = item?.is_ads ?? item?.aweme?.is_ads;
      return flag === true || flag === 1 || flag === "true" || flag === "1";
    };
    for (const key of ["aweme_list", "aweme_details", "data"]) {
      if (!Array.isArray(payload[key])) continue;
      payload[key] = payload[key].filter(item => {
        if (!isAd(item)) return true;
        removed += 1;
        return false;
      });
    }
    if (!removed) return $done({});
    let body = JSON.stringify(payload);
    body = body.replace(new RegExp('"' + prefix + '(\\d+)"', "g"), (_, index) => integers[Number(index)]);
    $done({ body });
  } catch (_) {
    // Non-JSON, unsupported or changed responses pass through unchanged.
    $done({});
  }
})();
