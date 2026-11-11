/* Teaching diagrams. Markup is ours, looked up by id, never built from user text. */
(function () {
  function svg(name, w, h, body) {
    return `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="cap-${name}">
      <defs>
        <marker id="mk-${name}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M 0 1.2 L 9 5 L 0 8.8 Z" fill="#c6452f"></path>
        </marker>
      </defs>
      <style>
        .t { font-family: "Noto Sans SC", "PingFang SC", sans-serif; font-size: 13px; fill: #1b1914; }
        .b { font-family: "Noto Sans SC", "PingFang SC", sans-serif; font-size: 13px; font-weight: 700; fill: #14352e; }
        .s { font-family: "Noto Sans SC", "PingFang SC", sans-serif; font-size: 12px; fill: #5e584e; }
        .box { fill: #fffdf8; stroke: #14352e; stroke-width: 1.5; }
        .soft { fill: #e7f3ea; stroke: #1d4a3e; stroke-width: 1.4; }
        .hot { fill: #fde8e2; stroke: #c6452f; stroke-width: 1.4; }
        .gold { fill: #f8efd4; stroke: #a97820; stroke-width: 1.4; }
        .chip { fill: #14352e; }
        .chip text { fill: #fffdf8; font-family: "IBM Plex Mono", monospace; font-size: 12px; }
        .arr { stroke: #c6452f; stroke-width: 1.6; fill: none; marker-end: url(#mk-${name}); }
      </style>
      ${body}
    </svg>`;
  }

  function chip(x, y, label, w) {
    w = w || 28;
    return `<g class="chip"><rect x="${x}" y="${y}" width="${w}" height="22" rx="6"></rect><text x="${x + w / 2}" y="${y + 15}" text-anchor="middle">${label}</text></g>`;
  }

  window.FIGURES = {
    gmp: {
      caption: "每个 P 绑一条 M，并有自己的本地队列。本地空了就去别的 P 偷一半。网络等待挂在 netpoller 上，不占着 M。",
      svg: svg("gmp", 400, 292, `
        <rect class="gold" x="16" y="12" width="368" height="36" rx="8"></rect>
        <text class="b" x="28" y="35">全局队列</text>
        ${chip(118, 19, "G")}${chip(152, 19, "G")}${chip(186, 19, "G")}
        <rect class="box" x="16" y="64" width="176" height="150" rx="10"></rect>
        <text class="b" x="28" y="86">P0 · 本地队列</text>
        <text class="s" x="28" y="106">M0 正在跑</text>
        ${chip(28, 118, "G")}${chip(62, 118, "G")}${chip(96, 118, "G", 44)}
        <text class="s" x="108" y="133">运行中</text>
        <rect class="box" x="208" y="64" width="176" height="150" rx="10"></rect>
        <text class="b" x="220" y="86">P1 · 本地队列</text>
        <text class="s" x="220" y="106">M1 正在跑</text>
        ${chip(220, 118, "G")}
        <text class="s" x="256" y="133">空了就去偷</text>
        <path class="arr" d="M188 150 H208"></path>
        <text class="s" x="16" y="240">阻塞系统调用：M 卡在内核，P 摘下来交给另一条 M。</text>
        <text class="s" x="16" y="262">网络等待：G 挂到 netpoller，P 立刻去跑别的 G。</text>
        <text class="s" x="16" y="284">能同时跑 Go 代码的数量 ≈ P 的数量 = GOMAXPROCS，不是 G 的数量。</text>
      `),
    },
    channel: {
      caption: "无缓冲必须发送和接收碰上。有缓冲还有空位时发送直接返回，满了才堵住。关闭后只能把剩下的读完，不能再发送。",
      svg: svg("channel", 400, 230, `
        <rect class="box" x="12" y="16" width="180" height="150" rx="10"></rect>
        <text class="b" x="24" y="40">无缓冲</text>
        ${chip(28, 58, "发", 36)}
        <path class="arr" d="M70 69 H108"></path>
        ${chip(112, 58, "收", 36)}
        <text class="s" x="24" y="108">没有格子。</text>
        <text class="s" x="24" y="128">两边都到了</text>
        <text class="s" x="24" y="148">这次交接才完成。</text>
        <rect class="box" x="208" y="16" width="180" height="150" rx="10"></rect>
        <text class="b" x="220" y="40">有缓冲 · 容量 4</text>
        <rect class="soft" x="224" y="58" width="32" height="28" rx="4"></rect>
        <rect class="soft" x="260" y="58" width="32" height="28" rx="4"></rect>
        <rect class="box" x="296" y="58" width="32" height="28" rx="4"></rect>
        <rect class="box" x="332" y="58" width="32" height="28" rx="4"></rect>
        <text class="s" x="230" y="77">值</text>
        <text class="s" x="266" y="77">值</text>
        <text class="s" x="220" y="112">还有空位，发送不阻塞。</text>
        <text class="s" x="220" y="132">四个都满，发送才挂起。</text>
        <text class="s" x="220" y="152">关闭后把这两格读完。</text>
        <text class="s" x="12" y="196">向已关闭的 channel 发送会 panic。close 只由发送方做一次。</text>
        <text class="s" x="12" y="216">select 里几个 case 同时就绪时随机选，书写顺序不是优先级。</text>
      `),
    },
    slice: {
      caption: "slice 只复制指针、长度和容量。容量还够时，append 写进同一块数组，另一个 slice 会看见被盖掉的元素。",
      svg: svg("slice", 400, 250, `
        <text class="b" x="16" y="24">底层数组</text>
        ${[0, 1, 2, 3, 4, 5].map((n) => `<rect class="box" x="${16 + n * 52}" y="36" width="46" height="32" rx="4"></rect><text class="t" x="${39 + n * 52}" y="57" text-anchor="middle">${n}</text>`).join("")}
        <rect class="soft" x="16" y="92" width="150" height="58" rx="8"></rect>
        <text class="b" x="28" y="112">A  len=3 cap=6</text>
        <text class="s" x="28" y="132">指针指向 0</text>
        <path class="arr" d="M40 92 V76"></path>
        <rect class="hot" x="210" y="92" width="160" height="58" rx="8"></rect>
        <text class="b" x="222" y="112">B  len=2 cap=4</text>
        <text class="s" x="222" y="132">指针指向 2</text>
        <path class="arr" d="M250 92 V76"></path>
        <text class="s" x="16" y="180">B 再 append 一个元素，长度还没超过容量，就会写到下标 4。</text>
        <text class="s" x="16" y="202">A 的容量覆盖到数组末尾，下标 4 也算在 A 能看见的范围里。</text>
        <text class="s" x="16" y="224">要切开，得拷到新数组。超过容量时 append 才会分配新数组。</text>
      `),
    },
    iface: {
      caption: "接口是类型和值两格。两格都空才是 nil。具体类型的 nil 指针放进来之后，类型那一格有字，err != nil 就是真。",
      svg: svg("iface", 400, 210, `
        <rect class="soft" x="16" y="20" width="170" height="120" rx="10"></rect>
        <text class="b" x="28" y="44">nil 接口</text>
        <rect class="box" x="32" y="60" width="138" height="26" rx="4"></rect>
        <text class="s" x="40" y="78">类型：空</text>
        <rect class="box" x="32" y="94" width="138" height="26" rx="4"></rect>
        <text class="s" x="40" y="112">值：空</text>
        <text class="b" x="28" y="154">err == nil</text>
        <rect class="hot" x="210" y="20" width="174" height="120" rx="10"></rect>
        <text class="b" x="222" y="44">装了 nil 指针</text>
        <rect class="box" x="226" y="60" width="142" height="26" rx="4"></rect>
        <text class="s" x="234" y="78">类型：*PathError</text>
        <rect class="box" x="226" y="94" width="142" height="26" rx="4"></rect>
        <text class="s" x="234" y="112">值：nil</text>
        <text class="b" x="222" y="154">err != nil</text>
        <text class="s" x="16" y="186">没有错误就直接 return nil，不要 return 一个声明了但还是 nil 的具体错误。</text>
      `),
    },
    hashmap: {
      caption: "桶下标是哈希和数组长度减一做与运算。一条链子太长且数组已经不小，这个桶会变成红黑树。扩容时节点只去原下标，或原下标加旧容量。",
      svg: svg("hashmap", 400, 250, `
        <text class="s" x="16" y="22">hash 高低位异或后，再 &amp; (n-1)</text>
        ${[0, 1, 2, 3].map((n) => `<rect class="box" x="${16 + n * 94}" y="36" width="84" height="28" rx="4"></rect><text class="t" x="${58 + n * 94}" y="55" text-anchor="middle">桶 ${n}</text>`).join("")}
        ${chip(34, 78, "k", 36)}${chip(34, 106, "k", 36)}
        <text class="s" x="78" y="93">拉链</text>
        <rect class="gold" x="204" y="76" width="84" height="70" rx="8"></rect>
        <text class="s" x="218" y="100">红黑树</text>
        <text class="s" x="218" y="120">链长 ≥ 8</text>
        <text class="s" x="218" y="138">且 n ≥ 64</text>
        <path class="arr" d="M250 64 V76"></path>
        <text class="s" x="16" y="176">扩容成两倍后，看哈希新的那一位：</text>
        <text class="s" x="16" y="198">0 → 留在原下标　　1 → 原下标 + 旧容量</text>
        <text class="s" x="16" y="220">JDK 8 用尾插，扩容不再把链表收成环。</text>
        <text class="s" x="16" y="240">多个线程同时 put 仍然会丢更新，尾插没有让它变成并发安全。</text>
      `),
    },
    tpool: {
      caption: "先占满核心线程，再进队列，队列满了才扩到最大线程，再满才拒绝。无界队列会让后面两步永远走不到。",
      svg: svg("tpool", 400, 250, `
        <rect class="gold" x="140" y="12" width="120" height="28" rx="8"></rect>
        <text class="b" x="200" y="31" text-anchor="middle">提交任务</text>
        <path class="arr" d="M200 40 V58"></path>
        <rect class="soft" x="70" y="62" width="260" height="32" rx="8"></rect>
        <text class="t" x="200" y="83" text-anchor="middle">核心线程没满？先开核心线程</text>
        <path class="arr" d="M200 94 V112"></path>
        <rect class="soft" x="70" y="116" width="260" height="32" rx="8"></rect>
        <text class="t" x="200" y="137" text-anchor="middle">队列还没满？任务进队列</text>
        <path class="arr" d="M200 148 V166"></path>
        <rect class="gold" x="70" y="170" width="260" height="32" rx="8"></rect>
        <text class="t" x="200" y="191" text-anchor="middle">线程数 &lt; 最大？再开线程</text>
        <path class="arr" d="M200 202 V218"></path>
        <rect class="hot" x="110" y="220" width="180" height="24" rx="8"></rect>
        <text class="b" x="200" y="237" text-anchor="middle">拒绝，或调用者自己跑</text>
      `),
    },
    aqs: {
      caption: "抢不到 state 的线程排进队列并 park。释放时改 state，再 unpark 后继。独占和共享的差别只在怎样改这个整数。",
      svg: svg("aqs", 400, 200, `
        <rect class="hot" x="16" y="24" width="110" height="64" rx="10"></rect>
        <text class="b" x="32" y="50">state</text>
        <text class="s" x="32" y="70">锁：重入次数</text>
        <path class="arr" d="M126 56 H156"></path>
        <rect class="box" x="160" y="20" width="70" height="36" rx="8"></rect>
        <text class="s" x="195" y="43" text-anchor="middle">头</text>
        <rect class="soft" x="240" y="20" width="70" height="36" rx="8"></rect>
        <text class="s" x="275" y="43" text-anchor="middle">等待</text>
        <rect class="gold" x="320" y="20" width="64" height="36" rx="8"></rect>
        <text class="s" x="352" y="43" text-anchor="middle">等待</text>
        <text class="s" x="160" y="78">拿不到就入队，然后 park</text>
        <text class="s" x="16" y="120">Semaphore 的 state 是剩余许可。CountDownLatch 的 state 是还没到的计数。</text>
        <text class="s" x="16" y="144">公平锁按队列来。非公平锁进队前先 CAS 抢一次，可能插队。</text>
        <text class="s" x="16" y="168">Latch 倒数到 0 就打开，不能重置。Barrier 到齐后可以再来一轮。</text>
      `),
    },
    g1: {
      caption: "G1 把堆切成同样大小的区域，优先收垃圾多的区域。停顿按区域切开。Full GC 是失败路径，不是正常的一拍。",
      svg: svg("g1", 400, 230, `
        ${Array.from({ length: 24 }, (_, i) => {
          const x = 16 + (i % 8) * 46;
          const y = 20 + Math.floor(i / 8) * 40;
          const cls = [2, 5, 11, 14, 20].includes(i) ? "hot" : [1, 7, 9, 18].includes(i) ? "gold" : "soft";
          return `<rect class="${cls}" x="${x}" y="${y}" width="40" height="32" rx="4"></rect>`;
        }).join("")}
        <text class="s" x="16" y="160">绿：还有不少活对象　　黄：年轻代　　红：垃圾多，优先收</text>
        <text class="s" x="16" y="184">目标是把大多数停顿控制在设定的上限附近，不是一次收完整堆。</text>
        <text class="s" x="16" y="208">ZGC 的停顿通常不随堆变大，代价是吞吐和运维。没有停顿数据不必换。</text>
      `),
    },
    btree: {
      caption: "联合索引按列从左到右排。能用上的是左端连续的等值，再加最多一个范围。只拿着 b 来查，这棵树用不上。",
      svg: svg("btree", 400, 240, `
        <text class="b" x="16" y="24">索引 (a, b, c)</text>
        <rect class="soft" x="16" y="40" width="368" height="36" rx="8"></rect>
        <text class="t" x="28" y="63">先按 a 分成几段</text>
        <rect class="gold" x="40" y="88" width="150" height="32" rx="8"></rect>
        <text class="t" x="52" y="109">a = 1 的这一段</text>
        <rect class="box" x="64" y="132" width="120" height="28" rx="6"></rect>
        <text class="s" x="74" y="151">再按 b，然后 c</text>
        <text class="s" x="16" y="184">WHERE a=1 AND b=2　　用得上</text>
        <text class="s" x="16" y="206">WHERE b=2　　左边没有 a，整段都用不上</text>
        <text class="s" x="16" y="228">WHERE a&gt;1 AND b=2　　a 已是范围，b 多半只能过滤</text>
      `),
    },
    mvcc: {
      caption: "普通读拿着 Read View 沿版本链找可见的那一版。当前读看最新已提交版本，并加锁挡住新插入的行。",
      svg: svg("mvcc", 400, 230, `
        <text class="b" x="16" y="24">同一行的版本链，新的在左</text>
        <rect class="hot" x="16" y="40" width="100" height="48" rx="8"></rect>
        <text class="s" x="28" y="60">trx 120</text>
        <text class="s" x="28" y="78">未提交</text>
        <rect class="soft" x="132" y="40" width="100" height="48" rx="8"></rect>
        <text class="s" x="144" y="60">trx 108</text>
        <text class="s" x="144" y="78">已提交</text>
        <rect class="box" x="248" y="40" width="100" height="48" rx="8"></rect>
        <text class="s" x="260" y="60">trx 90</text>
        <text class="s" x="260" y="78">更旧</text>
        <path class="arr" d="M116 64 H132"></path>
        <path class="arr" d="M232 64 H248"></path>
        <rect class="gold" x="16" y="108" width="368" height="44" rx="8"></rect>
        <text class="s" x="28" y="128">这次快照读的 Read View 看不见 120，看见 108</text>
        <text class="s" x="28" y="146">可重复读里，这个视图第一次读时定下，后面不换</text>
        <text class="s" x="16" y="180">提交读每次语句换一个新视图，所以能看见刚提交的行。</text>
        <text class="s" x="16" y="202">SELECT FOR UPDATE 是当前读，要锁，不是再看这个旧视图。</text>
        <text class="s" x="16" y="224">间隙锁防的是当前读的幻读，不是快照读。</text>
      `),
    },
    gap: {
      caption: "索引上已有 10、20、30。范围更新锁住记录，也锁住中间的空隙，别人就插不进 15。空隙和空隙不冲突，空隙和插入冲突。",
      svg: svg("gap", 400, 180, `
        <line x1="30" y1="70" x2="370" y2="70" stroke="#14352e" stroke-width="2"></line>
        ${[["10", 60], ["20", 190], ["30", 320]].map(([label, x]) => `<circle cx="${x}" cy="70" r="8" fill="#14352e"></circle><text class="b" x="${x}" y="100" text-anchor="middle">${label}</text>`).join("")}
        <rect class="hot" x="68" y="58" width="114" height="24" rx="6" opacity="0.85"></rect>
        <rect class="hot" x="198" y="58" width="114" height="24" rx="6" opacity="0.85"></rect>
        <text class="s" x="90" y="48">间隙，禁止插入</text>
        <text class="s" x="220" y="48">间隙，禁止插入</text>
        <text class="s" x="16" y="132">唯一索引等值而且记录存在时，通常只锁这一条，不必锁两边的间隙。</text>
        <text class="s" x="16" y="156">记录不存在时，要锁住它本该落下的那段空隙。</text>
      `),
    },
    deadlock: {
      caption: "A 拿着第 1 行去等第 2 行，B 拿着第 2 行去等第 1 行。检测之后回滚其中一笔，应用要从事务开头重试。",
      svg: svg("deadlock", 400, 200, `
        <rect class="soft" x="24" y="24" width="140" height="56" rx="10"></rect>
        <text class="b" x="94" y="48" text-anchor="middle">事务 A</text>
        <text class="s" x="94" y="68" text-anchor="middle">持有行 1</text>
        <rect class="gold" x="236" y="24" width="140" height="56" rx="10"></rect>
        <text class="b" x="306" y="48" text-anchor="middle">事务 B</text>
        <text class="s" x="306" y="68" text-anchor="middle">持有行 2</text>
        <path class="arr" d="M164 44 H236"></path>
        <text class="s" x="200" y="36" text-anchor="middle">等行 2</text>
        <path class="arr" d="M236 68 H164"></path>
        <text class="s" x="200" y="92" text-anchor="middle">等行 1</text>
        <text class="s" x="16" y="130">约定都按主键从小到大加锁，这个环就组不起来。</text>
        <text class="s" x="16" y="154">先查再插入的窗口，用唯一约束把第二次插入直接拒绝掉。</text>
        <text class="s" x="16" y="178">持锁期间不要发 RPC，锁会盖住整个等待。</text>
      `),
    },
    zset: {
      caption: "成员找分数走哈希，按分数取一段走跳表。GEO 只是把 52 位 geohash 填进这个分数，分数不是米。",
      svg: svg("zset", 400, 230, `
        <rect class="box" x="16" y="20" width="160" height="150" rx="10"></rect>
        <text class="b" x="28" y="44">哈希</text>
        <text class="s" x="28" y="70">用户 7 → 分数</text>
        <text class="s" x="28" y="94">用户 2 → 分数</text>
        <text class="s" x="28" y="118">店铺 9 → 分数</text>
        <text class="s" x="28" y="148">按成员查，均摊 O(1)</text>
        <rect class="soft" x="196" y="20" width="188" height="150" rx="10"></rect>
        <text class="b" x="208" y="44">跳表，按分数有序</text>
        <text class="s" x="208" y="72">— — — — — →</text>
        <text class="s" x="208" y="96">— — →</text>
        <text class="s" x="208" y="120">→ 下一段</text>
        <text class="s" x="208" y="148">取 M 个是 O(log N+M)</text>
        <text class="s" x="16" y="196">一个 zset 装全国，范围扫描会堵住这台 Redis 的那条执行线程。</text>
        <text class="s" x="16" y="218">按城市或格子拆开。GEO 的距离还要拿经纬度再算，不能减分数。</text>
      `),
    },
    cache: {
      caption: "订单以数据库为准：先提交数据库，再删缓存。下一次读未命中再回源。先改缓存再改库，慢的旧读会把旧值写回去。",
      svg: svg("cache", 400, 220, `
        <rect class="soft" x="24" y="36" width="100" height="40" rx="8"></rect>
        <text class="b" x="74" y="61" text-anchor="middle">改数据库</text>
        <path class="arr" d="M124 56 H156"></path>
        <rect class="hot" x="160" y="36" width="100" height="40" rx="8"></rect>
        <text class="b" x="210" y="61" text-anchor="middle">删缓存</text>
        <path class="arr" d="M260 56 H292"></path>
        <rect class="gold" x="296" y="36" width="80" height="40" rx="8"></rect>
        <text class="b" x="336" y="61" text-anchor="middle">下次读</text>
        <text class="s" x="16" y="110">删除失败要重试，或靠 binlog 再删一次。只删一次失败，旧值会留到 TTL。</text>
        <text class="s" x="16" y="136">强一致的读走主库，不走缓存。</text>
        <text class="s" x="16" y="162">最新位置如果允许旧几秒，缓存可以是在线事实来源，不要套这个顺序。</text>
        <text class="s" x="16" y="188">空值也缓存很短的时间，用来挡穿透。位置的空不能缓存太久。</text>
      `),
    },
    kafka: {
      caption: "同一个用户的点用用户 id 做键，进同一个分区，分区里有序。全局并不有序。处理完再提交位移，崩溃会重投，所以消费要幂等。",
      svg: svg("kafka", 400, 220, `
        <text class="s" x="16" y="24">键 = 用户 id</text>
        <rect class="box" x="16" y="40" width="110" height="120" rx="10"></rect>
        <text class="b" x="28" y="62">分区 0</text>
        <text class="s" x="28" y="86">用户A · 点1</text>
        <text class="s" x="28" y="106">用户A · 点2</text>
        <text class="s" x="28" y="126">用户A · 点3</text>
        <text class="s" x="28" y="146">顺序固定</text>
        <rect class="box" x="146" y="40" width="110" height="120" rx="10"></rect>
        <text class="b" x="158" y="62">分区 1</text>
        <text class="s" x="158" y="86">用户B · 点1</text>
        <text class="s" x="158" y="106">用户C · 点1</text>
        <rect class="soft" x="276" y="40" width="108" height="120" rx="10"></rect>
        <text class="b" x="288" y="62">消费组</text>
        <text class="s" x="288" y="88">一个分区</text>
        <text class="s" x="288" y="108">同时只给</text>
        <text class="s" x="288" y="128">一个消费者</text>
        <text class="s" x="16" y="184">所有用户挤进一个分区，顺序有了，吞吐没了。</text>
        <text class="s" x="16" y="206">提交太早会丢，提交太晚会重复。用行程和序号做幂等键。</text>
      `),
    },
    bucket: {
      caption: "漏桶出水速度恒定，突发只能排队。令牌桶里有存量，短突发可以一次通过，存量用完就回到稳定速率。",
      svg: svg("bucket", 400, 230, `
        <rect class="box" x="40" y="40" width="100" height="120" rx="8"></rect>
        <rect class="soft" x="48" y="90" width="84" height="62" rx="4"></rect>
        <text class="b" x="90" y="28" text-anchor="middle">漏桶</text>
        <text class="s" x="90" y="78" text-anchor="middle">请求在等</text>
        <path class="arr" d="M90 160 V190"></path>
        <text class="s" x="90" y="208" text-anchor="middle">固定速率流出</text>
        <rect class="box" x="250" y="40" width="100" height="120" rx="8"></rect>
        <rect class="gold" x="258" y="70" width="84" height="82" rx="4"></rect>
        <text class="b" x="300" y="28" text-anchor="middle">令牌桶</text>
        ${chip(268, 84, "●", 22)}${chip(296, 84, "●", 22)}${chip(268, 112, "●", 22)}
        <text class="s" x="300" y="208" text-anchor="middle">有存量就能突发</text>
        <text class="s" x="16" y="224">固定窗口会在整点两侧各放满一次。滑动窗口看的是最近一段时间。</text>
      `),
    },
    tcp: {
      caption: "三次是为了对齐双方的初始序号，并确认这次不是一个迟到的旧 SYN。少一次，服务端可能为一个不会再有数据的旧请求分配资源。",
      svg: svg("tcp", 400, 230, `
        <text class="b" x="70" y="24" text-anchor="middle">客户端</text>
        <text class="b" x="320" y="24" text-anchor="middle">服务端</text>
        <line x1="70" y1="32" x2="70" y2="200" stroke="#14352e" stroke-width="1.4"></line>
        <line x1="320" y1="32" x2="320" y2="200" stroke="#14352e" stroke-width="1.4"></line>
        <path class="arr" d="M70 56 H320"></path>
        <text class="s" x="195" y="48" text-anchor="middle">1 SYN，我的序号</text>
        <path class="arr" d="M320 104 H70"></path>
        <text class="s" x="195" y="96" text-anchor="middle">2 SYN+ACK，我的序号</text>
        <path class="arr" d="M70 156 H320"></path>
        <text class="s" x="195" y="148" text-anchor="middle">3 ACK，确认你的序号</text>
        <text class="s" x="16" y="220">挥手通常四次，因为每一端要单独关掉自己的发送方向。</text>
      `),
    },
    lsm: {
      caption: "写入先落日志和内存表，再整块刷成不再修改的有序文件。删除先写成墓碑，空间要等合并才还回来。在线最新位置不要来这里点查。",
      svg: svg("lsm", 400, 230, `
        <rect class="gold" x="16" y="20" width="90" height="40" rx="8"></rect>
        <text class="b" x="61" y="45" text-anchor="middle">写入</text>
        <path class="arr" d="M106 40 H130"></path>
        <rect class="soft" x="134" y="16" width="110" height="48" rx="8"></rect>
        <text class="s" x="189" y="36" text-anchor="middle">日志</text>
        <text class="s" x="189" y="54" text-anchor="middle">内存表</text>
        <path class="arr" d="M244 40 H268"></path>
        <rect class="box" x="272" y="16" width="110" height="48" rx="8"></rect>
        <text class="s" x="327" y="45" text-anchor="middle">有序文件</text>
        <text class="s" x="16" y="96">文件写好就不再改。更新是写一条新记录，删除是写墓碑。</text>
        <text class="s" x="16" y="120">读的时候从新到旧看内存表和各层文件，布隆过滤器跳过不可能的文件。</text>
        <text class="s" x="16" y="144">键按用户和时间排，一段轨迹才能顺序读出来。</text>
        <text class="s" x="16" y="168">合并跟不上时，读放大和占的磁盘一起涨。</text>
        <text class="s" x="16" y="196">最新位置放内存索引。这里只放追加的冷轨迹。</text>
      `),
    },
    rowcol: {
      caption: "按行存放时，沿着行走是下一步就在旁边。按列走每次跳过一整行。复杂度一样，缓存行不一样。",
      svg: svg("rowcol", 400, 220, `
        ${Array.from({ length: 16 }, (_, i) => {
          const x = 20 + (i % 4) * 36;
          const y = 36 + Math.floor(i / 4) * 28;
          return `<rect class="soft" x="${x}" y="${y}" width="30" height="22" rx="3"></rect>`;
        }).join("")}
        <path class="arr" d="M36 47 H150"></path>
        <text class="b" x="180" y="52">按行：下一块就在缓存行里</text>
        ${Array.from({ length: 16 }, (_, i) => {
          const x = 20 + (i % 4) * 36;
          const y = 150;
          return "";
        }).join("")}
        <text class="s" x="16" y="160">按列：下一步要跳过一整行的字节，预取也猜不中。</text>
        <text class="s" x="16" y="184">这不是 O(n²) 变成了别的复杂度，是内存带宽和缓存。</text>
        <text class="s" x="16" y="208">列优先存储的数组，结论反过来。先确认布局再交换循环。</text>
      `),
    },
    geohash: {
      caption: "经度和纬度轮流二分，偶数步取经度，每 5 位变成一个 base32 字符。半径查询要带上八个邻居，因为曲线在格子边界上会跳。",
      svg: svg("geohash", 400, 292, `
        <text class="b" x="16" y="28">比特交错</text>
        <text class="s" x="16" y="54">经度 1 0 1 1 …</text>
        <text class="s" x="16" y="76">纬度 0 1 1 0 …</text>
        <text class="s" x="16" y="98">每 5 位一个字符</text>
        ${Array.from({ length: 9 }, (_, i) => {
          const col = i % 3;
          const row = Math.floor(i / 3);
          const x = 214 + col * 56;
          const y = 16 + row * 46;
          const cls = i === 4 ? "hot" : "box";
          const label = i === 4 ? "点" : "邻";
          return `<rect class="${cls}" x="${x}" y="${y}" width="50" height="40" rx="4"></rect><text class="s" x="${x + 25}" y="${y + 25}" text-anchor="middle">${label}</text>`;
        }).join("")}
        <text class="s" x="16" y="186">只查中心格，贴边的更近点会落在邻居里。</text>
        <text class="s" x="16" y="208">邻居要按格子坐标偏移，不能对字符串加一。</text>
        <text class="s" x="16" y="230">九格结果还要用真实距离过滤。</text>
        <text class="s" x="16" y="252">位数越大格子越小。纬度越高，同样位数越窄。</text>
        <text class="s" x="16" y="274">字符串接近，不等于地理上接近。</text>
      `),
    },
    nine: {
      caption: "查询点贴在格子右下角时，真正更近的人在右下邻居里。只读中心格就会漏。九格结果再按距离删掉圆外的点。",
      svg: svg("nine", 400, 230, `
        ${Array.from({ length: 9 }, (_, i) => {
          const x = 40 + (i % 3) * 70;
          const y = 20 + Math.floor(i / 3) * 58;
          return `<rect class="${i === 4 ? "gold" : "box"}" x="${x}" y="${y}" width="64" height="52" rx="6"></rect>`;
        }).join("")}
        <circle cx="166" cy="118" r="5" fill="#c6452f"></circle>
        <circle cx="214" cy="156" r="5" fill="#14352e"></circle>
        <text class="s" x="250" y="50">中心格</text>
        <text class="s" x="250" y="120">查询点贴边</text>
        <text class="s" x="250" y="160">更近的点在邻居</text>
        <text class="s" x="16" y="210">半径比格子大很多时，一圈九格不够，要扩大圈数或换更粗的精度。</text>
      `),
    },
    ray: {
      caption: "从点向右画一条射线，和多边形边相交的次数是奇数就在内部。这是精确判断，只能对倒排收出来的少量围栏做。",
      svg: svg("ray", 400, 220, `
        <polygon points="40,40 150,30 180,110 120,170 30,120" fill="#e7f3ea" stroke="#14352e" stroke-width="1.6"></polygon>
        <circle cx="90" cy="100" r="5" fill="#c6452f"></circle>
        <line x1="90" y1="100" x2="360" y2="100" stroke="#c6452f" stroke-width="1.4" stroke-dasharray="4 3"></line>
        <circle cx="168" cy="100" r="4" fill="#a97820"></circle>
        <text class="s" x="200" y="92">穿过 1 次，奇数，在里面</text>
        <polygon points="40,180 90,150 150,190 70,200" fill="none" stroke="#14352e" stroke-width="1.4"></polygon>
        <text class="s" x="170" y="180">边界上的点用滞回，不要一次进出就算一次事件。</text>
        <text class="s" x="16" y="214">先用格子倒排拿候选，再用外包矩形丢掉一批，最后才数交点。</text>
      `),
    },
    hmm: {
      caption: "每个点有几条候选路。发射概率看离投影点有多远，转移概率看路网距离和两点直线距离是否说得通。Viterbi 取整条最像的路径，而不是每个点单独选最近的路。",
      svg: svg("hmm", 400, 220, `
        <path d="M20 150 C 80 150, 100 60, 180 70 S 300 160, 380 80" fill="none" stroke="#14352e" stroke-width="3"></path>
        <path d="M20 90 C 90 40, 140 40, 200 90 S 320 40, 380 120" fill="none" stroke="#a97820" stroke-width="2"></path>
        <circle cx="80" cy="78" r="5" fill="#c6452f"></circle>
        <circle cx="180" cy="96" r="5" fill="#c6452f"></circle>
        <circle cx="280" cy="70" r="5" fill="#c6452f"></circle>
        <text class="s" x="16" y="24">红点是 GPS。绿线是真路，黄线是平行的干扰路。</text>
        <text class="s" x="16" y="176">每个点单独吸到最近的路，会在两条平行路之间来回跳。</text>
        <text class="s" x="16" y="198">在线只用一个滑动窗口，窗口末端再输出已经稳定的前缀。</text>
      `),
    },
    decay: {
      caption: "σ 小，分数掉得快，适合咖啡这种近距离。σ 大，远处还留着分，适合景区。超过配送范围应该直接丢掉，而不是乘一个很小数。",
      svg: svg("decay", 400, 220, `
        <line x1="40" y1="180" x2="360" y2="180" stroke="#14352e" stroke-width="1.4"></line>
        <line x1="40" y1="20" x2="40" y2="180" stroke="#14352e" stroke-width="1.4"></line>
        <text class="s" x="300" y="198">距离</text>
        <text class="s" x="8" y="30">分</text>
        <path d="M40 30 C 80 30, 90 170, 160 175" fill="none" stroke="#c6452f" stroke-width="2"></path>
        <path d="M40 30 C 140 30, 180 150, 300 170" fill="none" stroke="#1d4a3e" stroke-width="2"></path>
        <text class="s" x="150" y="70">红：σ 小，咖啡</text>
        <text class="s" x="180" y="110">绿：σ 大，景区</text>
        <text class="s" x="16" y="214">配送看的是 ETA 能不能赶上承诺，不是这条直线距离曲线。</text>
      `),
    },
    recall: {
      caption: "每路召回有自己的配额，再交给排序。先在全库做向量近邻再滤城市，名额会被外地的相似店占满。",
      svg: svg("recall", 400, 230, `
        <rect class="soft" x="16" y="16" width="110" height="32" rx="6"></rect>
        <text class="s" x="71" y="37" text-anchor="middle">空间 · 配额</text>
        <rect class="gold" x="16" y="56" width="110" height="32" rx="6"></rect>
        <text class="s" x="71" y="77" text-anchor="middle">行为 · 配额</text>
        <rect class="box" x="16" y="96" width="110" height="32" rx="6"></rect>
        <text class="s" x="71" y="117" text-anchor="middle">热门 · 保底</text>
        <rect class="hot" x="16" y="136" width="110" height="32" rx="6"></rect>
        <text class="s" x="71" y="157" text-anchor="middle">新品 · 配额</text>
        <path class="arr" d="M126 32 H160"></path>
        <path class="arr" d="M126 72 H160"></path>
        <path class="arr" d="M126 112 H160"></path>
        <path class="arr" d="M126 152 H160"></path>
        <rect class="soft" x="164" y="56" width="90" height="72" rx="8"></rect>
        <text class="b" x="209" y="96" text-anchor="middle">排序</text>
        <text class="s" x="270" y="40">先全库 ANN</text>
        <text class="s" x="270" y="60">再滤城市</text>
        <text class="s" x="270" y="88">远方相似店</text>
        <text class="s" x="270" y="108">把名额占满</text>
        <text class="s" x="16" y="190">召回看覆盖和召回率。AUC 是排序阶段的指标。</text>
        <text class="s" x="16" y="214">新城市没有行为时，加大空间和热门，把个性化权重降下来。</text>
      `),
    },
    esmm: {
      caption: "转化如果只在点击样本上训练，线上却要对全部曝光打分。ESMM 学点击率，以及点击后的转化，两者相乘才是从曝光到转化。",
      svg: svg("esmm", 400, 200, `
        <rect class="box" x="16" y="70" width="80" height="40" rx="8"></rect>
        <text class="s" x="56" y="95" text-anchor="middle">曝光</text>
        <path class="arr" d="M96 80 H130"></path>
        <path class="arr" d="M96 100 H130"></path>
        <rect class="soft" x="134" y="24" width="100" height="40" rx="8"></rect>
        <text class="s" x="184" y="49" text-anchor="middle">点击率 pCTR</text>
        <rect class="gold" x="134" y="110" width="120" height="40" rx="8"></rect>
        <text class="s" x="194" y="135" text-anchor="middle">点击后转化 pCVR</text>
        <text class="b" x="270" y="90">×</text>
        <rect class="hot" x="296" y="64" width="88" height="44" rx="8"></rect>
        <text class="s" x="340" y="82" text-anchor="middle">全空间</text>
        <text class="s" x="340" y="100" text-anchor="middle">转化率</text>
        <text class="s" x="16" y="176">没点击的样本不能直接当成转化的负样本，也不能只在点击里训练再拿去给曝光排序。</text>
      `),
    },
    inverted: {
      caption: "倒排是从词找到文档列表。两个词的查询先各自取出列表再求交。短语还要看词在文档里的位置。相关度分不是距离。",
      svg: svg("inverted", 400, 210, `
        <rect class="soft" x="16" y="24" width="80" height="32" rx="6"></rect>
        <text class="s" x="56" y="45" text-anchor="middle">咖啡</text>
        <text class="s" x="110" y="45">→ 店 1、店 4、店 9</text>
        <rect class="gold" x="16" y="70" width="80" height="32" rx="6"></rect>
        <text class="s" x="56" y="91" text-anchor="middle">川菜</text>
        <text class="s" x="110" y="91">→ 店 4、店 7</text>
        <rect class="hot" x="16" y="120" width="200" height="32" rx="6"></rect>
        <text class="b" x="116" y="141" text-anchor="middle">交集：店 4</text>
        <text class="s" x="16" y="176">text 会分词再进这张表。keyword 整串当成一个精确值，用来过滤和聚合。</text>
        <text class="s" x="16" y="198">地理范围放进 filter，不要指望这个相关度分代表更近。</text>
      `),
    },
    geo: {
      caption: "经纬度先编成 52 位 geohash，再放进有序集合的分数。读回来的是格子中心，和原始点差一个格子。计费要用原始坐标再算。",
      svg: svg("geo", 400, 200, `
        <rect class="box" x="16" y="24" width="100" height="44" rx="8"></rect>
        <text class="s" x="66" y="50" text-anchor="middle">经度, 纬度</text>
        <path class="arr" d="M116 46 H146"></path>
        <rect class="gold" x="150" y="24" width="100" height="44" rx="8"></rect>
        <text class="s" x="200" y="50" text-anchor="middle">52 位</text>
        <path class="arr" d="M250 46 H280"></path>
        <rect class="soft" x="284" y="24" width="100" height="44" rx="8"></rect>
        <text class="s" x="334" y="50" text-anchor="middle">zset 分数</text>
        <text class="s" x="16" y="100">双精度能精确放下 52 位整数，所以分数不会把编码再四舍五入坏。</text>
        <text class="s" x="16" y="124">GEOPOS 解码的是格子中心，不能当原始 GPS 存档。</text>
        <text class="s" x="16" y="148">距离误差大约 0.5%，展示可以，计费不行。</text>
        <text class="s" x="16" y="172">纬度只到大约 ±85 度。成员没有单独的过期时间。</text>
      `),
    },
  };
})();
