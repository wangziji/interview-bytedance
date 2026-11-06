MORE_WALKS = {}

def _add(key, title, lang, intro, steps):
    MORE_WALKS[key] = [{"title": title, "lang": lang, "intro": intro, "steps": steps}]

_add("go/leak", "每个循环都能退出", "Go", "看发送和接收是不是都有取消。", [
    {"code": "func consume(ctx context.Context, jobs <-chan Point) {\n    for {\n        select {\n        case <-ctx.Done():\n            return\n        case p, ok := <-jobs:\n            if !ok {\n                return\n            }\n            handle(p)\n        }\n    }\n}", "say": "ctx 取消或 channel 关闭都会 return。少了 Done 这一支，发版之后这些 goroutine 停在接收上，数量不回落。"},
    {"code": "go consume(ctx, jobs) // 调用方必须能 cancel", "say": "谁启动谁持有 cancel。库函数内部偷偷 go 出去，调用方无法停，这就是泄漏的入口。"},
])
_add("go/shutdown", "先摘流量再关连接", "Go", "顺序反了，请求会打到正在关闭的依赖。", [
    {"code": "signal.Notify(sig, syscall.SIGTERM)\n<-sig\nregistry.Deregister()", "say": "先从服务发现摘掉，新请求不再进来。这时已经在处理的请求还要继续。"},
    {"code": "ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)\ndefer cancel()\nserver.Shutdown(ctx)", "say": "Shutdown 等已有请求结束，但最多 10 秒。超时后记录没写完的序号，而不是 os.Exit 把缓冲直接丢掉。"},
    {"code": "redisClient.Close()\ndb.Close()", "say": "连接放在请求都结束后再关。先关连接，正在写位置的请求会得到一串使用已关闭连接的错误。"},
])
_add("go/pool", "有界队列和固定 worker", "Go", "队列长度就是能堆积的上报数。", [
    {"code": "jobs := make(chan Point, 1024)\nfor i := 0; i < runtime.GOMAXPROCS(0); i++ {\n    go consume(ctx, jobs)\n}", "say": "worker 跟核数走。缓冲 1024 是上限。再多的点不会无界堆在内存里。"},
    {"code": "select {\ncase jobs <- point:\ncase <-ctx.Done():\n    return ctx.Err()\ndefault:\n    keepLatest(point)\n}", "say": "default 表示队列满了不等待。keepLatest 只保留这个用户的最后一点。如果没有 default，网关线程会堵在发送上。"},
])
_add("go/timeout", "用 context 而不是循环里的 After", "Go", "超时和空结果是两件事。", [
    {"code": "ctx, cancel := context.WithTimeout(ctx, 50*time.Millisecond)\ndefer cancel()\nids, err := search(ctx, lat, lng)", "say": "这一跳最多 50 毫秒。defer cancel 把定时器放掉。search 内部把 ctx 传给 Redis。"},
    {"code": "if errors.Is(err, context.DeadlineExceeded) {\n    return nil, err\n}", "say": "超时返回错误。如果这里返回空列表，调用方会显示附近没有店。"},
])
_add("go/defer", "循环里不要把解锁堆到函数末尾", "Go", "后进先出，而且会拖到函数返回。", [
    {"code": "for _, id := range ids {\n    func() {\n        mu.Lock()\n        defer mu.Unlock()\n        latest[id] = points[id]\n    }()\n}", "say": "匿名函数结束就解锁。如果 defer 写在外层函数，所有 id 的锁会等到整个请求结束才放，别的请求全部堵住。"},
])
_add("go/errors", "包装之后还能判断原因", "Go", "超时和坐标非法要能分开。", [
    {"code": "var ErrBadCoordinate = errors.New(\"bad coordinate\")\n\nif lat > 90 {\n    return fmt.Errorf(\"user %s: %w\", id, ErrBadCoordinate)\n}", "say": "%w 把哨兵错误留在链上。调用方用 errors.Is 判断是坐标非法，而不是看字符串里有没有 bad。"},
    {"code": "if errors.Is(err, context.DeadlineExceeded) {\n    metrics.Inc(\"timeout\")\n}", "say": "超时走指标和重试判断。坐标非法走拒绝，不要重试。两种错误如果只剩一句 Error()，分支就没了。"},
])
_add("go/mutex", "临界区只改表", "Go", "锁保护的是 latest 这张表。", [
    {"code": "mu.Lock()\nlatest[id] = point\nmu.Unlock()", "say": "只做赋值。不要在锁里算 Haversine 或访问 Redis。写多的位置表用互斥锁，不用读写锁。"},
    {"code": "jobs <- point // 把所有权交出去，之后不要再改 point", "say": "channel 传递的是所有权。送进去之后，发送方不能再改这个点，接收方也不能把它放进另一个共享 map 让第三人改。"},
])
_add("go/http-client", "连接池和请求超时分开", "Go", "默认客户端没有请求超时。", [
    {"code": "client := &http.Client{\n    Timeout: 200 * time.Millisecond,\n    Transport: &http.Transport{\n        MaxIdleConnsPerHost: 32,\n    },\n}", "say": "Client.Timeout 是整次请求的上限，包含连接和读 body。每个主机的空闲连接限制住，避免把下游打出过多连接。"},
    {"code": "req = req.WithContext(ctx)\nresp, err := client.Do(req)", "say": "这一跳再用更短的 ctx。不要用 http.Get。写位置如果重试，请求里要带序号，服务端才能丢掉重复包。"},
])

_add("mysql/explain", "先看 type 和 rows", "SQL", "一条 POI 查询的计划就这几个字段。", [
    {"code": "explain select id from poi\nwhere city_id = 110100 and category = 'cafe'\\G", "say": "type 希望是 ref 或 range。ALL 是全表扫。key 是真正用上的索引。possible_keys 里有名字不代表用了。"},
    {"code": "rows: 240\nExtra: Using index", "say": "rows 是优化器估计要看的行。Using index 表示不用回表。如果 Extra 出现 Using filesort，排序没有被索引吃掉。"},
])
_add("mysql/covering", "列表只拿索引里的列", "SQL", "星号会把覆盖打掉。", [
    {"code": "alter table poi add index idx_city_cat (city_id, category, id);", "say": "查询要的 city_id、category、id 都在这棵索引里。id 即使是主键，放进来也可以避免回表拿整行。"},
    {"code": "select id from poi where city_id = ? and category = ?;", "say": "只选 id。如果写成 select *，还是要按主键回聚簇索引把地址大字段读出来。"},
])
_add("mysql/gap-demo", "画出被锁的间隙", "SQL", "范围条件锁的不是已有的那几行而已。", [
    {"code": "select * from poi\nwhere city_id = 1 and id between 10 and 20\nfor update;", "say": "可重复读下，这会锁住 (10,20) 这段索引间隙。别人插入 id 15 会等待。只说锁住了 10 和 20 这两行是不完整的。"},
    {"code": "update poi set status = 0 where name = 'x';", "say": "name 没有索引时，扫描到的记录都可能被锁。所以更新条件必须走得上索引，否则锁范围会大到像表锁。"},
])
_add("mysql/deadlock", "按同一个主键顺序更新", "SQL", "相反顺序就会成环。", [
    {"code": "-- 事务 A\nupdate account set bal = bal - 1 where id = 1;\nupdate account set bal = bal - 1 where id = 2;\n-- 事务 B 先 2 后 1", "say": "A 持有 1 等 2，B 持有 2 等 1。InnoDB 会回滚其中一个。两个事务都改成先小 id 后大 id，环就没了。"},
    {"code": "retry at most 2 times with jitter", "say": "死锁可以重试，但要有次数和抖动。无限制重试会在热点行上放大冲突。"},
])
_add("mysql/rc-rr", "按事务里有几次读来选", "SQL", "默认值不是答案。", [
    {"code": "set transaction isolation level read committed;\nselect status from poi where id = 7;", "say": "展示读用提交读。语句结束，快照就更新。间隙锁更少，插入不容易被范围更新堵住。"},
    {"code": "start transaction;\nselect stock from sku where id = 9 for update;\nupdate sku set stock = stock - 1 where id = 9;", "say": "扣库存是当前读，在同一个事务里锁住再改。这种才需要可重复读或显式锁。位置最新值不要放进这个事务。"},
])
_add("mysql/binlog", "行格式才能同步地址", "SQL", "检索订阅的是行，不是语句。", [
    {"code": "binlog_format = ROW", "say": "每一行的前后镜像都在日志里。从库按行应用。订阅方能看到 poi 的主键和新地址。"},
    {"code": "update poi set updated_at = now() where id = 7;", "say": "语句格式会把 now() 记进 SQL，主从执行时刻不同，时间会漂。行格式记下的是执行后的值。"},
])
_add("mysql/lag", "写后读要决定走不走主", "Python", "延迟是秒，不是布尔值。", [
    {"code": "def read_poi(user, id):\n    if user.wrote_recently(id):\n        return primary.get(id)\n    return replica.get(id)", "say": "刚改过这家店的人，几秒内读主。别人的展示读可以走从库。没有这个分支，作者会看到自己的修改丢了。"},
    {"code": "metrics.gauge(\"replica.lag.seconds\", lag)", "say": "延迟按秒打出来。从库进程活着不代表已经追上。派单和支付不走这台从库。"},
])
_add("mysql/ddl", "大表切换前先追平", "SQL", "在线不代表没有锁。", [
    {"code": "pt-online-schema-change --alter 'add index idx_city (city_id)' D=lbs,t=poi", "say": "工具建新表、拷数据、用触发器或日志追增量。直接 ALTER 大表会在元数据锁上堵住读写。"},
    {"code": "rename table poi to poi_old, poi_new to poi;", "say": "追平之后再换名字。回滚是把名字换回去。切换窗口要和复制延迟一起看。"},
])
_add("mysql/version", "版本不匹配就不要覆盖", "SQL", "一条语句完成判断和写入。", [
    {"code": "update poi\nset address = ?, version = version + 1\nwhere id = ? and version = ?;", "say": "两个编辑同时保存时，后提交的人如果还拿着旧版本，影响行数是 0。这时重新读，而不是无声覆盖别人的地址。"},
    {"code": "if rows == 0:\n    reload()\nelse:\n    cache.delete(id)", "say": "只有更新成功才删缓存。删早了，失败的请求会把随后读到的旧值又写回缓存。"},
])
_add("mysql/count-star", "不要在请求里数全表", "SQL", "多版本下总数不是一个存在表上的整数。", [
    {"code": "select count(*) from poi where city_id = ?;", "say": "有 where 时走 city_id 索引数可见行。全城每次列表都数一次，会和真实查询抢 IO。"},
    {"code": "select approx_count from poi_stats where city_id = ?;", "say": "展示用的总数放统计表或缓存，接受短暂不准。show table status 的行数只是估计，不能当接口返回。"},
])

_add("redis/bigkey", "拆开再逐步删", "Redis", "一把 DEL 会堵住实例。", [
    {"code": "ZCARD geo:hot", "say": "元素个数异常高的格子就是大 key。看元素数量和内存，不要只看 key 总数。"},
    {"code": "ZPOPMIN geo:hot 500", "say": "每次弹出一小批。循环直到空，再删除 key。直接 DEL 一个几百万成员的 zset，单线程会卡在这一条命令上。"},
])
_add("redis/breakdown", "三种流量三种处理", "Python", "不要都回答成加锁。", [
    {"code": "if bloom.missing(id):\n    return None\nv = cache.get(id)\nif v == EMPTY:\n    return None", "say": "布隆说没有就可以挡穿透。空值缓存挡住已经确认不存在的 id，但 TTL 要短，新店不能被空值卡住一天。"},
    {"code": "v = flight.do(id, lambda: db.get(id))", "say": "热点 key 过期时，单飞让同一进程只有一个回源。这是击穿。大量 key 同时过期是雪崩，靠 TTL 加随机抖动。"},
])
_add("redis/pipeline", "管道不原子，Lua 才原子", "Python", "九宫格和释放锁用不同的工具。", [
    {"code": "pipe = redis.pipeline()\nfor cell in cells:\n    pipe.zrange(cell)\nrows = pipe.execute()", "say": "管道减少往返。执行期间别的客户端命令可以插在这些 zrange 之间。结果不是同一个瞬间的快照。"},
    {"code": "redis.eval(unlock_lua, 1, lock_key, token)", "say": "先读 value 再决定删，必须在服务器上一次做完。管道做不到这个判断。Lua 里不要写扫描全库的循环。"},
])
_add("redis/eviction", "能丢的和不能丢的分开", "Redis", "淘汰策略按实例选，不按一个默认值。", [
    {"code": "maxmemory-policy allkeys-lru", "say": "缓存实例内存满了就淘汰近似最久没用的 key。位置展示缓存可以丢。"},
    {"code": "maxmemory-policy noeviction", "say": "放锁和幂等序号的实例不能淘汰。写失败要返回错误。和缓存混在一个 allkeys-lru 实例里，锁会无声消失。"},
])
_add("redis/cluster", "多 key 必须同槽", "Redis", "九宫格的 key 默认会散开。", [
    {"code": "key = \"geo:{\" + city + \"}:\" + cell", "say": "花括号里的城市参与哈希。同一城市的格子进同一个槽，才能放进一次管道。代价是这个城市变成热点，所以只对确实要一起读的 key 加标签。"},
    {"code": "MOVED 3999 geo:{beijing}:wx4g", "say": "槽不在当前节点时，客户端按 MOVED 重试。迁槽过程中还会看到 ASK。当错误吞掉，查询就会缺一块城市。"},
])
_add("redis/geo-precision", "读回来的不是原坐标", "Redis", "误差来自编码和地球模型。", [
    {"code": "GEOADD cell 116.4074 39.9042 shop:1\nGEOPOS cell shop:1", "say": "写进去的经纬度，读出来是 52 位格子的中心，差在亚米到米。不能把 GEOPOS 存成原始 GPS。"},
    {"code": "GEOSEARCH cell FROMLONLAT 116.40 39.90 BYRADIUS 3 km", "say": "距离是球面 Haversine，最坏大约千分之五。展示可用。计费用原始 double 再算。纬度太靠两极会直接报错。"},
])
_add("redis/bitmap", "稠密 id 才能用位图", "Redis", "在线人数和这个人在哪是两套数据。", [
    {"code": "SETBIT online:20261106 42 1\nBITCOUNT online:20261106", "say": "偏移 42 表示用户 42 这一天来过。统计用位计数。id 是稀疏雪花时不要直接当偏移。"},
    {"code": "PFADD dau user:7\nPFCOUNT dau", "say": "稀疏 id 用 HyperLogLog 做近似去重，误差大约百分之一。它回答不了这个用户的坐标。坐标仍在 GEO。"},
])
_add("redis/redlock", "过期之后仍然要幂等", "Python", "多节点锁缩小窗口，不取消重叠。", [
    {"code": "ok = 0\nfor node in nodes:\n    if node.set(key, token, nx=True, px=3000):\n        ok += 1\nreturn ok >= 3", "say": "向 5 个独立节点申请，多数成功才算拿到。这是为了降低主从切换时两个人都持锁的概率。"},
    {"code": "if time.monotonic() - start > 2000:\n    unlock()\n    return False", "say": "申请花太久，锁可能已经快过期，直接放弃。即便如此，进程暂停仍可能让临界区重叠，所以扣库存还要有数据库约束。"},
])
_add("redis/stream", "消费失败还能再认领", "Redis", "List 弹出之后就没了。", [
    {"code": "XADD trace * user 7 lat 39.9 lng 116.4 ts 171000\nXREADGROUP GROUP g worker COUNT 100 STREAMS trace >", "say": "消息 id 由 Redis 生成，不是客户端采集时间。消费组里每个 worker 领走一批。"},
    {"code": "XPENDING trace g\nXCLAIM trace g worker 60000 171000-0", "say": "处理到一半崩溃，消息留在 pending。超时后别的 worker 认领。List 的 BRPOP 做不到这一步。跨机房的长期轨迹仍用 Kafka。"},
])
_add("redis/memory", "过期不等于立刻释放", "Redis", "看 rss、used 和元素个数。", [
    {"code": "INFO memory\nMEMORY USAGE geo:hot", "say": "used 是 Redis 认为的数据量，rss 是操作系统看到的。两者差很多就是碎片。MEMORY USAGE 用来确认某一个格子是不是大 key。"},
    {"code": "maxmemory 8gb\nmaxmemory-policy noeviction", "say": "到顶后写失败、读仍可进行。缓存实例才会改成淘汰。不要等键过期就以为内存马上降下来，大 key 的删除是逐步的。"},
])

_add("es/text-keyword", "一个字段两种用途", "JSON", "搜索和过滤不要共用一个分词字段。", [
    {"code": "\"name\": {\n  \"type\": \"text\",\n  \"fields\": {\"raw\": {\"type\": \"keyword\"}}\n}", "say": "name 分词后搜『川菜』。name.raw 不分词，用来精确匹配和聚合。城市编码只用 keyword。"},
    {"code": "\"city_id\": {\"type\": \"keyword\"}", "say": "如果城市用 text，过滤『北京』会按字匹配，结果不可解释。聚合也会变成单字桶。"},
])
_add("es/inverted", "先命中词，再和地理求交", "JSON", "倒排不懂三公里。", [
    {"code": "{\n  \"bool\": {\n    \"must\": {\"match\": {\"name\": \"咖啡\"}},\n    \"filter\": [{\"term\": {\"city_id\": \"110100\"}}]\n  }\n}", "say": "must 走倒排算相关。filter 用城市词项求交，不参与算分。距离还要另加地理过滤，分词不会把远近算进去。"},
])
_add("es/filter", "首页顺序不要用 ES 分", "JSON", "ES 负责召回，排序在外面。", [
    {"code": "\"filter\": [\n  {\"term\": {\"open\": true}},\n  {\"geo_distance\": {\"distance\": \"3km\", \"loc\": {\"lat\": 39.9, \"lon\": 116.4}}}\n]", "say": "营业和半径是是否符合，放 filter，结果可以缓存。不要放进 must，否则相关性分会被这些条件带着跑。"},
    {"code": "ids = es.search(...)\nreturn ranker.score(ids, user)", "say": "候选 id 交给自己的距离和转化模型。直接用 _score 当首页顺序，远的高文本分会排到前面。"},
])
_add("es/geo", "点和多边形两种字段", "JSON", "写入前坐标已经是约定的 crs。", [
    {"code": "\"loc\": {\"type\": \"geo_point\"}\n\"area\": {\"type\": \"geo_shape\"}", "say": "门店用点，做距离和圆。配送范围用形状，判断用户点在不在多边形里。不要把多边形拆成一串 geo_point。"},
    {"code": "doc[\"loc\"] = {\"lat\": lat, \"lon\": lng}  # 已经是 gcj02", "say": "经度字段是 lon。写反会落到错误的地方，而且不一定报错。ES 不做 WGS84 到 GCJ-02 的转换。"},
])
_add("es/refresh", "可搜和已刷盘不是一件事", "HTTP", "POI 允许一秒后才搜到。", [
    {"code": "PUT /poi/_doc/7?refresh=false", "say": "默认约一秒 refresh 后才能搜到。每次写入都 refresh=true，索引会碎，写入变慢。管理后台要立刻看见时，只对那一次请求刷新。"},
    {"code": "index.translog.durability: request", "say": "宕机恢复看 translog。refresh 只是让新段可搜，不是把数据从操作系统页缓存里 fsync 完。"},
])
_add("es/search-after", "用上一页的排序值续上", "JSON", "深分页不要增大 from。", [
    {"code": "\"sort\": [{\"updated_at\": \"desc\"}, {\"_id\": \"asc\"}]\n\"search_after\": [1710000000000, \"p_1024\"]", "say": "排序要唯一。只有时间的话，同一毫秒的店会在翻页时重复或漏掉，所以加上 id。"},
    {"code": "\"from\": 10000, \"size\": 20", "say": "这种写法每个分片都要先准备一万多条再丢掉。用户翻页改成 search_after。必须跳页就限制最大页，或改成导出。"},
])
_add("es/bulk", "旧版本写不进去", "JSON", "乱序消息靠外部版本挡住。", [
    {"code": "{\"index\":{\"_id\":\"p_7\",\"version\":18,\"version_type\":\"external\"}}\n{\"address\":\"新地址\",\"version\":18}", "say": "版本来自数据库。后到的旧消息版本更小，ES 拒绝，新地址不会被盖回去。冲突记一条指标再继续。"},
    {"code": "for item in response[\"items\"]:\n    if item[\"index\"][\"status\"] >= 500:\n        retry(item)", "say": "批量响应里有的成功有的失败。只重试 5xx 和拒绝，不要把整批再写一遍，否则会把已经成功的版本又冲突一遍。"},
])
_add("es/heap", "重查询先被拒绝", "JSON", "内存打满先看查询形状。", [
    {"code": "indices.breaker.total.limit: 70%", "say": "估算会超过限制的聚合或字段加载直接拒绝，避免把进程打死。这是保护，不是把堆无限加大。"},
    {"code": "\"aggs\": {\"cities\": {\"terms\": {\"field\": \"city_id\", \"size\": 10}}}", "say": "聚合走 keyword 的 doc values。对 text 开 fielddata 会把词项载进堆。size 很大或按距离对全市排序，都会把内存打满。"},
])

_add("backend/timeout-budget", "预算从网关往下减", "Python", "每一跳都用满 200 毫秒，用户侧就是 600 毫秒。", [
    {"code": "budget = 200\ncells = search(timeout=min(50, budget))\nbudget -= elapsed(cells)\nprofiles = fetch(timeout=min(30, budget))", "say": "九宫格最多 50 毫秒，资料再最多 30 毫秒，而且不能超过剩余预算。下游超时设得和网关一样长，上游已经失败了你还在查。"},
    {"code": "if err.timeout and attempt == 0 and budget_left > 20:\n    retry_once()", "say": "只对幂等读重试一次，并且总时间仍在预算里。写位置不在这里盲重试。"},
])
_add("backend/conn-pool", "等待连接的时间单独记", "Go", "池排队会被误看成 SQL 变慢。", [
    {"code": "db.SetMaxOpenConns(32)\ndb.SetMaxIdleConns(16)\ndb.SetConnMaxLifetime(5 * time.Minute)", "say": "32 是下游能承受的并发，不是本机线程数。空闲连接五分钟回收，避免对端已经把连接关掉你还拿着。"},
    {"code": "wait := time.Since(start)\nconn := pool.Get()\nmetrics.Observe(\"pool.wait\", time.Since(start)-wait)", "say": "拿到连接之前的时间是池等待。它和查询本身的时间分开打。池被占满又没有慢查询，先查是不是事务里等了 RPC。"},
])
_add("backend/outbox", "消息和改地址同一个事务", "Python", "发送可以失败，记录不能丢。", [
    {"code": "with db.transaction():\n    poi.update(id, address, version)\n    outbox.insert(id, address, version)", "say": "两行在一个事务里。提交成功就一定有待发送记录。应用先更新再发消息，崩溃会发生在中间。"},
    {"code": "for row in outbox.pending():\n    bus.send(row)\n    outbox.mark_sent(row.id)", "say": "发送成功才标记。标记前崩溃会再发一次，所以消费按 poi id 和 version 幂等。不要指望恰好一次。"},
])
_add("backend/backpressure", "满了就合并，而不是无界排队", "Go", "队列长度是保护，不是装饰。", [
    {"code": "select {\ncase queue <- point:\ndefault:\n    latest.Store(point.UserID, point)\n    dropped.Inc()\n}", "say": "队列满时只保留该用户最新点，并计数。没有 default，生产方会堵住，网关所有接口一起变慢。"},
    {"code": "if traceLag > 30*time.Second {\n    traceConsumer.SkipMiddle()\n}", "say": "轨迹可以丢中间点。最新位置的消费者不要和轨迹共用一条会无限堆积的队列，否则实时查询被历史拖死。"},
])
_add("backend/shard", "查询扇出和写入热点对着看", "Python", "分片键换一个，坏的地方就换一处。", [
    {"code": "shard = hash(city) % n\nsub = hash(user_id) % 4 if hot(cell) else 0\nkey = (shard, cell, sub)", "say": "先按城市分开，热格子再按用户切成 4 份。写入不再打在一个 key 上。"},
    {"code": "ids = []\nfor sub in range(subs(cell)):\n    ids += read(city, cell, sub)", "say": "查询要把热格子的子分片都读出来，或者读一份一秒快照。只读 sub 0 会漏人。这是二次散列的代价。"},
])
_add("backend/degrade", "降级结果要能解释", "Python", "空列表会被客户端理解成附近没有店。", [
    {"code": "try:\n    return live_nearby(lat, lng)\nexcept DependencyDown:\n    return {\"mode\": \"city_hot\", \"items\": hot(city)}", "say": "依赖挂了就返回城市热门，并标明不是实时距离。不要返回空，也不要返回昨天缓存的个人附近列表去派单。"},
    {"code": "if point.accuracy > 500:\n    return {\"mode\": \"district\", \"name\": district}", "say": "精度太差就退回区级，隐藏米。开关和模式都打点，才能知道现在有多少请求不在实时路径上。"},
])
