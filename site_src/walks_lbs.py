# Line-by-line walkthroughs for LBS cards. Keys are track/card id.

LBS_WALKS = {
    "lbs/crs": [{
        "title": "入口只接受一种坐标",
        "lang": "Python",
        "intro": "面试时不要只背三个名字。把校验写出来，说明脏点在哪一行被拒绝。",
        "steps": [
            {"code": "def accept_point(body):\n    crs = body[\"crs\"]\n    if crs != \"wgs84\":\n        raise Reject(\"crs\")", "say": "内部基准定成 WGS84。请求没带 crs，或者带了 gcj02、bd09，在这一行就拒绝。转换只允许发生在网关外的适配层，库里面不再出现第二套坐标。"},
            {"code": "    lat = float(body[\"lat\"])\n    lng = float(body[\"lng\"])", "say": "字段必须分开叫 lat 和 lng。用一个长度为 2 的数组时，调用方会把经纬度写反，而类型系统看不出来。"},
            {"code": "    if not -90 <= lat <= 90:\n        raise Reject(\"lat\")\n    lng = (lng + 180) % 360 - 180", "say": "纬度离开 [-90, 90] 一定是脏数据。经度先归一化到 [-180, 180]，这样 181 度和 -179 度是同一个位置，后面的格子计算才不会裂开。"},
            {"code": "    if body.get(\"accuracy\", 0) < 0:\n        raise Reject(\"accuracy\")\n    return {\"lat\": lat, \"lng\": lng, \"crs\": \"wgs84\"}", "say": "精度是半径，负数没有意义。返回值里再次写上 crs，下游不用猜这组数是哪一套。"},
        ],
    }],
    "lbs/validate-fix": [{
        "title": "旧点不能覆盖新点",
        "lang": "Python",
        "intro": "校验通过之后还要决定这一笔写不写进最新位置。",
        "steps": [
            {"code": "def should_update(prev, point):\n    if prev is None:\n        return True", "say": "第一次上报没有旧值，直接写入。"},
            {"code": "    if point[\"ts\"] + 5 * 60_000 < now_ms():\n        raise Reject(\"stale\")", "say": "采集时间比服务端现在早太多，多半是补报的历史点。它不能当最新位置，但可以进轨迹管道。这里选择直接拒绝进最新表。"},
            {"code": "    if point[\"ts\"] <= prev[\"ts\"]:\n        return False", "say": "乱序到达时，更旧的时间戳不能覆盖新点。用事件时间，不用消息到达时间，否则补报会把人移回半小时前。"},
            {"code": "    return True", "say": "通过这三关才更新 Redis 里的最新坐标。"},
        ],
    }],
    "lbs/distance": [{
        "title": "Haversine 每一行在算什么",
        "lang": "Python",
        "intro": "这是精排用的距离。召回阶段不要对全表调用它。",
        "steps": [
            {"code": "import math\n\ndef haversine_m(lat1, lon1, lat2, lon2):", "say": "参数顺序固定成纬度、经度。和 Redis GEO 的经度在前不同，所以函数名旁边要写清楚，调用处不能混。"},
            {"code": "    radius = 6_371_000.0", "say": "把地球当成球体，半径 6371 公里，结果用米。计费里程不要用这个数，它忽略了椭球和高程。"},
            {"code": "    p1 = math.radians(lat1)\n    p2 = math.radians(lat2)\n    dphi = math.radians(lat2 - lat1)\n    dlam = math.radians(lon2 - lon1)", "say": "math.sin 吃的是弧度。漏掉 radians，距离会小一个数量级，而且不会抛异常。"},
            {"code": "    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2", "say": "a 是半正矢。它随距离单调增加，所以只排序、不展示米数时，可以比 a，省掉开方。"},
            {"code": "    return 2 * radius * math.asin(min(1.0, math.sqrt(a)))", "say": "浮点误差会让 a 略大于 1，asin 会报错。先夹到 1。两点重合时 a 是 0，结果是 0 米。"},
        ],
    }],
    "lbs/index": [{
        "title": "先粗筛再精确算",
        "lang": "Python",
        "intro": "索引只负责缩小候选。这一小段把选型讲成代码路径。",
        "steps": [
            {"code": "def nearby(store, lat, lng, radius_m):\n    cells = cover(lat, lng, radius_m)", "say": "cover 按半径选格子。点查询用 Geohash 或 S2，多边形相交才走 R 树。这里返回的是格子 id 列表，不是最终结果。"},
            {"code": "    candidates = []\n    for cell in cells:\n        candidates.extend(store.get(cell))", "say": "每个格子一个 key。查询要扫中心格和邻居，所以这里是循环，不是只取一个前缀。"},
            {"code": "    return [p for p in candidates\n            if haversine_m(lat, lng, p.lat, p.lng) <= radius_m]", "say": "格子是矩形，圆会被多盖住一块。这一行删掉假阳性。漏掉这行，边界外的店会进结果。"},
        ],
    }],
    "lbs/geohash": [{
        "title": "编码：先经度，再纬度",
        "lang": "Python",
        "intro": "标准 Geohash。偶数步切经度。下面只看主循环里容易写反的几行。",
        "steps": [
            {"code": "lat_range = [-90.0, 90.0]\nlon_range = [-180.0, 180.0]\neven = True", "say": "初始区间是整个地球。even 为真时处理经度。很多人从纬度开始，编出来的字符串和标准实现对不上。"},
            {"code": "if even:\n    mid = (lon_range[0] + lon_range[1]) / 2\n    if lon >= mid:\n        value = (value << 1) | 1\n        lon_range[0] = mid\n    else:\n        value <<= 1\n        lon_range[1] = mid", "say": "落在中点右边记 1，并丢掉左半边。落在中点上用 >=，归到高半区。这一行要和测试向量对齐，否则边界点会差一格。"},
            {"code": "even = not even\nif bit == 5:\n    chars.append(BASE32[value])", "say": "经度、纬度交替。每攒满 5 位，查 base32。字符表去掉了 a、i、l、o，不能用普通的 base32 字母表。"},
        ],
    }, {
        "title": "查询要带邻居",
        "lang": "Python",
        "intro": "编码函数本身不解决边界漏召回。",
        "steps": [
            {"code": "cell = encode(lat, lng, precision)\ncells = [cell, *neighbors(cell)]", "say": "neighbors 在二进制格子上走，不是给字符串加一。base32 的下一位并不等于东边那一格。"},
            {"code": "hits = []\nfor item in store.mget(cells):\n    hits.extend(item)", "say": "九个 key 分别取。一个点只存在于其中一格，所以写入时不要复制九份。"},
        ],
    }],
    "lbs/cell-query": [{
        "title": "九宫格完整查询",
        "lang": "Python",
        "intro": "这是附近的人查询路径里最值得白板写的函数。",
        "steps": [
            {"code": "def query_nearby(store, lat, lng, radius_m, limit):\n    precision = precision_for(radius_m)\n    cells = neighbors9(encode(lat, lng, precision))", "say": "precision_for 让格子边长和半径同一量级。半径 3 公里却用 8 位 Geohash，九宫格只有几十米，圆根本盖不住。"},
            {"code": "    seen = {}\n    for cell in cells:\n        for user in store.zrange(cell):\n            seen[user.id] = user", "say": "同一个用户理论上只在一个格子里。用字典是为了防御重复写入。zrange 取出的是 id，不是完整资料。"},
            {"code": "    ranked = []\n    for user in seen.values():\n        if now_ms() - user.ts > 30_000:\n            continue\n        dist = haversine_m(lat, lng, user.lat, user.lng)\n        if dist <= radius_m:\n            ranked.append((dist, user.id))", "say": "先丢掉过期位置。GEO 成员没有单独 TTL，所以时间戳要另存，在这里滤。然后再做精确距离，删掉格子带进来的假阳性。"},
            {"code": "    ranked.sort()\n    return [uid for _, uid in ranked[:limit]]", "say": "按距离升序截断。limit 很小也不能在这一行之前就停，否则你拿到的是格子遍历顺序，不是最近的人。"},
        ],
    }],
    "lbs/s2h3": [{
        "title": "三种 cell 的调用差别",
        "lang": "Python",
        "intro": "选型不要背面积表。看函数签名就知道查询形态。",
        "steps": [
            {"code": "key = geohash_encode(lat, lng, 6)\nstore.get(key)", "say": "Geohash 的 key 是字符串前缀。实现最短，边界要自己算邻居。适合已经用 Redis 的半径查询。"},
            {"code": "cell = s2.cell_id(lat, lng, level=16)\nranges = s2.covering(circle)", "say": "S2 的 id 是整数，覆盖一个圆可以得到若干个 id 区间。区间能做范围扫描，比九宫格更不容易漏在曲线边界上。"},
            {"code": "h3.latlng_to_cell(lat, lng, 9)\nh3.grid_disk(cell, k=1)", "say": "H3 直接给六边形和一圈邻居。热力图、运力覆盖用它，因为每个邻居距离更接近。它不替代点在多边形内。"},
        ],
    }],
    "lbs/poi": [{
        "title": "先空间还是先文本",
        "lang": "Python",
        "intro": "检索顺序由选择性决定。下面是商场内搜咖啡的路径。",
        "steps": [
            {"code": "def search_in_mall(mall_id, text):\n    shop_ids = spatial.shops_in_aoi(mall_id)", "say": "商场是面，店是点。人已经在商场里，空间选择性很高，先拿这个 AOI 里的店。"},
            {"code": "    hits = text_index.filter(shop_ids, text)", "say": "再在这批 id 里做文本过滤。如果反过来先全城搜『咖啡』，候选会有几万，再过滤商场会浪费。"},
            {"code": "    return [hit for hit in hits if hit.open_now]", "say": "营业状态是硬条件，不进排序分。关掉的店不应该靠距离分靠前。"},
        ],
    }],
    "lbs/trajectory": [{
        "title": "不可能的点先丢掉",
        "lang": "Python",
        "intro": "清洗发生在停留点之前。单位是米和秒。",
        "steps": [
            {"code": "def keep(prev, point):\n    if point.accuracy > 100:\n        return False", "say": "精度半径超过 100 米的点，不能参与到店判断。可以留在原始日志里，但不要进匹配。"},
            {"code": "    dist = haversine_m(prev.lat, prev.lng, point.lat, point.lng)\n    seconds = (point.ts - prev.ts) / 1000\n    if seconds <= 0:\n        return False", "say": "时间没有前进，就是乱序或重复点。距离函数用米，所以阈值后面也要用米，不能用经纬度差。"},
            {"code": "    speed = dist / seconds\n    return speed < 80", "say": "80 米每秒大约 288 公里每小时。城市轨迹里超过这个速度，多半是漂移，不是车。阈值按业务改，但要说得出单位。"},
        ],
    }],
    "lbs/stay-cut": [{
        "title": "把轨迹切成停留段",
        "lang": "Python",
        "intro": "输入必须已经按用户和事件时间排好序。",
        "steps": [
            {"code": "def stays(points, speed_max=1.0, hold_ms=180_000):\n    out = []\n    start = points[0]", "say": "速度上限 1 米每秒，持续 3 分钟才算停留。等红灯通常到不了 3 分钟，所以不会被当成到店。"},
            {"code": "    for i in range(1, len(points)):\n        dist = haversine_m(points[i-1].lat, points[i-1].lng,\n                           points[i].lat, points[i].lng)\n        dt = points[i].ts - points[i-1].ts\n        moving = dist / max(dt / 1000, 0.001) > speed_max", "say": "用相邻两点估速度。dt 用事件时间。补报如果用了到达时间，这里会把一段停留切成很多段。"},
            {"code": "        if moving and points[i-1].ts - start.ts >= hold_ms:\n            out.append((start, points[i-1]))\n        if moving:\n            start = points[i]", "say": "一旦开始移动，回头看这一段是否够久。够久才输出。新的起点从当前移动点开始。"},
            {"code": "    return out", "say": "返回的是时间区间。坐标用这段里精度最小的那个点，不要用第一个点，第一个点往往还在漂移。"},
        ],
    }],
    "lbs/mapmatch": [{
        "title": "发射概率和转移概率",
        "lang": "Python",
        "intro": "不用把 Viterbi 整段默写完。把两个概率怎么来的写清楚。",
        "steps": [
            {"code": "def emission(dist_m, sigma=20):\n    return math.exp(-(dist_m ** 2) / (2 * sigma * sigma))", "say": "观测点到候选路段投影点的距离越大，概率越小。sigma 取定位精度，大约 20 米。这是高斯，不是线性衰减。"},
            {"code": "def transition(route_m, observed_m):\n    gap = abs(route_m - observed_m)\n    return math.exp(-gap / 50)", "say": "两个候选路段之间的路网距离，应该和两个 GPS 点的大圆距离差不多。差得越远，越不像同一条路。50 米是尺度，不是必须背的常数。"},
            {"code": "score[t][j] = emission(cands[t][j].dist) * max(\n    score[t-1][i] * transition(cands[t-1][i], cands[t][j])\n    for i in range(len(cands[t-1]))\n)", "say": "这就是 Viterbi 的递推：当前候选的最好分数，来自上一时刻某个候选走过来。在线时只保留一个滑动窗口，不要每次重算全天。"},
        ],
    }],
    "lbs/geofence": [{
        "title": "射线法逐行",
        "lang": "Python",
        "intro": "只对倒排筛完的候选调用。大规模场景不能对所有围栏跑这个循环。",
        "steps": [
            {"code": "def point_in_polygon(x, y, polygon):\n    inside = False\n    j = len(polygon) - 1", "say": "j 起初是最后一条边的另一个端点。边是 (j -> i)，这样不用把首点再复制到末尾。"},
            {"code": "    for i in range(len(polygon)):\n        xi, yi = polygon[i]\n        xj, yj = polygon[j]", "say": "取出当前边的两个端点。坐标必须已经和围栏同一套 crs，否则这一行的比较没有意义。"},
            {"code": "        if (yi > y) != (yj > y):", "say": "两个端点分处射线上下两侧，这条边才可能和向右的水平射线相交。水平边两端的比较相同，被自然跳过，顶点也不会被数两次。"},
            {"code": "            x_cross = (xj - xi) * (y - yi) / (yj - yi) + xi\n            if x < x_cross:\n                inside = not inside", "say": "算出边与射线的交点横坐标。点在交点左边，才算穿过一次。奇数次在内。点正好在边上时结果不稳定，业务上要另外规定边界算内。"},
            {"code": "        j = i\n    return inside", "say": "循环结束时 inside 就是奇偶结果。调用前应该已经用外包矩形滤过，否则百万围栏会在这个双重循环里打满 CPU。"},
        ],
    }],
    "lbs/fence-index": [{
        "title": "发布倒排和在线判定",
        "lang": "Python",
        "intro": "左边是发布，右边的查询只用得到 id 列表。",
        "steps": [
            {"code": "def publish(fence):\n    if fence.self_intersects():\n        raise Reject(\"geometry\")\n    cells = cover_polygon(fence.ring)", "say": "自交多边形的射线法奇偶不再可靠，发布时就拒绝。cover 算出围栏盖住的格子，而不是只取中心一个格子。"},
            {"code": "    for cell in cells:\n        index.add(cell, fence.id, fence.version)", "say": "倒排是 cell 到围栏 id。版本号让查询可以整份切换，避免新位置读到写了一半的几何。"},
            {"code": "def match(point):\n    ids = index.get(point.cell, point.version)\n    return [fid for fid in ids\n            if bbox_hit(fid, point) and point_in_polygon(point, geom(fid))]", "say": "先查所在格子，再用外包矩形，最后才射线法。三步都写上，面试官就知道你不会两两计算。"},
        ],
    }],
    "lbs/eta": [{
        "title": "边权是时间，不是距离",
        "lang": "Python",
        "intro": "Dijkstra 的松弛看懂这四行就够。启发式要和边权同一单位。",
        "steps": [
            {"code": "def heuristic(node, goal):\n    meters = haversine_m(node.lat, node.lng, goal.lat, goal.lng)\n    return meters / 40", "say": "40 米每秒是速度上界。启发式用时间，因为边权也是时间。如果这里返回米，A* 就不再可采纳，可能丢最短路。"},
            {"code": "alt = dist[u] + edge.seconds\nif alt < dist[v]:\n    dist[v] = alt", "say": "松弛用行驶秒数，不用路段长度。拥堵、限速都已经折进 edge.seconds。限行是在扩展邻居之前剪掉这条边，不放进权重里硬减。"},
        ],
    }],
    "lbs/realtime": [{
        "title": "最新位置的一次写入",
        "lang": "Python",
        "intro": "member 只放用户 id。资料和过期时间不要塞进 GEO。",
        "steps": [
            {"code": "def write_location(redis, user_id, lng, lat, ts):\n    cell = encode(lat, lng, 6)\n    pipe = redis.pipeline()", "say": "6 位大约 1 公里。管道把下面几条命令一次发出，避免最新位置和时间戳各走一次网络。"},
            {"code": "    pipe.geoadd(f\"geo:{cell}\", lng, lat, user_id)", "say": "Redis 的参数是经度在前。传反了它仍可能接受，因为两个数都落在合法范围里，但人会偏到错误的城市。"},
            {"code": "    pipe.hset(f\"loc:{user_id}\", mapping={\n        \"lat\": lat, \"lng\": lng, \"ts\": ts, \"cell\": cell, \"crs\": \"wgs84\"\n    })\n    pipe.execute()", "say": "哈希里留原始坐标和时间。GEOPOS 读回的是格子中心，不能当原始 GPS。查询时用 ts 判断 30 秒内是否在线。"},
        ],
    }],
    "lbs/privacy": [{
        "title": "展示前降精度",
        "lang": "Python",
        "intro": "合规不是一段声明。对外返回前把坐标变成网格。",
        "steps": [
            {"code": "def public_view(point, role):\n    if role == \"self\":\n        return point", "say": "用户看自己的导航，可以拿精确点。这是最小必要里的例外，而且只在当次请求。"},
            {"code": "    cell = encode(point.lat, point.lng, 6)\n    center = decode_center(cell)\n    return {\"cell\": cell, \"lat\": round(center.lat, 2),\n            \"lng\": round(center.lng, 2), \"crs\": point.crs}", "say": "给别人看时只到大约 1 公里的格子中心，再把小数砍到两位。日志里同样不要打原始点。crs 仍然保留，避免下游又转换一次。"},
        ],
    }],
}
