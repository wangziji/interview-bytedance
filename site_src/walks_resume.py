RESUME_WALKS = {}

def _add(key, title, lang, intro, steps):
    RESUME_WALKS[key] = [{"title": title, "lang": lang, "intro": intro, "steps": steps}]

_add("resume/guess-dest", "请求进来之后的四步", "Python", "白板先写这四步，数字放在实验那一步之后。", [
    {"code": "def predict(req):\n    ctx = build_context(req.user, req.lat, req.lng, req.ts)", "say": "上下文只用请求时刻之前的状态。这里的 ts 是事件时间。用服务器处理时间，补报和回放会对不齐。"},
    {"code": "    cands = recall(ctx)          # 历史目的地 + 周边 + 兜底\n    feats = features(ctx, cands, as_of=req.ts)", "say": "先召回再拼特征。as_of 把特征截止死。候选如果是全城 POI，Recall@1 的 68% 和只有十几个历史点完全不是一个难度，你要说出当时的候选规模。"},
    {"code": "    scores = model.forward(feats)\n    top = cands[argmax(scores)]", "say": "简历里的产品是给出目的地，所以在线取第一名。如果当时展示的是列表，CTR 和 Recall@1 就要分开讲，不能用同一个头。"},
    {"code": "    log_experiment(req.bucket, model.version, top.id)\n    return top", "say": "实验日志带着分桶和模型版本。三轮迭代的 10 个点，要能指回某一版 version 的对照，而不是三轮混在一个总数里。"},
])

_add("resume/features", "同一套截止时间", "Python", "泄漏通常出在 join 的时间条件，不出现在模型结构。", [
    {"code": "def features(ctx, cand, as_of):\n    hist = trips.before(ctx.user, as_of)", "say": "只取 as_of 之前结束的行程。如果用行程开始时间，进行中的单会把目的地漏进特征。"},
    {"code": "    home = stay_cell(hist, night=True)\n    dist = haversine_m(ctx.lat, ctx.lng, cand.lat, cand.lng)", "say": "常驻地用夜间停留的格子，和线上一致。距离用请求里的定位，定位缺失就不要填 0。"},
    {"code": "    return {\n        \"seen\": cand.id in hist.destinations,\n        \"dist_m\": dist,\n        \"hour\": hour(as_of),\n        \"missing_loc\": ctx.lat is None,\n    }", "say": "是否去过、距离、小时、定位是否缺失，分开给模型。缺失用布尔，不用距离 0。面试官问重要度时，你要能说这几类里谁在前，以及你怎么排除泄漏。"},
])

_add("resume/trpc", "业务只填配置", "Go", "复用的是这四段，不是目的地规则。", [
    {"code": "type Predictor interface {\n    Recall(ctx context.Context, req *Request) ([]Candidate, error)\n    Score(ctx context.Context, feats []Feature) ([]float32, error)\n}", "say": "接口只留召回和打分。脚手架负责超时、限流、打点和协议。第二个业务接入时实现这两个方法，而不是复制一份服务。"},
    {"code": "ctx, cancel := context.WithTimeout(ctx, 40*time.Millisecond)\ndefer cancel()\nfeats, err := featClient.Fetch(ctx, req)", "say": "特征超时单独 40 毫秒，不要和模型前向共用一个 200 毫秒。特征失败要决定是降级召回还是整请求失败，这个决定要提前写进脚手架。"},
    {"code": "model, err := registry.Current(req.Exp)\nif err != nil {\n    model = registry.Stable()\n}", "say": "实验版本挂了就回稳定版。热更新换的是 registry 里的指针，不重启进程。4 个项目共用 registry 的协议，模型文件各自一份。"},
])

_add("resume/ddp", "把 1 分钟拆开", "Python", "面试官要的是瓶颈，不是 DDP 这个单词。", [
    {"code": "model = DDP(model, device_ids=[local_rank])\nscaler = GradScaler()", "say": "4 张卡各一个进程。GradScaler 说明当时用了混合精度。如果实际是 bf16 或 fp32，这里改成你的精度，不要背成 fp16。"},
    {"code": "for batch in loader:\n    loss = model(batch)\n    scaler.scale(loss).backward()\n    scaler.step(opt)", "say": "一个 epoch 1 分钟，取决于 global batch 和 6G 样本里一条样本有多大。6G 若是压缩特征，计算可能很轻，时间会花在 DataLoader。你要准备当时的 batch 和 worker 数。"},
    {"code": "sampler = DistributedSampler(dataset, shuffle=True)\nsampler.set_epoch(epoch)", "say": "每个 rank 看不同切片。set_epoch 让每轮 shuffle 不同。验证集如果也用这个采样，指标会对不齐，验证应该固定一份、不参与切分。"},
])

_add("resume/metrics-dest", "先写口径再写数字", "Python", "防止把 pp、候选集和曝光混在一句里。", [
    {"code": "recall_at_1 = mean(rank[true_dest] == 1 for s in sessions)", "say": "分母是有真实下一目的地、并且它在候选集里的请求。不在候选集里的请求不能算进 68%，否则数字被候选召回率污染。"},
    {"code": "ctr = clicks / impressions\nlift_pp = (ctr_new - ctr_old) * 100", "say": "10pp 是两个点击率相减再乘 100。如果实验报告里写的是相对提升 10%，口误会差一截。40% 以上是绝对值。曝光是否包含未渲染，要和报表一致。"},
    {"code": "compare(bucket == \"exp\", bucket == \"ctrl\", same_slot=True)", "say": "对照必须是同一展示位。位置或样式变了，CTR 涨 10 个点不能算模型。竞品对照同样要同一入口。"},
])

_add("resume/bert-intent", "宏平均和按类阈值", "Python", "0.88 要落到最小的那个类。", [
    {"code": "logits = bert(query)\npred = argmax(logits)", "say": "BERT 编码整句 query。类别是酒店意图，不是开放域闲聊。超短 query 和空 query 在进模型前就要有规则，否则宏平均会被垃圾流量拉低。"},
    {"code": "f1_macro = mean(f1(class_) for class_ in classes)", "say": "宏平均对每一类等权。你要能说类别数，以及最差一类的 F1，而不是只记 0.88。微平均会被『找酒店』这种大类主导。"},
    {"code": "if confidence[pred] < threshold[pred]:\n    pred = \"unknown\"", "say": "每类一个阈值。不确定就交给兜底召回，不要硬走进品牌或价格意图。坏例表比总分更能挡住追问。"},
])

_add("resume/hotel-rank", "召回配额和精排分工", "Python", "GAUC +20pp 和线上 +6pp 可以同时为真，但你要解释差距。", [
    {"code": "cands = []\nfor layer, quota in [(\"text\", 80), (\"geo\", 80), (\"hot\", 20)]:\n    cands += es.search(layer, quota)", "say": "ES 分层召回，每层配额。地理和文本不要先做全库相关再过滤。热门只占兜底配额，避免吃掉个性化。"},
    {"code": "wide = [dist, price, brand_match]\ndeep = mlp(cross(user, hotel))\nscore = wide_linear(wide) + deep", "say": "Wide 放距离、价格、是否命中品牌，面试官能听懂。Deep 吃交叉。ES 的文本分可以当 Wide 的一列，不要替代整个模型。"},
    {"code": "offline = gauc(scores, group=session)\nonline = clicks / impressions", "say": "GAUC 按会话分组。提升 20 个点要说出对照是规则还是上一版模型。线上会话点击率 33%、提升 6 个点，是曝光后的行为。两者差距来自离线候选和真实曝光不同，主动讲这句。"},
])

_add("resume/subsidy", "估计增量而不是估计会买", "Python", "ROI +15pp 的分母是补贴成本。", [
    {"code": "uplift = lgbm.predict(features)   # 给补贴 vs 不给的差\ncost = amount(uplift)", "say": "模型输出的是增量，不是下单概率。人工策略是对照。如果当时模型直接预测转化，你就不要把它说成 uplift，面试会被拆穿。"},
    {"code": "roi = incremental_profit / subsidy_cost\nlift_pp = (roi_model - roi_manual) * 100", "say": "15 个百分点是两个 ROI 相减。利润还是 GMV，必须和财务口径一致。不补贴也会买的订单进了分子，ROI 会被高估。"},
    {"code": "if random() < explore:\n    amount = random_arm()", "say": "没有探索就无法知道增量。探索比例和有没有排除羊毛，是这题的第二层。节假日要单独看，不能和日常混成 15 个点。"},
])

_add("resume/agent-arch", "流式、工具、卡片三截", "Go", "断线重连不能把写操作做两次。", [
    {"code": "func Stream(w http.ResponseWriter, events <-chan Event) {\n    w.Header().Set(\"Content-Type\", \"text/event-stream\")\n    for ev := range events {\n        fmt.Fprintf(w, \"id: %s\\ndata: %s\\n\\n\", ev.ID, ev.JSON)\n        flusher.Flush()\n    }\n}", "say": "SSE 每一条带 id。小程序断线用 Last-Event-ID 续上。AGUI 吃的是 data 里的卡片 JSON，不是把正文再解析一遍。"},
    {"code": "type Agent interface {\n    Tools() []Tool\n    OnEvent(ctx context.Context, in Event) ([]Event, error)\n}", "say": "A2A 里每个代理只暴露自己的工具和事件处理。选单代理不能调用下单工具。这样两个代理不会各写各的订单。"},
    {"code": "if tool.Mutates() {\n    if !confirmed(draftID) {\n        return waitCard(draftID)\n    }\n    return tool.Run(idempotencyKey)\n}", "say": "写操作先出确认卡片。幂等键用草稿 id。重连如果再跑一遍工具，第二次要被幂等键挡住。开发周期缩短，是因为这段不用每个业务重写。"},
])

_add("resume/prompt-platform", "版本号跟着请求走", "Python", "热更新没有版本，就无法复现坏案例。", [
    {"code": "def load(name, env):\n    if env == \"test\":\n        return drafts.get(name)\n    return online.get(name)   # 已审批", "say": "测试环境读草稿，线上只读审批过的版本。两条存储不要混。私有化客户若不能拉线上配置，就要把已审批版本打进发布包。"},
    {"code": "ver = stable\nif user_in_gray(uid, 5):\n    ver = candidate\nprompt = registry[name][ver]\nlog(request_id, name, ver)", "say": "5% 流量用候选。日志写请求 id 和版本。回滚是把 candidate 指针指回上一版，不发客户端。灰度指标用任务成功率和工具失败率。"},
])

_add("resume/sft-order", "可用先于像不像", "Python", "90% 可用率和 0.95 的 F1 不是同一个数。", [
    {"code": "text = model.generate(prompt, max_new_tokens=128)\nchoice = parse(text)\nok = choice in candidate_ids", "say": "可用率是解析成功且选项在候选集合里。基线提升 44 个百分点后到 90% 以上。解析失败算不可用，不能算业务转化。"},
    {"code": "f1 = f1_score(y_true, choice)  # > 0.95", "say": "F1 比较的是和标注选中的那一项是否一致。你要说正样本是『选对了标注项』。类别如果极不平衡，只报 F1 不够，准备按场景拆开。"},
    {"code": "t0 = time()\nout = infer(req)          # 排队 + 前向 + 解析\nobserve(time() - t0)      # P50 < 1.8s, P95 < 3.7s", "say": "简历写的是完整推理。如果 1.8 秒不含排队，现场会和监控对不上。用户如果要等全文结束才看到卡片，就要补一句首 token 时间；如果是流式中途出卡片，P50 应该指卡片出现。"},
])

_add("resume/gateway-crypto", "握手和数据包分开测", "Go", "98% 的耗时下降必须说清比的是哪一段。", [
    {"code": "shared := x25519(clientEphemeral, serverPublic)\nkey := hkdf(shared, dayID)\ncipher := chacha20poly1305(key)", "say": "Curve25519 做一次协商，数据用对称加密。和 RSA 比的是这段握手加每包加密，不是业务逻辑。天级密钥用 dayID 混进 HKDF，轮换时新旧 dayID 要有重叠窗口。"},
    {"code": "// 压测记录三列：明文 / RSA / X25519\n// 峰值 RPS：X25519 与明文持平\n// 相对 RSA：RPS +67%，CPU -22.3pp，平均耗时 -98%", "say": "峰值和明文一样，说明瓶颈已经不在密码。耗时下降 98% 只在你测量的那一段成立，不要说成整个接口快 50 倍。内存降低简历写的是 4.51，单位面试前核对，不要在现场猜成百分点或 MB。"},
    {"code": "// 4C8G，CPU 40%，650 QPS", "say": "这是单机压测点，不是线上全天均值。说明是单接口还是整网关，连接是否复用。CPU 只有 40%，可能还没打满，面试官会问为什么不再加压。"},
])

_add("resume/auto-map", "只讲你拍板的两件事", "口述", "亿级收入是结果，不是你的技术方案。", [
    {"code": "性能：掉帧 -> 抓某一帧的渲染或数据耗时 -> 你改的那条路径\n需求：客户 A 和排期冲突 -> 你砍掉或改期的功能 -> 理由", "say": "两件都要有你的决定。车机内存和启动与手机不是同一约束，架构图上把车机进程和地图渲染分开讲。量产分支和主干怎么合，是第三问，提前想好。"},
])

_add("resume/pano", "增长和客户端指标分开", "Android", "6 倍日活不要揽到自己头上。", [
    {"code": "进入成功率、首帧耗时、崩溃率、瓦片缓存命中", "say": "你能负责的是这四个客户端指标。日活从 150 万到 900 万如果对不齐你的版本，就说明主要是入口和运营。直接说清楚。"},
    {"code": "funnel: 曝光入口 -> 点击 -> 首帧 -> 停留", "say": "如果某次发布让进入成功率上去，并且入口因此被放到主路径，这段因果可以讲。没有漏斗就不要把 900 万说成优化结果。"},
])
