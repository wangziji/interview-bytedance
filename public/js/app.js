(function () {
  const SITE = window.SITE;
  const view = document.querySelector("#view");
  const nav = document.querySelector("#nav");
  const meter = document.querySelector("#meter");
  const search = document.querySelector("#search");
  const searchPanel = document.querySelector("#searchPanel");
  const sider = document.querySelector("#sider");
  const scrim = document.querySelector("#scrim");
  const KEY = "geodian-mastered-v1";
  const LANG_KEY = "geodian-lang";
  let timerId = null;

  const tracks = Object.fromEntries(SITE.tracks.map((track) => [track.id, track]));
  const problems = Object.fromEntries(SITE.problems.map((problem) => [problem.id, problem]));
  const designs = Object.fromEntries(SITE.designs.map((design) => [design.id, design]));

  const NAV = [
    ["开始", [["/", "总览"], ["/plan", "七日"], ["/lab", "实验室"]]],
    ["领域", SITE.tracks.map((track) => [`/track/${track.id}`, track.title])],
    ["手写", [["/problems", "算法题"]]],
    ["系统设计", [["/designs", "四道口述"], ["/project", "项目深挖"], ["/quiz", "自测"]]],
  ];

  function mastered() {
    try {
      return new Set(JSON.parse(localStorage.getItem(KEY) || "[]"));
    } catch (err) {
      return new Set();
    }
  }

  function setMastered(set) {
    localStorage.setItem(KEY, JSON.stringify([...set]));
    renderMeter();
    renderNav(navTarget(currentParts()));
  }

  function currentParts() {
    return (location.hash.replace(/^#/, "") || "/").split("/").filter(Boolean);
  }

  function countDone(ids) {
    const set = mastered();
    return ids.reduce((sum, id) => sum + (set.has(id) ? 1 : 0), 0);
  }

  function progressForHref(href) {
    if (href.startsWith("/track/")) {
      const track = tracks[href.slice("/track/".length)];
      if (!track) return null;
      const ids = track.cards.map((card) => card.id);
      return { done: countDone(ids), total: ids.length };
    }
    if (href === "/problems") {
      const ids = SITE.problems.map((problem) => problem.id);
      return { done: countDone(ids), total: ids.length };
    }
    if (href === "/designs") {
      const ids = SITE.designs.map((design) => design.id);
      return { done: countDone(ids), total: ids.length };
    }
    return null;
  }

  function allIds() {
    const ids = [];
    SITE.tracks.forEach((track) => track.cards.forEach((card) => ids.push(card.id)));
    SITE.problems.forEach((problem) => ids.push(problem.id));
    SITE.designs.forEach((design) => ids.push(design.id));
    return ids;
  }

  function renderMeter() {
    const done = allIds().filter((id) => mastered().has(id)).length;
    meter.innerHTML = `<b>${done}</b> / ${allIds().length} 已掌握`;
  }

  function esc(text) {
    return String(text ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function diffClass(diff) {
    if (diff === "简单") return "easy";
    if (diff === "困难") return "hard";
    return "mid";
  }

  function navTarget(parts) {
    if (!parts.length) return "/";
    if (parts[0] === "card" || parts[0] === "track") return `/track/${parts[1]}`;
    if (parts[0] === "problem" || parts[0] === "problems") return "/problems";
    if (parts[0] === "design" || parts[0] === "designs") return "/designs";
    return `/${parts[0]}`;
  }

  function renderNav(path) {
    nav.innerHTML = NAV.map(
      ([group, links]) =>
        `<div class="nav-group">${esc(group)}</div>` +
        links
          .map(([href, label]) => {
            const active = path === href || (href !== "/" && path.startsWith(href));
            const progress = progressForHref(href);
            const full = progress && progress.total > 0 && progress.done === progress.total;
            const count = progress
              ? `<span class="nav-count${full ? " full" : ""}">${progress.done}/${progress.total}</span>`
              : "";
            return `<a href="#${href}" class="${active ? "active" : ""}"><span class="nav-label">${esc(label)}</span>${count}</a>`;
          })
          .join(""),
    ).join("");
  }

  function masterButton(id) {
    const on = mastered().has(id);
    return `<button class="btn ${on ? "on" : ""}" data-master="${esc(id)}" type="button">${on ? "已掌握" : "标为已掌握"}</button>`;
  }

  function bindMaster() {
    view.querySelectorAll("[data-master]").forEach((button) => {
      button.addEventListener("click", () => {
        const set = mastered();
        const id = button.dataset.master;
        if (set.has(id)) set.delete(id);
        else set.add(id);
        setMastered(set);
        button.classList.toggle("on", set.has(id));
        button.textContent = set.has(id) ? "已掌握" : "标为已掌握";
      });
    });
  }

  function paras(text) {
    return String(text ?? "")
      .split(/\n\n+/)
      .filter((part) => part.trim())
      .map((part) => `<p>${esc(part.trim())}</p>`)
      .join("");
  }

  function primerHtml(primer) {
    if (!primer) return "";
    return `<section class="primer">
      <article><h3>背景</h3>${paras(primer.context)}</article>
      <article><h3>原理</h3>${paras(primer.principle)}</article>
      <article><h3>重点考察</h3><ul>${(primer.focus || []).map((item) => `<li>${esc(item)}</li>`).join("")}</ul></article>
    </section>`;
  }

  function blocksHtml(blocks) {
    return (blocks || [])
      .map(
        (block) => `<section class="block">
          ${block.h ? `<h3>${esc(block.h)}</h3>` : ""}
          ${block.p ? `<p>${esc(block.p)}</p>` : ""}
          ${block.bullets ? `<ul>${block.bullets.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>` : ""}
        </section>`,
      )
      .join("");
  }

  function codeBlock(text) {
    return `<pre><code>${esc(text)}</code></pre>`;
  }

  function renderHome() {
    const home = SITE.home;
    view.innerHTML = `
      <p class="kicker">${esc(home.kicker)}</p>
      <h1>${esc(home.title)}</h1>
      <p class="lede">${esc(home.subtitle)}</p>
      <p>${esc(home.level)}</p>
      <div class="toolbar">
        <a class="btn primary" href="#/track/lbs">从坐标系开始</a>
        <a class="btn" href="#/problems">算法题</a>
        <a class="btn" href="#/quiz">做一组自测</a>
        <a class="btn" href="#/lab">打开实验室</a>
      </div>
      <div class="section-head"><h2>四轮在问什么</h2></div>
      <div class="grid">
        ${home.loops
          .map((loop) => `<article class="loop"><b>${esc(loop.name)}</b><span>${esc(loop.detail)}</span></article>`)
          .join("")}
      </div>
      <div class="section-head"><h2>白板旁边的六个数</h2></div>
      <div class="grid-3">
        ${home.formulas
          .map((item) => `<article class="formula"><b>${esc(item.name)}</b><span>${esc(item.text)}</span></article>`)
          .join("")}
      </div>
      <div class="section-head"><h2>今天可以切进去的题</h2><a href="#/problems">全部题目</a></div>
      <div class="list">
        ${SITE.problems
          .slice(0, 6)
          .map(
            (problem) => `<a class="row-link" href="#/problem/${problem.id}">
              <span><b>${esc(problem.title)}</b><br /><span class="muted">${esc(problem.tags.join(" · "))}</span></span>
              <span class="badge ${diffClass(problem.diff)}">${esc(problem.diff)}</span>
            </a>`,
          )
          .join("")}
      </div>
    `;
  }

  function renderPlan() {
    view.innerHTML = `
      <p class="kicker">安排</p>
      <h2>七天，按面试顺序而不是按课本顺序</h2>
      <p class="muted">每天都有口述和手写。语言专项只深挖你投递的那一门。</p>
      <div class="list">
        ${SITE.plan
          .map(
            (day) => `<article class="day"><b>${esc(day.day)} · ${esc(day.title)}</b><ul>${day.items
              .map((item) => `<li>${esc(item)}</li>`)
              .join("")}</ul></article>`,
          )
          .join("")}
      </div>
    `;
  }

  function masteredMark(id) {
    return mastered().has(id)
      ? `<span class="badge easy">已掌握</span>`
      : `<span class="badge pending">未掌握</span>`;
  }

  function renderTrack(id) {
    const track = tracks[id];
    if (!track) return renderMissing();
    const done = countDone(track.cards.map((card) => card.id));
    view.innerHTML = `
      <p class="kicker">专题</p>
      <h2>${esc(track.title)}</h2>
      <p class="lede">${esc(track.blurb)}</p>
      <p class="progress-line">已掌握 <b>${done}/${track.cards.length}</b></p>
      <div class="list">
        ${track.cards
          .map(
            (card) => `<a class="row-link${mastered().has(card.id) ? " done" : ""}" href="#/card/${track.id}/${card.id}">
              <span><b>${esc(card.title)}</b><br /><span class="muted">${esc(card.lead)}</span></span>
              <span class="row-marks">${masteredMark(card.id)}<span class="badge level">${esc(card.level)}</span></span>
            </a>`,
          )
          .join("")}
      </div>
    `;
  }

  function walkHtml(walks) {
    if (!walks || !walks.length) return "";
    return `<section class="walks"><h3>逐行看代码</h3><p class="muted">按执行顺序拆开。先看这几行在算什么，再看下一截。把这些小段按顺序拼起来就是完整实现。</p>${walks
      .map(
        (walk) => `<article class="walk">
          <header><b>${esc(walk.title)}</b>${walk.lang ? `<span class="tag">${esc(walk.lang)}</span>` : ""}</header>
          ${walk.intro ? `<p>${esc(walk.intro)}</p>` : ""}
          <ol class="walk-steps">
            ${walk.steps
              .map(
                (step, index) => `<li>
                  <span class="step-no">${index + 1}</span>
                  <pre><code>${esc(step.code)}</code></pre>
                  <p>${esc(step.say)}</p>
                </li>`,
              )
              .join("")}
          </ol>
        </article>`,
      )
      .join("")}</section>`;
  }

  function renderCard(trackId, cardId) {
    const track = tracks[trackId];
    const card = track && track.cards.find((item) => item.id === cardId);
    if (!card) return renderMissing();
    view.innerHTML = `
      <p class="crumb"><a href="#/track/${track.id}">${esc(track.title)}</a> / ${esc(card.title)}</p>
      <p class="kicker">${esc(card.level)} · 约 ${card.mins} 分钟</p>
      <h2>${esc(card.title)}</h2>
      <p class="lede">${esc(card.lead)}</p>
      <div class="toolbar">
        ${masterButton(card.id)}
        <button class="btn" id="speakTimer" type="button">口述计时 70 秒</button>
        <span class="timer" id="clock"></span>
      </div>
      ${primerHtml(card.primer)}
      <div class="speech"><b>收成一段口述</b><p>${esc(card.speech)}</p></div>
      ${blocksHtml(card.blocks)}
      ${walkHtml(card.walks)}
      ${card.code ? `<h3>${esc(card.code.lang)}</h3>${codeBlock(card.code.text)}` : ""}
      <div class="split">
        <section class="pitfall"><h3>容易说错</h3><ul>${(card.pitfalls || []).map((item) => `<li>${esc(item)}</li>`).join("")}</ul></section>
        <section class="ask"><h3>追问</h3><ul>${(card.asks || []).map((item) => `<li>${esc(item)}</li>`).join("")}</ul></section>
      </div>
    `;
    bindMaster();
    bindTimer(70);
  }

  function renderProblems() {
    view.innerHTML = `
      <p class="kicker">手写</p>
      <h2>算法题</h2>
      <p class="muted">按公开面经里反复出现的字节题型整理，覆盖 3-1、3-2 仍会手写的链表、树、二分、堆、动态规划和地理题。每题都有 Java、Go、Python，三份代码过同一组断言。题面是训练改写，不是原题照抄。先写再对答案。</p>
      <p class="progress-line">已掌握 <b>${countDone(SITE.problems.map((problem) => problem.id))}/${SITE.problems.length}</b></p>
      <div class="toolbar" id="filters">
        ${["全部", "简单", "中等", "困难", "LBS", "高频"].map((name) => `<button class="btn" data-filter="${esc(name)}" type="button">${esc(name)}</button>`).join("")}
      </div>
      <div class="list" id="problemList"></div>
    `;
    const list = view.querySelector("#problemList");
    const paint = (filter) => {
      list.innerHTML = SITE.problems
        .filter((problem) => {
          if (filter === "全部") return true;
          if (filter === "LBS" || filter === "高频") return problem.tags.includes(filter);
          return problem.diff === filter;
        })
        .map(
          (problem) => `<a class="row-link${mastered().has(problem.id) ? " done" : ""}" href="#/problem/${problem.id}">
            <span><b>${esc(problem.title)}</b><br /><span class="muted">${problem.tags.map(esc).join(" · ")} · ${problem.mins} 分钟</span></span>
            <span class="row-marks">${masteredMark(problem.id)}<span class="badge ${diffClass(problem.diff)}">${esc(problem.diff)}</span></span>
          </a>`,
        )
        .join("");
    };
    paint("全部");
    view.querySelectorAll("[data-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        view.querySelectorAll("[data-filter]").forEach((item) => item.classList.remove("primary"));
        button.classList.add("primary");
        paint(button.dataset.filter);
      });
    });
  }

  function renderProblem(id) {
    const problem = problems[id];
    if (!problem) return renderMissing();
    const lang = localStorage.getItem(LANG_KEY) || "Java";
    view.innerHTML = `
      <p class="crumb"><a href="#/problems">算法题</a> / ${esc(problem.title)}</p>
      <p class="kicker">${esc(problem.diff)} · 建议 ${problem.mins} 分钟</p>
      <h2>${esc(problem.title)}</h2>
      <div class="tags">${problem.tags.map((tag) => `<span class="tag">${esc(tag)}</span>`).join("")}</div>
      <p>${esc(problem.prompt)}</p>
      ${problem.examples
        .map((example) => `<p class="example">输入 ${esc(example.in)}<br />输出 ${esc(example.out)}</p>`)
        .join("")}
      <div class="toolbar">
        ${masterButton(problem.id)}
        <button class="btn" id="showIdea" type="button">看思路</button>
        <button class="btn" id="showCode" type="button">看题解</button>
        <button class="btn" id="speakTimer" type="button">限时 ${problem.mins} 分钟</button>
        <span class="timer" id="clock"></span>
      </div>
      <section id="idea" hidden>
        <h3>思路</h3>
        <p>${esc(problem.idea)}</p>
        <div class="split">
          <section class="ask"><h3>边界</h3><ul>${problem.boundary.map((item) => `<li>${esc(item)}</li>`).join("")}</ul></section>
          <section class="pitfall"><h3>追问</h3><ul>${problem.follow.map((item) => `<li>${esc(item)}</li>`).join("")}</ul></section>
        </div>
        <p><b>${esc(problem.complexity)}</b></p>
      </section>
      <section id="code" hidden>
        <div class="tabs">
          ${["Java", "Go", "Python"].map((name) => `<button class="btn" data-lang="${name}" type="button" aria-selected="${name === lang}">${name}</button>`).join("")}
          <button class="btn" id="copyCode" type="button">复制</button>
        </div>
        <pre><code id="snippet"></code></pre>
      </section>
    `;
    bindMaster();
    bindTimer(problem.mins * 60);
    const idea = view.querySelector("#idea");
    const code = view.querySelector("#code");
    view.querySelector("#showIdea").addEventListener("click", () => {
      idea.hidden = !idea.hidden;
    });
    view.querySelector("#showCode").addEventListener("click", () => {
      code.hidden = false;
      paintLang(localStorage.getItem(LANG_KEY) || "Java");
    });
    const paintLang = (name) => {
      localStorage.setItem(LANG_KEY, name);
      view.querySelectorAll("[data-lang]").forEach((button) => {
        button.setAttribute("aria-selected", String(button.dataset.lang === name));
      });
      view.querySelector("#snippet").textContent = problem.code[name];
    };
    view.querySelectorAll("[data-lang]").forEach((button) => {
      button.addEventListener("click", () => {
        code.hidden = false;
        paintLang(button.dataset.lang);
      });
    });
    view.querySelector("#copyCode").addEventListener("click", async () => {
      const text = view.querySelector("#snippet").textContent;
      try {
        await navigator.clipboard.writeText(text);
        view.querySelector("#copyCode").textContent = "已复制";
      } catch (err) {
        view.querySelector("#copyCode").textContent = "复制失败";
      }
    });
  }

  function renderDesigns() {
    view.innerHTML = `
      <p class="kicker">口述</p>
      <h2>四道系统设计</h2>
      <p class="muted">每道都按澄清、容量、接口、结构、数据和故障来排。数字来自页面里的假设，面试官改假设时只替换一项。</p>
      <p class="progress-line">已掌握 <b>${countDone(SITE.designs.map((design) => design.id))}/${SITE.designs.length}</b></p>
      <div class="list">
        ${SITE.designs
          .map(
            (design) => `<a class="row-link${mastered().has(design.id) ? " done" : ""}" href="#/design/${design.id}">
              <span><b>${esc(design.title)}</b><br /><span class="muted">${esc(design.summary)}</span></span>
              <span class="row-marks">${masteredMark(design.id)}<span class="badge">${design.mins} 分钟</span></span>
            </a>`,
          )
          .join("")}
      </div>
    `;
  }

  function renderDesign(id) {
    const design = designs[id];
    if (!design) return renderMissing();
    const section = (title, body) => `<section class="block"><h3>${esc(title)}</h3>${body}</section>`;
    view.innerHTML = `
      <p class="crumb"><a href="#/designs">系统设计</a> / ${esc(design.title)}</p>
      <h2>${esc(design.title)}</h2>
      <p class="lede">${esc(design.summary)}</p>
      <div class="toolbar">
        ${masterButton(design.id)}
        <button class="btn" id="speakTimer" type="button">口述计时 ${design.mins} 分钟</button>
        <span class="timer" id="clock"></span>
      </div>
      ${section("先澄清", `<ul>${design.clarify.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>`)}
      ${section("容量", `<p>${esc(design.capacity)}</p>`)}
      ${section("接口", `<ul>${design.api.map((item) => `<li><span class="example">${esc(item)}</span></li>`).join("")}</ul>`)}
      ${section("结构", `<ul>${design.architecture.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>`)}
      ${section("数据", `<p>${esc(design.data)}</p>`)}
      <div class="split">
        <section class="ask"><h3>取舍</h3><ul>${design.tradeoffs.map((item) => `<li>${esc(item)}</li>`).join("")}</ul></section>
        <section class="pitfall"><h3>故障</h3><ul>${design.failures.map((item) => `<li>${esc(item)}</li>`).join("")}</ul></section>
      </div>
    `;
    bindMaster();
    bindTimer(design.mins * 60);
  }

  function renderProject() {
    const project = SITE.project;
    view.innerHTML = `
      <p class="kicker">项目</p>
      <h2>${esc(project.title)}</h2>
      <p class="lede">${esc(project.lead)}</p>
      <div class="split">
        <section class="card"><h3>被追问时按这个清单答</h3><ul>${project.checks.map((item) => `<li>${esc(item)}</li>`).join("")}</ul></section>
        <section class="card"><h3>练习骨架，不是你的经历</h3><ul>${project.template.map((item) => `<li>${esc(item)}</li>`).join("")}</ul></section>
      </div>
      <section class="pitfall"><h3>减分</h3><ul>${project.traps.map((item) => `<li>${esc(item)}</li>`).join("")}</ul></section>
    `;
  }

  function renderQuiz() {
    const state = { index: 0, picked: null, correct: 0, answered: 0, wrong: [] };
    const paint = () => {
      const item = SITE.quiz[state.index];
      const done = state.index >= SITE.quiz.length;
      if (done) {
        view.innerHTML = `
          <p class="kicker">自测</p>
          <h2>${state.correct} / ${SITE.quiz.length}</h2>
          <p>错题留在下面。再看一次解释，比把分数刷高有用。</p>
          <div class="list">
            ${state.wrong
              .map((id) => {
                const quiz = SITE.quiz.find((row) => row.id === id);
                return `<article class="card"><b>${esc(quiz.q)}</b><p>${esc(quiz.why)}</p></article>`;
              })
              .join("") || "<p>这组题没有错。换一道系统设计口述。</p>"}
          </div>
          <button class="btn primary" id="restartQuiz" type="button">再来一次</button>
        `;
        view.querySelector("#restartQuiz").addEventListener("click", renderQuiz);
        return;
      }
      view.innerHTML = `
        <p class="kicker">自测 · ${esc(item.topic)} · ${state.index + 1} / ${SITE.quiz.length}</p>
        <div class="progress-track"><span style="width:${(state.index / SITE.quiz.length) * 100}%"></span></div>
        <h2>${esc(item.q)}</h2>
        <div id="options">
          ${item.options.map((option, index) => `<button class="quiz-option" data-choice="${index}" type="button">${esc(option)}</button>`).join("")}
        </div>
        <p id="why" hidden></p>
        <button class="btn primary" id="nextQuiz" type="button" hidden>下一题</button>
      `;
      view.querySelectorAll(".quiz-option").forEach((button) => {
        button.addEventListener("click", () => {
          if (state.picked !== null) return;
          state.picked = Number(button.dataset.choice);
          state.answered += 1;
          const good = state.picked === item.answer;
          if (good) state.correct += 1;
          else state.wrong.push(item.id);
          view.querySelectorAll(".quiz-option").forEach((option) => {
            const choice = Number(option.dataset.choice);
            if (choice === item.answer) option.classList.add("good");
            if (choice === state.picked && !good) option.classList.add("bad");
          });
          const why = view.querySelector("#why");
          why.hidden = false;
          why.textContent = item.why;
          view.querySelector("#nextQuiz").hidden = false;
        });
      });
      view.querySelector("#nextQuiz").addEventListener("click", () => {
        state.index += 1;
        state.picked = null;
        paint();
      });
    };
    paint();
  }

  function renderLab() {
    window.LBSLab.render(view);
  }

  function renderMissing() {
    view.innerHTML = `<h2>这一页不存在</h2><p><a href="#/">回到总览</a></p>`;
  }

  function bindTimer(seconds) {
    const button = view.querySelector("#speakTimer");
    const clock = view.querySelector("#clock");
    if (!button) return;
    button.addEventListener("click", () => {
      if (timerId) {
        clearInterval(timerId);
        timerId = null;
        clock.textContent = "";
        return;
      }
      let left = seconds;
      const tick = () => {
        const min = String(Math.floor(left / 60)).padStart(2, "0");
        const sec = String(left % 60).padStart(2, "0");
        clock.textContent = `${min}:${sec}`;
        if (left <= 0) {
          clearInterval(timerId);
          timerId = null;
          clock.textContent = "时间到";
        }
        left -= 1;
      };
      tick();
      timerId = setInterval(tick, 1000);
    });
  }

  function route() {
    if (timerId) {
      clearInterval(timerId);
      timerId = null;
    }
    const parts = (location.hash.replace(/^#/, "") || "/").split("/").filter(Boolean);
    sider.classList.remove("open");
    scrim.classList.remove("show");
    searchPanel.hidden = true;
    renderNav(navTarget(parts));
    if (!parts.length) renderHome();
    else if (parts[0] === "plan") renderPlan();
    else if (parts[0] === "lab") renderLab();
    else if (parts[0] === "track") renderTrack(parts[1]);
    else if (parts[0] === "card") renderCard(parts[1], parts[2]);
    else if (parts[0] === "problems") renderProblems();
    else if (parts[0] === "problem") renderProblem(parts[1]);
    else if (parts[0] === "designs") renderDesigns();
    else if (parts[0] === "design") renderDesign(parts[1]);
    else if (parts[0] === "project") renderProject();
    else if (parts[0] === "quiz") renderQuiz();
    else renderMissing();
    window.scrollTo(0, 0);
  }

  function indexItems() {
    const items = [];
    SITE.tracks.forEach((track) => {
      track.cards.forEach((card) => {
        items.push({
          href: `#/card/${track.id}/${card.id}`,
          kind: track.title,
          title: card.title,
          text: `${card.title} ${card.lead} ${card.speech} ${card.primer ? `${card.primer.context} ${card.primer.principle} ${(card.primer.focus || []).join(" ")}` : ""} ${(card.pitfalls || []).join(" ")} ${(card.walks || []).map((walk) => walk.steps.map((step) => step.say).join(" ")).join(" ")}`,
        });
      });
    });
    SITE.problems.forEach((problem) => {
      items.push({
        href: `#/problem/${problem.id}`,
        kind: "算法",
        title: problem.title,
        text: `${problem.title} ${problem.prompt} ${problem.tags.join(" ")}`,
      });
    });
    SITE.designs.forEach((design) => {
      items.push({
        href: `#/design/${design.id}`,
        kind: "设计",
        title: design.title,
        text: `${design.title} ${design.summary}`,
      });
    });
    return items;
  }

  const indexed = indexItems();
  search.addEventListener("input", () => {
    const q = search.value.trim().toLowerCase();
    if (!q) {
      searchPanel.hidden = true;
      return;
    }
    const hits = indexed
      .filter((item) => item.text.toLowerCase().includes(q))
      .sort((a, b) => Number(!a.title.toLowerCase().includes(q)) - Number(!b.title.toLowerCase().includes(q)))
      .slice(0, 8);
    searchPanel.hidden = hits.length === 0;
    searchPanel.innerHTML = hits
      .map((hit) => `<a href="${hit.href}"><small>${esc(hit.kind)}</small>${esc(hit.title)}</a>`)
      .join("");
  });
  function setMenu(open) {
    sider.classList.toggle("open", open);
    scrim.classList.toggle("show", open);
  }
  document.querySelector("#menuBtn").addEventListener("click", () => setMenu(!sider.classList.contains("open")));
  scrim.addEventListener("click", () => setMenu(false));
  nav.addEventListener("click", (event) => {
    if (event.target.closest("a")) setMenu(false);
  });
  window.addEventListener("hashchange", route);
  renderMeter();
  route();
})();
