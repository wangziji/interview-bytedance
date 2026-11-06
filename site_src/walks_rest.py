# Line-by-line walkthroughs for the other domain tracks.

REST_WALKS = {}

def _add(key, title, lang, intro, steps):
    REST_WALKS[key] = [{"title": title, "lang": lang, "intro": intro, "steps": steps}]

_add("java/hashmap", "树化条件不要背错", "Java", "面试写的是判断，不是把 HashMap 源码抄完。", [
    {"code": "if (binCount >= 8 && table.length >= 64) {\n    treeify(bin);\n}", "say": "链表长度到 8 还不够。数组不到 64 时 JDK 8 先扩容。漏掉后半句，追问会直接指出你记混了。"},
    {"code": "int h = key.hashCode();\nint hash = h ^ (h >>> 16);\nint index = hash & (n - 1);", "say": "高 16 位和低 16 位异或，是为了让高位也参与下标。容量 n 是 2 的幂，与 n-1 才等价于取模。"},
    {"code": "map.put(null, value);", "say": "HashMap 允许一个 null 键，放在 0 号桶。ConcurrentHashMap 不允许，因为 null 分不清是没有还是空值。"},
])
_add("java/chm", "检查和写入必须是一次调用", "Java", "ConcurrentHashMap 的读不加锁，复合操作仍要原子方法。", [
    {"code": "if (!map.containsKey(id)) {\n    map.put(id, load(id));\n}", "say": "这两行之间别的线程可以插入。缓存场景会重复打数据库。这不是 ConcurrentHashMap 的线程安全范围。"},
    {"code": "map.computeIfAbsent(id, this::load);", "say": "computeIfAbsent 把检查和放入放在同一次桶锁里。映射函数里不要再查同一张表，可能自己等自己。"},
    {"code": "long size = map.mappingCount();", "say": "并发下 size 是近似值，由 baseCount 和 CounterCell 拼出来。不要拿它做强一致的库存。"},
])
_add("java/jmm", "发布一个配置对象", "Java", "volatile 解决可见性，不解决加加的原子性。", [
    {"code": "private volatile Config config;", "say": "引用是 volatile。写配置的线程把新对象赋给它之后，读线程能看到这个引用，以及构造这个对象时发生的写入。"},
    {"code": "config = new Config(a, b);", "say": "如果 config 不是 volatile，读线程可能看到引用已经变了，但 a、b 还是默认值。双重检查单例就是这个坑。"},
    {"code": "count++;", "say": "这一行是读、改、写。volatile 挡不住两个线程同时加。要用 AtomicLong 或锁。"},
])
_add("java/lock", "锁要包住共享状态", "Java", "synchronized 可重入。不要在锁里等 RPC。", [
    {"code": "synchronized (guard) {\n    if (balance < fare) return false;\n    balance -= fare;\n}", "say": "检查和扣减在同一把锁里。锁对象必须是所有线程共用的那个，锁 this 和锁另一个新对象不是同一把。"},
    {"code": "// 不要写成\nsynchronized (guard) {\n    rpc.charge();\n}", "say": "RPC 在锁里会把所有等待的线程堵住，而且超时后你不知道远端是否成功。先在锁外准备参数，锁里只改内存状态。"},
])
_add("java/pool", "拒绝时要有业务动作", "Java", "线程池参数的顺序比四个数字本身重要。", [
    {"code": "executor = new ThreadPoolExecutor(\n    nCpu, nCpu * 2, 30, SECONDS,\n    new ArrayBlockingQueue<>(1000),\n    new CallerRunsPolicy());", "say": "核心线程满了先进有界队列，队列满了才扩到最大线程，再满才拒绝。无界队列会让最大线程数失效，并把内存打满。"},
    {"code": "public void rejectedExecution(Runnable task, ThreadPoolExecutor ex) {\n    metrics.inc(\"location.reject\");\n    mergeLatest(task);\n}", "say": "位置上报被拒绝时，要按用户合并成最新一点，而不是丢掉后假装没有失败。CallerRunsPolicy 则把压力退回调用线程。"},
])
_add("java/aqs", "只讲 state 和队列", "Java", "业务代码很少直接碰 AQS。讲清谁用它。", [
    {"code": "if (compareAndSetState(0, 1)) {\n    setExclusiveOwnerThread(current);\n    return true;\n}", "say": "独占锁把 state 从 0 改成 1。成功的线程成为拥有者。ReentrantLock 的非公平模式会先走这一下，再进队列。"},
    {"code": "node.waitStatus = SIGNAL;\nLockSupport.park(this);", "say": "抢不到就入队并挂起。释放时 unpark 后继。公平锁按队列来，非公平锁允许插队，吞吐更好，但可能饿死。"},
])
_add("java/threadlocal", "请求结束必须 remove", "Java", "线程池把线程复用之后，ThreadLocal 不再是请求级的。", [
    {"code": "LOCATION.set(point);\ntry {\n    handle();\n} finally {\n    LOCATION.remove();\n}", "say": "set 之后任何异常都要走到 remove。否则下一个请求复用这条线程，会读到上一个用户的坐标。"},
    {"code": "executor.submit(() -> LOCATION.get());", "say": "子线程看不到父线程的 ThreadLocal。要传参就放进任务对象。InheritableThreadLocal 在池化线程上几乎总是错的。"},
])
_add("java/gc", "先看停顿再选收集器", "Java", "没有日志就不要推荐 ZGC。", [
    {"code": "-Xlog:gc*:file=gc.log\n-XX:+UseG1GC\n-XX:MaxGCPauseMillis=200", "say": "默认从 G1 开始。200 毫秒是目标，不是保证。先看日志里的停顿和分配速率，再决定要不要换。"},
    {"code": "-XX:+UseZGC", "say": "堆大、停顿预算很紧时再看 ZGC。没有数据就上 ZGC，只是把未知问题换成另一种未知。"},
])
_add("java/spring-tx", "自调用不会进代理", "Java", "事务失效几乎都是代理没走到。", [
    {"code": "public void checkout() {\n    this.deduct();\n}\n@Transactional\npublic void deduct() { }", "say": "checkout 在同一个类里调用 deduct，不经过 Spring 代理，事务注解不生效。要把 deduct 放到另一个 Bean，或者把自己注入回来。"},
    {"code": "@Transactional(rollbackFor = Exception.class)\npublic void deduct() throws Exception { }", "say": "默认只在 RuntimeException 和 Error 回滚。检查型异常会提交。回滚范围要写出来。"},
])
_add("java/java-geo", "GEO 只存 id", "Java", "Lettuce 或 Jedis 都一样，错在参数顺序和 key 设计。", [
    {"code": "commands.geoadd(\"geo:\" + cell, lng, lat, userId);", "say": "经度在前。cell 是城市或 Geohash 前缀，不要用一个 key 装全国。"},
    {"code": "commands.geosearch(\"geo:\" + cell,\n    GeoSearch.FROMLONLAT(lng, lat),\n    GeoSearch.BYRADIUS(3, KILOMETERS),\n    GeoSearch.WITHDIST);", "say": "用 GEOSEARCH，不要用已经废弃的 GEORADIUS。返回的是 id 和距离。详情再批量去另一份缓存取。"},
    {"code": "commands.hset(\"loc:\" + userId, \"ts\", String.valueOf(ts));", "say": "成员没有 TTL。时间戳另存，查询时丢掉超过 30 秒的人。GEOPOS 读回的坐标是格子中心，不能当原始点存档。"},
])

_add("go/gmp", "不要为每个上报开无界 goroutine", "Go", "GMP 适合大量连接。无界启动会先把内存打满。", [
    {"code": "jobs := make(chan Point, 1024)\nfor i := 0; i < runtime.GOMAXPROCS(0); i++ {\n    go consume(jobs)\n}", "say": "worker 数量跟 P 的数量走，默认是核数。缓冲 1024 是明确的队列，满了发送方会阻塞，形成背压。"},
    {"code": "select {\ncase jobs <- point:\ncase <-ctx.Done():\n    return\n}", "say": "发送也要能取消。否则下游一停，所有处理请求的 goroutine 堆在这个发送上。"},
])
_add("go/chan", "关闭只能由发送方做", "Go", "channel 的坑集中在 close 和 select。", [
    {"code": "func produce(out chan<- Point) {\n    defer close(out)\n    for _, p := range batch {\n        out <- p\n    }\n}", "say": "发送方关闭。接收方用 for range 可以读到关闭前的全部数据，然后结束。多个发送方不能各自 close。"},
    {"code": "select {\ncase p := <-points:\n    handle(p)\ncase <-time.After(time.Second):\n    return\ndefault:\n}", "say": "同时就绪的 case 随机选。default 让它变成非阻塞。位置消费如果漏了超时，工作线程会永远堵在接收上。"},
])
_add("go/slice-map", "append 可能覆盖别人的数组", "Go", "slice 是指针、长度、容量。map 并发会直接崩溃。", [
    {"code": "func clip(s []Point) []Point {\n    return append([]Point(nil), s...)\n}", "say": "先分配新底层数组再拷贝。直接把切片传出去，调用方 append 没超容量时会改到你后面的元素。"},
    {"code": "var mu sync.Mutex\nmu.Lock()\nlatest[id] = point\nmu.Unlock()", "say": "map 的并发读写是 fatal，不是 error。最新位置这种 map 必须加锁，或者按分片拆开。sync.Map 适合读多写少，不是默认更快。"},
])
_add("go/nil-iface", "返回错误不要先装进接口", "Go", "接口里有类型信息时，值是 nil 也不等于 nil。", [
    {"code": "func load() error {\n    var err *os.PathError\n    return err\n}", "say": "具体指针是 nil，但返回的 error 接口带着 *os.PathError 这个类型，调用方的 err != nil 为真。日志里打印又像 nil。"},
    {"code": "func load() error {\n    return nil\n}", "say": "没有错误就直接 return nil。不要先声明一个具体错误类型再返回它。比较错误用 errors.Is，不要比字符串。"},
])
_add("go/context", "超时从入口传下去", "Go", "context 是请求的生命周期，不是参数包。", [
    {"code": "ctx, cancel := context.WithTimeout(ctx, 50*time.Millisecond)\ndefer cancel()", "say": "位置查询的下游超时要短于网关。cancel 必须调用，否则定时器会留到超时才释放。"},
    {"code": "row := db.QueryRowContext(ctx, query, userID)", "say": "数据库和 Redis 调用都要带 ctx。在函数内部另起 context.Background() 会把取消和超时切掉。"},
    {"code": "select {\ncase <-ctx.Done():\n    return ctx.Err()\ndefault:\n}", "say": "取消是协作的。算很重的路径时要看 ctx.Done，不然上游已经走了，你还在算完全城的距离。"},
])
_add("go/gc-escape", "先看分配，再谈 Pool", "Go", "逃逸决定变量在栈上还是堆上。", [
    {"code": "func newPoint(lat, lng float64) *Point {\n    p := Point{Lat: lat, Lng: lng}\n    return &p\n}", "say": "返回局部变量的指针，p 会逃到堆上。每个请求都这样分配，分配速率上去之后 GC 会成为延迟来源。"},
    {"code": "buf := pool.Get().(*Point)\ndefer func() {\n    *buf = Point{}\n    pool.Put(buf)\n}()", "say": "Pool 里的对象可能被下一个请求复用。放回去之前清掉坐标，否则会把上一个用户的位置漏出去。Pool 在 GC 时会被清空，不能当可靠缓存。"},
])
_add("go/singleflight", "同一个 POI 只回源一次", "Go", "进程内合并。多实例仍然各有一次。", [
    {"code": "v, err, _ := flight.Do(key, func() (any, error) {\n    return db.GetPOI(ctx, id)\n})", "say": "key 必须包含坐标系、城市和 id。漏了城市，北京和上海的同名查询会被合并成一次。"},
    {"code": "g, ctx := errgroup.WithContext(ctx)\nfor _, cell := range cells {\n    cell := cell\n    g.Go(func() error { return search(ctx, cell) })\n}\nerr := g.Wait()", "say": "九个邻域用 errgroup 一起查。任何一个失败会取消其余的。cell 要拷进循环变量，否则闭包看见的是最后一格。"},
])
_add("go/pprof", "抓剖面只开在内网", "Go", "线上问题要有抓法。", [
    {"code": "import _ \"net/http/pprof\"\ngo http.ListenAndServe(\"127.0.0.1:6060\", nil)", "say": "监听回环地址。CPU 剖面看热点函数，heap 看谁在分配，goroutine 看谁堵在 channel。"},
    {"code": "go test -race ./...", "say": "数据竞争在测试和预发跑。生产不要开 race，开销明显。goroutine 数持续上涨，通常是退出条件永远不满足。"},
])

_add("python/gil", "CPU 距离不要丢进线程池", "Python", "先判断任务是 CPU 还是 IO。", [
    {"code": "def batch(points):\n    return [haversine_m(*p) for p in points]", "say": "纯 Python 循环持有 GIL。开 8 个线程不会让这段变快，它们轮流执行字节码。"},
    {"code": "with ProcessPoolExecutor() as pool:\n    pool.map(batch, chunks)", "say": "CPU 密集用进程。进程间不要来回拷贝几百万个点，按块切。在线单次请求不值得为了这点计算去 fork。"},
])
_add("python/asyncio", "协程里不能调用阻塞客户端", "Python", "一个阻塞调用会卡住整个事件循环。", [
    {"code": "async def nearby(lat, lng):\n    cells = neighbors9(encode(lat, lng, 6))", "say": "这一行是纯计算，很短，可以留在协程里。"},
    {"code": "    async with redis.pipeline() as pipe:\n        for cell in cells:\n            pipe.zrange(cell)\n        raw = await pipe.execute()", "say": "await 才会让出循环。如果这里写成同步 redis 的 execute，所有请求一起等这一个阻塞调用。"},
    {"code": "    return await asyncio.wait_for(fetch_profiles(ids), timeout=0.05)", "say": "扇出查询要有整体超时，并且短于网关超时。超时后告诉上游失败，不要继续用空列表假装附近没有人。"},
])
_add("python/pitfalls", "默认参数只算一次", "Python", "这是手写题前后最常见的快问。", [
    {"code": "def add_point(p, buf=[]):\n    buf.append(p)\n    return buf", "say": "buf 在函数定义时创建一次。第二次调用会看见第一次的点。轨迹缓冲因此串用户。"},
    {"code": "def add_point(p, buf=None):\n    if buf is None:\n        buf = []\n    buf.append(p)\n    return buf", "say": "默认用 None，在函数体内新建列表。比较坐标值用 ==。is 只比较是不是同一个对象。"},
])
_add("python/decorator", "缓存键必须包含坐标系", "Python", "装饰器适合校验和日志，不适合藏起重试。", [
    {"code": "def cached(fn):\n    @functools.wraps(fn)\n    def wrapper(lat, lng, crs):\n        key = (round(lat, 5), round(lng, 5), crs)\n        ...\n        return fn(lat, lng, crs)\n    return wrapper", "say": "wraps 保留原函数的名字和签名，否则框架读参数会失败。key 里没有 crs，WGS84 和 GCJ-02 的结果会撞在一起。"},
])
_add("python/process", "服务进程里用 spawn", "Python", "fork 会继承已经连上的 Redis。", [
    {"code": "ctx = multiprocessing.get_context(\"spawn\")\npool = ctx.Pool(processes=4)", "say": "spawn 会重新导入模块，不复制父进程的连接和锁。服务已经启动后再 fork，子进程里的数据库连接是坏的。"},
    {"code": "pool.map(compress_chunk, chunks)", "say": "批量 Douglas-Peucker 适合丢进进程池。在线一次请求的几十个点，直接在当前进程算完。"},
])
_add("python/geo-py", "校验在边界做完", "Python", "库负责鲁棒性，原理你要先能讲。", [
    {"code": "class PointIn(BaseModel):\n    lat: float = Field(ge=-90, le=90)\n    lng: float = Field(ge=-180, le=180)\n    crs: Literal[\"wgs84\", \"gcj02\"]", "say": "纬度 200 在模型层就被拒绝。crs 是枚举，不能是自由字符串。"},
    {"code": "if body.crs == \"gcj02\":\n    lat, lng = to_wgs84(body.lat, body.lng)", "say": "转换只在这一处。核心函数一律接收 wgs84。shapely 做点在多边形时，也要确认输入已经是同一套坐标。"},
])
_add("python/typing", "经纬度不要共用一个 float", "Python", "类型要让写反变得困难。", [
    {"code": "Latitude = NewType(\"Latitude\", float)\nLongitude = NewType(\"Longitude\", float)\n\ndef distance(lat: Latitude, lng: Longitude) -> float:\n    ...", "say": "两个 NewType 在检查器里不能互换。运行时它们仍是 float，所以校验还要有。"},
    {"code": "lat: Latitude | None = None", "say": "None 表示用户没授权。不能默认成 0，那是几内亚湾，距离和城市都会错。"},
])

_add("android/fused", "按场景选优先级", "Kotlin", "不要把高精度和 1 秒间隔当成默认。", [
    {"code": "val request = LocationRequest.Builder(Priority.PRIORITY_BALANCED_POWER_ACCURACY, 15_000)\n    .setMinUpdateDistanceMeters(30f)\n    .setMaxUpdateDelayMillis(60_000)\n    .build()", "say": "同城浏览用平衡精度，15 秒一笔，移动不到 30 米不回调。maxUpdateDelay 允许系统把点攒一批再给你，省一次无线电唤醒。"},
    {"code": "if (location.accuracy > 100) return", "say": "精度半径太大的点不能参与到店。导航场景才把优先级改成 HIGH_ACCURACY，并且只在行程前台服务里开。"},
])
_add("android/permission", "权限按版本分开要", "XML", "一次弹出所有权限，用户拒绝后功能全死。", [
    {"code": "<uses-permission android:name=\"android.permission.ACCESS_COARSE_LOCATION\" />\n<uses-permission android:name=\"android.permission.ACCESS_FINE_LOCATION\" />\n<uses-permission android:name=\"android.permission.ACCESS_BACKGROUND_LOCATION\" />", "say": "精确和大致是两档。Android 10 起后台定位单独申请。Android 12 用户可以只给大致位置，业务必须还能在城市级工作。"},
    {"code": "if (fine != PERMISSION_GRANTED && coarse == PERMISSION_GRANTED) {\n    showCityOnly()\n}", "say": "只拿到大致位置时，不要显示米级距离。界面上标明是城市或区，并给一个升级精确权限的理由。"},
])
_add("android/fgs", "行程用前台服务", "Kotlin", "持续定位靠可见通知，不靠拉活。", [
    {"code": "ServiceCompat.startForeground(\n    this, id, notification,\n    ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION\n)", "say": "Android 14 要在 startForeground 里带上类型。调用之前定位权限必须已经拿到，否则系统抛 SecurityException。"},
    {"code": "override fun onDestroy() {\n    stopForeground(STOP_FOREGROUND_REMOVE)\n}", "say": "行程结束必须停掉通知。用户划掉任务后如果通知还在，位置就还在上报，这是投诉来源。"},
])
_add("android/battery", "静止就不要轮询", "Kotlin", "省电是功能指标。", [
    {"code": "if (speed < 0.5) {\n    request.setMinUpdateIntervalMillis(120_000)\n} else {\n    request.setMinUpdateIntervalMillis(5_000)\n}", "say": "几乎不动时把间隔放到两分钟。导航中才缩短。失败重试要退避，地下室里不要每秒打一次。"},
    {"code": "geofencingClient.addGeofences(list, pending)", "say": "到店能用围栏触发，就不要用 5 秒定位轮询。系统围栏大约 100 个，全城店不能都下发。"},
])
_add("android/geofence-api", "只登记和用户相关的围栏", "Kotlin", "100 个上限是产品约束。", [
    {"code": "val fence = Geofence.Builder()\n    .setRequestId(storeId)\n    .setCircularRegion(lat, lng, 80f)\n    .setTransitionTypes(GEOFENCE_TRANSITION_ENTER or GEOFENCE_TRANSITION_EXIT)\n    .setLoiteringDelay(60_000)\n    .build()", "say": "半径 80 米，进入和离开都要。停留延迟 60 秒，减少在边界上来回触发。requestId 用店 id，方便回调对上业务。"},
    {"code": "if (registered.size > 90) registered.removeOldest()", "say": "留出余量，不要正好打到 100 再被系统拒绝。超出的判定放到服务端。回调可能延迟几分钟，不能直接改支付状态。"},
])
_add("android/android-crs", "上传前标明 crs", "Kotlin", "系统定位是 WGS84，国内地图展示常常不是。", [
    {"code": "val fix = LocationFix(\n    lat = location.latitude,\n    lng = location.longitude,\n    crs = \"wgs84\"\n)", "say": "FusedLocation 给的是 WGS84。这里不要先转成 GCJ-02 再上传，除非协议写明服务端收的是火星坐标。"},
    {"code": "mapView.moveCamera(toGcj02(fix.lat, fix.lng))", "say": "转换只放在地图适配层。围栏如果是在地图上画的，判断用的多边形也要是同一套，否则人站在店里会被判在外面。"},
])
_add("android/upload", "先落库再上传", "Kotlin", "弱网是默认条件。", [
    {"code": "dao.insert(point)\nwork.enqueue(uploadRequest)", "say": "点先进本地表。进程被杀之后内存队列会丢。上传成功再删除这行。"},
    {"code": "body.seq = trip.nextSeq()\nbody.ts = point.elapsedRealtime", "say": "序号按行程递增，服务端用来去重。时间用采集时间。到达服务器的时间只用来发现延迟，不用来覆盖轨迹。"},
])
_add("android/anr", "抽稀离开主线程", "Kotlin", "地图页卡顿经常是在主线程做空间计算。", [
    {"code": "scope.launch(Dispatchers.Default) {\n    val thin = douglasPeucker(points, 8.0)\n    withContext(Dispatchers.Main) { map.setPolyline(thin) }\n}", "say": "Douglas-Peucker 和围栏判断放 Default。只有把结果交给地图时回到主线程。阈值 8 米，单位要写出来。"},
    {"code": "clusterer.addItems(screenGrid(points, cellPx = 48))", "say": "上千个点先按屏幕网格聚合。每个手势都做球面距离会卡。缩放后再展开。"},
])

_add("hot/level-31", "回答时主动改一个约束", "口述", "3-1 的差别在追问，不在题面。", [
    {"code": "先写能跑的版本\n再说最坏复杂度\n再改一个约束：内存放不下 / 有并发 / 要外部存储", "say": "三句按这个顺序。只停在第一句，听起来像 2-1。第三句要具体，比如『10 亿个点不能放进这张哈希表，按 geohash 分片再归并』。"},
])
_add("hot/mysql-index", "按查询建联合索引", "SQL", "先看等值列，再看范围列。", [
    {"code": "select id from poi\nwhere city_id = 110100 and category = 'cafe' and lat between ? and ?", "say": "等值列是 city_id 和 category，范围是 lat。索引顺序应是 (city_id, category, lat)。lat 放前面，category 的过滤就用不上这棵索引。"},
    {"code": "explain select ...\\G", "say": "看 key 是不是这棵联合索引，type 是不是 range，Extra 有没有 Using filesort。rows 很大说明选择性不够，不是再加一个单列索引就能好。"},
])
_add("hot/mvcc", "快照读和当前读", "SQL", "两种读的锁不一样。", [
    {"code": "start transaction;\nselect balance from account where id = 7;", "say": "可重复读下，这是快照读。事务里第一次读建立 Read View，后面重复读看到的是当时的版本。"},
    {"code": "select balance from account where id = 7 for update;", "say": "for update 是当前读，会锁住这条索引记录。要防止别人在范围内插入，还要靠间隙锁。说『可重复读完全没有幻读』会在这一行被追问打回来。"},
])
_add("hot/row-lock", "没有索引就锁很多行", "SQL", "行锁锁的是索引记录。", [
    {"code": "update loc set status = 0 where user_id = 42;", "say": "user_id 上有索引，就锁这一条。没有索引，扫描到的记录都可能被锁，并发更新会挤在一起。"},
    {"code": "show engine innodb status;", "say": "死锁看这段输出里的事务和等待的锁，不要靠猜加锁顺序。修复是固定更新顺序，并缩短事务。"},
])
_add("hot/sql-opt", "先解释计划再改", "SQL", "慢查询的顺序是证据、计划、改写。", [
    {"code": "select id from poi where city_id = ? and id > ? order by id limit 20;", "say": "深度分页不要用大 offset。用上一次的主键当游标，引擎可以从这个主键接着扫。"},
    {"code": "select count(*) from poi where city_id = ? and category = ?;", "say": "如果这条很慢，先看联合索引是否盖住这两个等值列。不要先加 Redis 计数，除非你接受计数和表短暂不一致。"},
])
_add("hot/redis-struct", "ZRANGE 的代价", "Redis", "GEO 是 zset。把命令和复杂度连起来。", [
    {"code": "ZRANGE key 0 99", "say": "从排名 0 取 100 个。跳表定位起点大约 O(log N)，再输出 100 个。不是 O(1)，也不是把整个集合扫一遍。"},
    {"code": "GEOADD geo:wx4g 116.40 39.90 user:7", "say": "经度、纬度、成员。score 是 52 位 geohash，不是米。成员只放 id。"},
])
_add("hot/dist-lock", "加锁和释放都要原子", "Redis", "锁过期之后的误删是追问重点。", [
    {"code": "SET lock:{order} {uuid} NX PX 3000", "say": "NX 保证没有锁才能设置，PX 给过期时间。必须是一条命令。先 GET 再 SET 中间可以插进来别人。"},
    {"code": "if redis.call('get', KEYS[1]) == ARGV[1] then\n  return redis.call('del', KEYS[1])\nend", "say": "Lua 里先比对自己的 uuid 再删。否则你的锁过期后别人拿到了，你的解锁会把别人的锁删掉。"},
])
_add("hot/redis-persist", "AOF 重放", "Redis", "恢复路径要能讲成启动顺序。", [
    {"code": "appendfsync everysec", "say": "大约每秒刷一次盘。宕机可能丢最近一秒的写。always 每个命令都刷，位置高写入会把磁盘打满。"},
    {"code": "BGREWRITEAOF", "say": "重写把历史命令压成最小集合。只有 AOF 时，启动按重写后的文件再加增量重放。从节点不是备份，误删除会复制过去。"},
])
_add("hot/cache-db", "先改库再删缓存", "Python", "删除失败要有补偿。", [
    {"code": "db.update(poi)\ntry:\n    cache.delete(poi.id)\nexcept Exception:\n    outbox.add('cache-del', poi.id)", "say": "数据库是 POI 的事实来源。删缓存失败就写进发件箱，后面重试。没有这一步，旧地址会一直被读到。"},
    {"code": "if cache.get(id) is None and db.get(id) is None:\n    cache.set(id, EMPTY, ex=30)", "say": "空值短 TTL，挡住穿透。30 秒后可以再查。位置这种很快会变的状态，不要用这么长的空值。"},
])
_add("hot/kafka", "分区键决定顺序", "Java", "全局有序和单用户有序不是一回事。", [
    {"code": "producer.send(new ProducerRecord<>(topic, userId, point));", "say": "key 用 userId，同一用户进同一分区，分区内有序。用随机 key 会把一个人的轨迹打散。"},
    {"code": "consumer.commitSync();\nhandle(record);", "say": "先提交再处理，崩溃会丢消息。位置轨迹应先按序号幂等处理，再提交位移。重复投递是正常情况。"},
])
_add("hot/rate-limit", "令牌桶允许短突发", "Python", "三种算法的差别在这一小段状态上。", [
    {"code": "def allow(bucket, now):\n    bucket.tokens = min(cap, bucket.tokens + (now - bucket.ts) * rate)\n    bucket.ts = now\n    if bucket.tokens < 1:\n        return False\n    bucket.tokens -= 1\n    return True", "say": "先按流逝时间补令牌，上限是桶容量。有存量就可以一次通过，所以短突发被允许。漏桶则是出水速度恒定，多出来的请求排队或拒绝。"},
])
_add("hot/id-gen", "号段只分配一段", "Python", "高并发 ID 不要每笔都打数据库。", [
    {"code": "class Segment:\n    def next_id(self):\n        if self.cur >= self.end:\n            self.cur, self.end = db.alloc(step=1000)\n        self.cur += 1\n        return self.cur", "say": "数据库只在段用完时写一次，发号在内存里完成。趋势递增，但不是全局每毫秒严格加一。时钟回拨的雪花算法要另外处理。"},
])
_add("hot/consistency", "本地事务加发件箱", "Python", "最终一致要有一张能重试的表。", [
    {"code": "with db.transaction():\n    orders.mark_paid(order_id)\n    outbox.insert('paid', order_id)", "say": "订单状态和消息放在同一个数据库事务里。提交成功后，后台再把 outbox 发到消息队列。这样不会出现付了款但消息丢了。"},
    {"code": "def on_paid(order_id):\n    if ledger.exists(order_id):\n        return\n    ledger.insert(order_id)", "say": "消费端用订单号做幂等。消息至少会到一次，重复投递不能记两笔账。"},
])
_add("hot/tcp", "第三次是确认这次序号", "口述", "两句话讲完，不要从物理层开始。", [
    {"code": "客户端 SYN  seq=x\n服务端 SYN+ACK seq=y ack=x+1\n客户端 ACK ack=y+1", "say": "前两次交换了双方的初始序号。第三次让服务端知道客户端认可的是这一次，而不是一个迟到的旧 SYN。两次握手时，服务端可能为一个已经放弃的连接分配资源。"},
])
_add("hot/url-path", "只讲你的服务经过的盒子", "口述", "链路按层，不要背全集。", [
    {"code": "DNS -> TLS -> 网关鉴权限流 -> 位置服务校验 crs -> Redis 九宫格 -> 资料缓存", "say": "这是附近的人一次读的真实路径。讲的时候停在你负责的服务，说出超时和失败时返回什么。不要从网卡中断开始。"},
])
_add("hot/lsm", "追加写，读可能跨层", "Python", "轨迹冷数据适合这个模型。", [
    {"code": "memtable[user_id].append(point)\nwal.append(point)", "say": "先写内存表和日志，写是顺序的。冻住之后刷成有序文件。随机更新不是它的优势。"},
    {"code": "for level in levels:\n    hit = level.get(user_id, ts)\n    if hit: return hit", "say": "读要从新到旧查多层。布隆过滤器用来跳过肯定没有的文件。删除常常是墓碑，合并前空间不会立刻回来。最新位置不要走这条读路径。"},
])
_add("hot/es-sync", "按主键幂等写入", "Python", "不要在业务里双写。", [
    {"code": "for change in binlog:\n    search.index(id=change.poi_id, doc=change.after, version=change.version)", "say": "变更日志是来源。同一个主键重复投递，用版本盖住旧文档。应用同时写 MySQL 和搜索引擎，失败时两边会分叉。"},
    {"code": "search.search_after(last_id, size=50)", "say": "深分页用上一页的排序值接着取。from 加 size 到几千，协调节点要拉大量命中再丢掉。"},
])
_add("hot/discovery", "熔断要有探测", "Python", "打开之后不是永远失败。", [
    {"code": "if breaker.open and now < breaker.until:\n    return fallback_city_list()", "say": "熔断打开时快速失败，返回城市热门这种能解释的降级。不要返回空指针或过期的个人附近列表。"},
    {"code": "if now >= breaker.until:\n    breaker.half_open()\n    if call(): breaker.close()", "say": "到时间放少量探测。成功再合上。没有探测，下游恢复了你仍然全失败。"},
])
_add("hot/row-col", "连续维放在内层", "Python", "这是缓存，不是复杂度。", [
    {"code": "for r in range(rows):\n    for c in range(cols):\n        total += matrix[r][c]", "say": "行内元素在内存里相邻，内层扫列是顺序读，能吃满缓存行。"},
    {"code": "for c in range(cols):\n    for r in range(rows):\n        total += matrix[r][c]", "say": "内层跳整行。数据一大，缓存和预取都失效，耗时明显变长，但大 O 仍是 O(rows*cols)。"},
])
_add("hot/project-31", "开口用四段", "口述", "每一段都要能被追问。", [
    {"code": "边界：同城到店距离，我负责上报到存储\n量级：写入每秒数万，p99 几十毫秒\n取舍：服务端只存 WGS84，放弃在库里兼容所有历史脏坐标\n故障：展示用了另一套 crs，距离中位数整体平移", "say": "数字和被放弃的方案必须是你自己的。最后准备一句：量再大十倍，先坏的是热点格子，不是磁盘容量。"},
])

_add("backend/capacity", "把公式写在旁边", "Python", "面试官改一个数，你只替换一项。", [
    {"code": "online = 50_000_000 * 0.10\nqps = online / 10 * 3\nbandwidth = qps * 100", "say": "5000 万日活、10% 在线、10 秒上报、峰值系数 3、每包 100 字节。先写出 qps，再乘包长得到带宽。这些是假设，不是公司内部数字。"},
    {"code": "ram = online * 100", "say": "在线状态大约几百 MB。所以结论是内存不是瓶颈，热点格子和连接数才是。"},
])
_add("backend/redis-geo", "拆 key 再查询", "Python", "一个 zset 装全国会成为单线程热点。", [
    {"code": "cell = encode(lat, lng, 5)\nredis.geoadd(f\"city:{city}:{cell}\", lng, lat, shop_id)", "say": "key 里有城市和格子。5 位大约 5 公里，适合商圈级。经度在前。"},
    {"code": "ids = []\nfor neighbor in neighbors9(cell):\n    ids += redis.geosearch(f\"city:{city}:{neighbor}\", lon=lng, lat=lat, radius=3, unit=\"km\")", "say": "九个 key 都查。GEOSEARCH 的半径过滤是球面距离，仍要知道它最坏大约 0.5% 的模型误差，计费再算一次。"},
])
_add("backend/hot-key", "热格子做一秒快照", "Python", "三里屯会打进一个 key。", [
    {"code": "def read_cell(cell):\n    hit = local.get(cell)\n    if hit and hit.age < 1:\n        return hit.ids", "say": "展示用的附近列表可以缓存 1 秒。这一秒内同一格的读合并成一次 Redis 查询。派单要最新位置，不能走这个缓存。"},
    {"code": "    ids = flight.do(cell, lambda: redis.zrange(cell))\n    local.set(cell, ids, ttl=1)\n    return ids", "say": "singleflight 让并发的第一次请求只有一个打到 Redis。key 是格子，不是用户。"},
])
_add("backend/mysql", "空间条件和普通条件分开", "SQL", "两列范围不是空间索引。", [
    {"code": "select id from poi\nwhere geohash6 in (?, ?, ?, ?, ?, ?, ?, ?, ?)\n  and open_status = 1", "say": "九个前缀用 IN。open_status 如果选择性高，可以放在联合索引后面。不要写 lat between and lng between 再指望两个 B+ 树同时好用。"},
    {"code": "select id from fence where mbrintersects(geom, point);", "say": "多边形管理查询可以用空间索引。高写入的在线位置不要走这张表。"},
])
_add("backend/pipeline", "一条管道两个消费者", "Python", "最新位置和历史轨迹分开存。", [
    {"code": "def on_point(record):\n    if record.ts >= latest_ts[record.user_id]:\n        save_latest(record)", "say": "这个消费者只维护最新位置。更旧的点直接忽略，避免乱序覆盖。"},
    {"code": "def on_trace(record):\n    cold.append(record.user_id, record.ts, record.lat, record.lng)", "say": "另一个消费者按用户和事件时间追加。它落后几秒可以接受。两个消费者读同一个分区，顺序仍然按用户保持。"},
])
_add("backend/idempotency", "序号单调才覆盖", "Python", "重试一定发生。", [
    {"code": "def apply(point):\n    prev = db.seq(point.user_id, point.trip_id)\n    if point.seq <= prev:\n        return\n    db.save(point)\n    db.cas_seq(point.user_id, point.trip_id, prev, point.seq)", "say": "序号小于等于已处理的，是重复包，丢掉。cas 避免两个请求同时越过同一个旧序号。幂等表按行程过期，不能无限长。"},
])
_add("backend/observe", "看业务分布，不只看 CPU", "Python", "坐标系写反时 CPU 可能仍然正常。", [
    {"code": "metrics.histogram(\"nearby.empty\", city)\nmetrics.histogram(\"distance.p50\", city)", "say": "空结果突然升高，可能是索引坏了，也可能是客户端坐标系错了。距离中位数整体平移几百米，优先怀疑转换被调用了两次。按城市看，避免一个小城被全国均值盖住。"},
])

_add("rec/objective", "硬条件先滤掉", "Python", "排序分不应该负责营业和库存。", [
    {"code": "cands = [s for s in shops if s.open and s.stock > 0 and s.eta <= promise]", "say": "营业、有货、能在承诺时间送到，是硬过滤。关掉的店即使点击率高也不进排序。"},
    {"code": "score = 0.5 * p_pay + 0.3 * p_redeem - 0.2 * late_risk", "say": "剩下的才是多目标。权重按场景变。只优化点击会推出标题党，只优化成交会推出远且容易超时的高价店。"},
])
_add("rec/decay", "按品类给 sigma", "Python", "全国一个衰减会惩罚小城市。", [
    {"code": "def gauss(dist, sigma):\n    return math.exp(-(dist ** 2) / (2 * sigma * sigma))", "say": "距离越大乘上的系数越小。sigma 是尺度。咖啡的 sigma 小，景区的 sigma 大。"},
    {"code": "if scene == \"delivery\" and eta > promise:\n    return None", "say": "配送不要只看直线距离。过了承诺时间直接丢掉。直线近但要过河的店，ETA 会把它滤掉。"},
])
_add("rec/recall", "先把城市圈住", "Python", "相似不等于附近。", [
    {"code": "ids = spatial.within(city, radius)\nranked = vector.score(ids, user_vec)[:200]", "say": "先拿空间候选，再在里面算相似。先全库做向量检索再滤城市，远方的相似店会占满名额。"},
    {"code": "quota = {\"spatial\": 80, \"reorder\": 40, \"new\": 20}", "say": "每路有配额。新品不和老店在一个热度里竞争，否则新店没有曝光。"},
])
_add("rec/multitask", "转化要在全空间估计", "Python", "只在点击样本上训练，会对全部曝光打分时偏掉。", [
    {"code": "p_ctr = tower_click(features)\np_cvr = tower_pay(features)\np_ctcvr = p_ctr * p_cvr", "say": "点击率和点击后转化分开学，相乘得到曝光空间的成交概率。这就是 ESMM 要解决的选择偏差。样本不够时，先用树模型加距离特征当基线。"},
])
_add("rec/feature", "三个位置不要合成一个字段", "Python", "作者所在地、内容 POI、用户现在的位置经常不一致。", [
    {"code": "features = {\n  \"home_cell\": user.home_cell,\n  \"now_cell\": ctx.cell,\n  \"poi_cell\": item.poi_cell,\n  \"dist_m\": haversine_m(ctx.lat, ctx.lng, item.lat, item.lng),\n}", "say": "常驻地、当前位置、店铺格子分开。交叉特征用当前距离和是否落在常去格子。缺失 POI 的内容只能降到城市级，并把地理权重降下来。"},
])
_add("rec/bias", "按距离分层留曝光", "Python", "系统会自己学成只推最近的店。", [
    {"code": "for band in (1000, 3000, 5000):\n    picked += sample(cands_within(band), quota[band])", "say": "每一档距离都有最小曝光。否则模型只见过近处的正样本，稍远的好店永远出不来。探索流量不能打到运力已经满的店。"},
])
_add("rec/eval", "指标按距离段拆开", "Python", "一个整体 AUC 不够。", [
    {"code": "for band in bands:\n    report(gauc(requests_in(band)), timeout_rate(band))", "say": "按距离段看排序质量和超时率。近处好看、远处超时，整体 AUC 仍然可能上升。实验用用户分桶时，要承认店铺运力是共享的，桶和桶会互相影响。"},
])

_add("agent/why", "能用检索就不要自由发挥", "Python", "Agent 是工具编排。", [
    {"code": "if intent in {\"nearby\", \"filter\"}:\n    return search_poi(**slots)\nplan = planner.plan(intent)", "say": "固定的附近列表和筛选走确定性检索。只有开放条件、多步比较才进入计划和工具循环。"},
])
_add("agent/tools", "返回里必须有 id 和 crs", "JSON", "工具的形状比模型名字重要。", [
    {"code": "{\n  \"poi_id\": \"p_1024\",\n  \"name\": \"示例川菜\",\n  \"crs\": \"gcj02\",\n  \"distance_m\": 860,\n  \"eta_min\": 32,\n  \"open\": true\n}", "say": "模型只能引用这个 poi_id。没有 crs，下游不知道距离是在哪套坐标里算的。open 是布尔值，不是模型自己说的营业中。"},
])
_add("agent/hallucination", "回答里的店必须回链", "Python", "提示词里写不要编造，不够。", [
    {"code": "allowed = {item[\"poi_id\"] for item in tool_results}\nfor mentioned in extract_ids(reply):\n    if mentioned not in allowed:\n        reject(reply)", "say": "最终回答里出现的店、价格、营业时间都要能对上某次工具返回的 id。对不上就拒绝或重写。校验在模型外面，用代码做。"},
])
_add("agent/rag", "先按城市过滤再向量", "Python", "同名店会跨城。", [
    {"code": "docs = index.search(query, filter={\"city\": city, \"poi_id\": poi_id})", "say": "过滤在检索里做。先向量召回再看城市，会把上海的同名店介绍安到北京。文档还要带更新时间，过期活动不进上下文。"},
])
_add("agent/write", "下单前给结构化确认", "Python", "写操作和读操作分开。", [
    {"code": "draft = {\n  \"poi_id\": chosen,\n  \"address\": addr,\n  \"pay_fen\": price,\n  \"eta_min\": eta,\n}\nwait_for_user_confirm(draft)\norder.create(draft, idempotency_key=key)", "say": "确认卡片的字段来自工具，不是模型复述时改写的。幂等键防止重试创建两张订单。没确认就停。"},
])
_add("agent/eval-agent", "离线回放固定任务", "Python", "看任务是否完成，不看文采。", [
    {"code": "for task in tasks:\n    trace = agent.run(task, tools=stubs)\n    assert trace.poi_ids <= stub_ids\n    assert task.done(trace)", "say": "工具打桩，模型版本固定。断言店 id 都来自桩的返回，并且任务条件达成，比如半径和营业状态都传了。缺定位的任务必须追问，不能默认北京。"},
])
_add("agent/context", "上下文只放短卡片", "Python", "失败时不能用记忆里的旧库存。", [
    {"code": "cards = [{\"id\": s.id, \"dist\": s.dist, \"eta\": s.eta, \"open\": s.open} for s in top]\nif tool.status == \"timeout\":\n    say(\"实时库存没取到\")\n    return", "say": "短卡片进上下文。超时和空结果是两种状态。超过几分钟的工具结果不能用来下单。没有定位权限就追问，不把原始轨迹点放进提示词。"},
])
