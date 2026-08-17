const url = $request.url;
const method = $request.method;
const notifyTitle = "bilibili-json";
console.log(`b绔檍son-2023.10.22`);
if (!$response.body) {
    // 鏈塽ndefined鐨勬儏鍐?    console.log(`$response.body涓簎ndefined:${url}`);
    $done({});
}
if (method !== "GET") {
    console.log(notifyTitle, "method閿欒:", method);
}
let body = JSON.parse($response.body);


if (!body.data) {
    console.log(url);
    console.log(`body:${$response.body}`);
    console.log(notifyTitle, url, "data瀛楁閿欒");
} else {
    if (url.includes("x/v2/splash")) {
        console.log('寮€灞忛〉' + (url.includes("splash/show") ? 'show' : 'list'));
        if (!body.data.show) {
            // 鏈夋椂鍊欒繑鍥炵殑鏁版嵁娌℃湁show瀛楁
            console.log('鏁版嵁鏃爏how瀛楁');
        } else {
            delete body.data.show;
            console.log('鎴愬姛');
        }
    } else if (url.includes("resource/show/tab/v2")) {
        console.log('tab淇敼');
        // 椤堕儴鍙充笂瑙?        if (!body.data.top) {
            console.log(`body:${$response.body}`);
            console.log(notifyTitle, 'tab', "top瀛楁閿欒");
        } else {
            body.data.top = body.data.top.filter(item => {
                if (item.name === '娓告垙涓績') {
                    console.log('鍘婚櫎鍙充笂瑙掓父鎴忎腑蹇?);
                    return false;
                }
                return true;
            });
            fixPos(body.data.top);
        }
        // 搴曢儴tab鏍?        if (!body.data.bottom) {
            console.log(`body:${$response.body}`);
            console.log(notifyTitle, 'tab', "bottom瀛楁閿欒");
        } else {
            body.data.bottom = body.data.bottom.filter(item => {
                if (item.name === '鍙戝竷') {
                    console.log('鍘婚櫎鍙戝竷');
                    return false;
                } else if (item.name === '浼氬憳璐? || item.tab_id === '浼氬憳璐瑽ottom') {
                    console.log('鍘婚櫎浼氬憳璐?);
                    return false;
                }
                return true;
            });
            fixPos(body.data.bottom);
        }
    } else if (url.includes("x/v2/feed/index")) {
        console.log('鎺ㄨ崘椤?);
        if (!body.data.items?.length) {
            console.log(`body:${$response.body}`);
            console.log(notifyTitle, '鎺ㄨ崘椤?, "items瀛楁閿欒");
        } else {
            body.data.items = body.data.items.filter(i => {
                const {card_type: cardType, card_goto: cardGoto} = i;
                if (cardType && cardGoto) {
                    if (cardType === 'banner_v8' && cardGoto === 'banner') {
                        if (!i.banner_item) {
                            console.log(`body:${$response.body}`);
                            console.log(notifyTitle, '鎺ㄨ崘椤?, "banner_item閿欒");
                        } else {
                            for (const v of i.banner_item) {
                                if (!v.type) {
                                    console.log(`body:${$response.body}`);
                                    console.log(notifyTitle, '鎺ㄨ崘椤?, "type閿欒");
                                } else {
                                    if (v.type === 'ad') {
                                        console.log('banner骞垮憡');
                                        return false;
                                    }
                                }
                            }
                        }
                    } else if (cardType === 'cm_v2' && ['ad_web_s', 'ad_av', 'ad_web_gif', 'ad_player', 'ad_inline_3d', 'ad_inline_eggs'].includes(cardGoto)) {
                        // ad_player澶ц棰戝箍鍛?ad_web_gif澶if骞垮憡 ad_web_s鏅€氬皬骞垮憡 ad_av鍒涗綔鎺ㄥ箍骞垮憡 ad_inline_3d  涓婃柟澶х殑瑙嗛3d骞垮憡 ad_inline_eggs 涓婃柟澶х殑瑙嗛骞垮憡
                        console.log(`${cardGoto}骞垮憡鍘婚櫎)`);
                        return false;
                    } else if (cardType === 'small_cover_v10' && cardGoto === 'game') {
                        console.log('娓告垙骞垮憡鍘婚櫎');
                        return false;
                    } else if (cardType === 'cm_double_v9' && cardGoto === 'ad_inline_av') {
                        console.log('鍒涗綔鎺ㄥ箍-澶ц棰戝箍鍛?);
                        return false;
                    }
                } else {
                    console.log(`body:${$response.body}`);
                    console.log(notifyTitle, '鎺ㄨ崘椤?, "鏃燾ard_type/card_goto");
                }
                return true;
            });
        }
    } else {
        console.log(notifyTitle, "璺緞鍖归厤閿欒:", url);
    }
}

body = JSON.stringify(body);
$done({
    body
});


function fixPos(arr) {
    for (let i = 0; i < arr.length; i++) {
        // 淇pos
        arr[i].pos = i + 1;
    }
}

