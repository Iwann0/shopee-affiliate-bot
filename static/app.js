// Tab switching
document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
        tab.classList.add("active");
        document.getElementById("tab-" + tab.dataset.tab).classList.add("active");
    });
});

function showToast(msg) {
    const toast = document.getElementById("toast");
    toast.textContent = msg;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2000);
}

// ── Profile ──
async function loadProfile() {
    try {
        const res = await fetch("/api/profile");
        const data = await res.json();
        if (data.error) {
            document.getElementById("profile-badge").innerHTML =
                `<span style="color:#f4212e">${data.error}</span>`;
            return;
        }
        document.getElementById("profile-badge").innerHTML = `
            <span class="username">@${data.username}</span>
            <div class="stats">
                <span class="stat"><span class="stat-num">${data.followers}</span> followers</span>
                <span class="stat"><span class="stat-num">${data.following}</span> following</span>
            </div>`;

        document.getElementById("stat-followers").textContent = data.followers;
        document.getElementById("stat-following").textContent = data.following;
        document.getElementById("stat-tweets").textContent = data.tweets;

        if (data.tips && data.tips.length) {
            const tipsEl = document.getElementById("growth-tips");
            tipsEl.style.display = "block";
            document.getElementById("tips-list").innerHTML =
                data.tips.map(t => `<div class="tip">${t}</div>`).join("");
        }
    } catch (e) {
        document.getElementById("profile-badge").innerHTML =
            `<span style="color:#f4212e">Connection error</span>`;
    }
}

// ── Trends ──
async function loadTrends() {
    document.getElementById("twitter-trends").innerHTML = '<span class="loading">Loading trends...</span>';
    document.getElementById("interest-scores").innerHTML = '<span class="loading">Loading scores...</span>';
    document.getElementById("rising-queries").innerHTML = '<span class="loading">Loading queries...</span>';

    try {
        const res = await fetch("/api/trends");
        const data = await res.json();
        if (data.error) {
            document.getElementById("twitter-trends").innerHTML =
                `<span style="color:#f4212e">${data.error}</span>`;
            return;
        }

        // Twitter trends
        if (data.twitter_trends && data.twitter_trends.length) {
            document.getElementById("twitter-trends").innerHTML = `
                <ol class="trend-list">
                    ${data.twitter_trends.map((t, i) =>
                        `<li><span class="trend-rank">${i + 1}</span><span class="trend-name">${t}</span></li>`
                    ).join("")}
                </ol>`;
        } else {
            document.getElementById("twitter-trends").innerHTML = "No trends found";
        }

        // Interest scores
        if (data.interest_scores && Object.keys(data.interest_scores).length) {
            const sorted = Object.entries(data.interest_scores).sort((a, b) => b[1] - a[1]);
            document.getElementById("interest-scores").innerHTML = sorted.map(([k, v]) => `
                <div class="interest-item">
                    <span class="interest-label">${k}</span>
                    <div class="interest-bar-bg">
                        <div class="interest-bar" style="width:${v}%"></div>
                    </div>
                    <span class="interest-value">${v}</span>
                </div>`).join("");
        } else {
            document.getElementById("interest-scores").innerHTML = "No interest data";
        }

        // Rising queries
        if (data.rising_queries && Object.keys(data.rising_queries).length) {
            let html = "";
            for (const [keyword, queries] of Object.entries(data.rising_queries)) {
                if (queries.length === 0) continue;
                html += `<div class="rising-group"><h4>${keyword}</h4>`;
                html += queries.slice(0, 5).map(q => `
                    <div class="rising-item">
                        <span>${q.query}</span>
                        <span class="rising-value">+${q.value}%</span>
                    </div>`).join("");
                html += "</div>";
            }
            document.getElementById("rising-queries").innerHTML = html || "No rising queries";
        } else {
            document.getElementById("rising-queries").innerHTML = "No rising queries";
        }
    } catch (e) {
        document.getElementById("twitter-trends").innerHTML =
            `<span style="color:#f4212e">Failed to load trends</span>`;
    }
}

// ── Drafts ──
async function loadDrafts() {
    document.getElementById("drafts-list").innerHTML = '<span class="loading">Generating drafts...</span>';

    try {
        const res = await fetch("/api/drafts");
        const data = await res.json();
        if (data.error) {
            document.getElementById("drafts-list").innerHTML =
                `<span style="color:#f4212e">${data.error}</span>`;
            return;
        }

        document.getElementById("drafts-list").innerHTML = data.map(d => `
            <div class="draft-card" onclick="copyDraft(this)">
                <div class="draft-header">
                    <span class="draft-topic">${d.topic}</span>
                    <span class="draft-chars">${d.char_count} chars</span>
                </div>
                <div class="draft-text">${d.full_tweet}</div>
                <div class="copy-hint">Click to copy</div>
            </div>`).join("");
    } catch (e) {
        document.getElementById("drafts-list").innerHTML =
            `<span style="color:#f4212e">Failed to generate drafts</span>`;
    }
}

function copyDraft(card) {
    const text = card.querySelector(".draft-text").textContent;
    navigator.clipboard.writeText(text).then(() => showToast("Copied to clipboard!"));
}

// ── Accounts ──
async function loadAccounts() {
    document.getElementById("accounts-list").innerHTML = '<span class="loading">Loading suggestions...</span>';

    try {
        const res = await fetch("/api/accounts");
        const data = await res.json();
        if (data.error) {
            document.getElementById("accounts-list").innerHTML =
                `<span style="color:#f4212e">${data.error}</span>`;
            return;
        }

        document.getElementById("accounts-list").innerHTML = data.map(s => `
            <div class="account-card">
                <h4>${s.keyword}</h4>
                <div class="search-query" onclick="copySearch(this)" title="Click to copy">
                    ${s.search_query}
                </div>
                <div class="strategy">${s.strategy}</div>
                <ul>${s.account_types.map(t => `<li>${t}</li>`).join("")}</ul>
            </div>`).join("");
    } catch (e) {
        document.getElementById("accounts-list").innerHTML =
            `<span style="color:#f4212e">Failed to load suggestions</span>`;
    }
}

function copySearch(el) {
    navigator.clipboard.writeText(el.textContent.trim()).then(() =>
        showToast("Search query copied!")
    );
}

// ── Analytics ──
async function loadAnalytics() {
    try {
        const res = await fetch("/api/analytics");
        const data = await res.json();
        if (data.error) {
            document.getElementById("growth-summary").innerHTML =
                `<span style="color:#f4212e">${data.error}</span>`;
            return;
        }

        // Summary
        const s = data.summary;
        if (s && s.total_snapshots > 0) {
            const growth = s.follower_growth || 0;
            document.getElementById("growth-summary").innerHTML = `
                <table class="summary-table">
                    <tr><td>Total snapshots</td><td>${s.total_snapshots}</td></tr>
                    <tr><td>Current followers</td><td>${s.current_followers}</td></tr>
                    <tr><td>Follower growth</td><td>${growth >= 0 ? "+" : ""}${growth}</td></tr>
                    <tr><td>Avg per day</td><td>${s.avg_followers_per_day || 0}</td></tr>
                    <tr><td>Period</td><td>${s.period_days || 0} days</td></tr>
                </table>`;
        } else {
            document.getElementById("growth-summary").innerHTML =
                "No analytics data yet. Run the bot to start tracking.";
        }

        // Follower chart
        if (data.history && data.history.length > 0) {
            const maxF = Math.max(...data.history.map(h => h.followers), 1);
            document.getElementById("follower-chart").innerHTML = data.history.map(h => {
                const pct = (h.followers / maxF * 100);
                const date = new Date(h.timestamp).toLocaleString();
                return `
                    <div class="chart-row">
                        <span class="chart-date">${date}</span>
                        <div class="chart-bar-bg">
                            <div class="chart-bar" style="width:${pct}%"></div>
                        </div>
                        <span class="chart-val">${h.followers}</span>
                    </div>`;
            }).join("");
        } else {
            document.getElementById("follower-chart").innerHTML =
                '<span class="loading">No history data yet</span>';
        }
    } catch (e) {
        document.getElementById("growth-summary").innerHTML =
            `<span style="color:#f4212e">Failed to load analytics</span>`;
    }
}

// ── Settings ──
async function loadSettings() {
    try {
        const res = await fetch("/api/settings");
        const data = await res.json();
        document.getElementById("settings-keywords").value =
            Array.isArray(data.niche_keywords) ? data.niche_keywords.join(", ") : data.niche_keywords;
        document.getElementById("settings-draft-count").value = data.draft_count || 5;
    } catch (e) {
        console.error("Failed to load settings", e);
    }
}

async function saveSettings() {
    const keywords = document.getElementById("settings-keywords").value;
    const draftCount = document.getElementById("settings-draft-count").value;

    try {
        const res = await fetch("/api/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                niche_keywords: keywords,
                draft_count: parseInt(draftCount),
            }),
        });
        const data = await res.json();
        if (data.error) {
            document.getElementById("settings-status").innerHTML =
                `<span style="color:#f4212e">${data.error}</span>`;
        } else {
            showToast("Settings saved!");
        }
    } catch (e) {
        document.getElementById("settings-status").innerHTML =
            `<span style="color:#f4212e">Failed to save</span>`;
    }
}

// ── Init ──
loadProfile();
loadTrends();
loadDrafts();
loadAccounts();
loadAnalytics();
loadSettings();
