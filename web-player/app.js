/**
 * IPTV Web Player — App Logic
 * HLS.js player, channel management, EPG guide, subtitles
 */

const API = window.location.origin;
let hls = null;
let allChannels = [];
let currentChannel = null;
let currentGroup = "all";
let epgGuide = {};
let subLang = "it";
let currentSrtText = null;
let currentSubOffset = 0;

// DOM refs
const $ = (s) => document.querySelector(s);
const video = $("#video");
const placeholder = $("#placeholder");
const channelList = $("#channelList");
const groupTabs = $("#groupTabs");
const searchInput = $("#search");
const controls = $("#controls");
const epgPanel = $("#epgPanel");
const epgContent = $("#epgContent");
const epgCurrent = $("#epgCurrent");
const epgSchedule = $("#epgSchedule");
const subsModal = $("#subsModal");
const subResults = $("#subResults");

// ============================================================
// Init
// ============================================================
async function init() {
    try {
        const res = await fetch(`${API}/api/channels`);
        const data = await res.json();

        // Flatten channels & build group tabs
        const groups = data.groups || {};
        const groupNames = Object.keys(groups);
        allChannels = [];

        groupNames.forEach(g => {
            (groups[g] || []).forEach(ch => {
                ch._group = g;
                allChannels.push(ch);
            });
        });

        // Build group tabs and select
        groupTabs.innerHTML = `<button class="group-tab active" data-group="all">Tutti (${allChannels.length})</button>`;
        const groupSelect = $("#groupSelect");
        let selectHtml = `<option value="all">Tutti (${allChannels.length})</option>`;

        groupNames.forEach(g => {
            const count = groups[g].length;
            groupTabs.innerHTML += `<button class="group-tab" data-group="${g}">${g} (${count})</button>`;
            selectHtml += `<option value="${g}">${g} (${count})</option>`;
        });

        if (groupSelect) groupSelect.innerHTML = selectHtml;

        // Sync Selection function
        function setGroup(g) {
            currentGroup = g;
            groupTabs.querySelectorAll(".group-tab").forEach(b => b.classList.remove("active"));
            const activeBtn = Array.from(groupTabs.querySelectorAll(".group-tab")).find(b => b.dataset.group === g);
            if (activeBtn) activeBtn.classList.add("active");

            if (groupSelect) groupSelect.value = g;
            renderChannels();
        }

        // Desktop tab click handlers
        groupTabs.querySelectorAll(".group-tab").forEach(btn => {
            btn.addEventListener("click", () => setGroup(btn.dataset.group));
        });

        // Mobile select change handler
        if (groupSelect) {
            groupSelect.addEventListener("change", (e) => setGroup(e.target.value));
        }

        // Load EPG guide
        loadEpgGuide();

        // Render channels
        renderChannels();
    } catch (err) {
        channelList.innerHTML = `<div class="loading-spinner">Errore: ${err.message}<br><small>Assicurati che il server sia avviato</small></div>`;
    }
}

async function loadEpgGuide() {
    try {
        const res = await fetch(`${API}/api/epg/guide`);
        epgGuide = await res.json();
    } catch (e) {
        console.warn("EPG guide not available:", e);
    }
}

// ============================================================
// Channel List
// ============================================================
function renderChannels() {
    const query = searchInput.value.toLowerCase().trim();
    let filtered = allChannels;

    if (currentGroup !== "all") {
        filtered = filtered.filter(ch => ch._group === currentGroup);
    }
    if (query) {
        filtered = filtered.filter(ch => ch.name.toLowerCase().includes(query));
    }

    // Deduplicate by name within same group view
    const seen = new Set();
    filtered = filtered.filter(ch => {
        const key = `${ch.name}|${ch._group}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });

    if (filtered.length === 0) {
        channelList.innerHTML = '<div class="loading-spinner">Nessun canale trovato</div>';
        return;
    }

    channelList.innerHTML = filtered.map(ch => {
        const isActive = currentChannel && currentChannel.name === ch.name && currentChannel._group === ch._group;
        const epgInfo = epgGuide[ch.tvg_id];
        const nowTitle = epgInfo?.current?.title || "";
        const logoHtml = ch.logo
            ? `<img class="channel-logo" src="${ch.logo}" alt="" loading="lazy" onerror="this.outerHTML='<div class=\\'channel-logo-placeholder\\'>${ch.name.substring(0, 2)}</div>'">`
            : `<div class="channel-logo-placeholder">${ch.name.substring(0, 2)}</div>`;

        return `
            <div class="channel-item ${isActive ? 'active' : ''}" data-name="${ch.name}" data-group="${ch._group}">
                ${logoHtml}
                <div class="channel-info">
                    <div class="ch-name">${ch.name}</div>
                    ${nowTitle ? `<div class="ch-program">${nowTitle}</div>` : ''}
                    <span class="ch-group">${ch._group}</span>
                </div>
                ${isActive ? '<div class="live-dot"></div>' : ''}
            </div>
        `;
    }).join("");

    // Click handlers
    channelList.querySelectorAll(".channel-item").forEach(el => {
        el.addEventListener("click", () => {
            const name = el.dataset.name;
            const group = el.dataset.group;
            const ch = allChannels.find(c => c.name === name && c._group === group);
            if (ch) playChannel(ch);
        });
    });
}

// ============================================================
// HLS Player
// ============================================================
function playChannel(ch) {
    currentChannel = ch;

    // Update UI
    placeholder.style.display = "none";
    video.style.display = "block";

    // Update now playing
    $("#channelNameDisplay").textContent = ch.name;
    const logoEl = $("#channelLogo");
    if (ch.logo) {
        logoEl.src = ch.logo;
        logoEl.style.display = "block";
    } else {
        logoEl.style.display = "none";
    }

    // Proxy the stream URL
    const streamUrl = `${API}/proxy/stream?url=${encodeURIComponent(ch.url)}`;

    // Clear old subtitle tracks and hide CC button/offset controls
    Array.from(video.querySelectorAll("track")).forEach(t => t.remove());
    $("#btnToggleSubs").style.display = "none";
    $("#btnToggleSubs").style.opacity = "1";
    $("#subOffsetControls").style.display = "none";
    currentSrtText = null;
    currentSubOffset = 0;
    $("#subOffsetDisplay").textContent = "0.0s";

    // Destroy old HLS
    if (hls) {
        hls.destroy();
        hls = null;
    }

    if (Hls.isSupported()) {
        hls = new Hls({
            maxBufferLength: 30,
            maxMaxBufferLength: 60,
            enableWorker: true,
        });
        hls.loadSource(streamUrl);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
            video.play().catch(() => { });
        });
        hls.on(Hls.Events.ERROR, (_, data) => {
            if (data.fatal) {
                console.error("HLS fatal error:", data);
                if (data.type === Hls.ErrorTypes.NETWORK_ERROR) {
                    hls.startLoad();
                } else {
                    hls.destroy();
                }
            }
        });
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
        // Safari native HLS
        video.src = streamUrl;
        video.play().catch(() => { });
    }

    // Load EPG for this channel
    loadChannelEpg(ch);

    // Re-render channel list to update active state
    renderChannels();
}

// ============================================================
// EPG
// ============================================================
async function loadChannelEpg(ch) {
    const epgId = ch.tvg_id || ch.id;
    $("#programTitleDisplay").textContent = "Caricamento guida...";

    try {
        const res = await fetch(`${API}/api/epg?channel_id=${encodeURIComponent(epgId)}`);
        const data = await res.json();

        // Current program
        if (data.current) {
            const now = Date.now() / 1000;
            const start = new Date(data.current.start).getTime() / 1000;
            const stop = new Date(data.current.stop).getTime() / 1000;
            const progress = Math.min(100, ((now - start) / (stop - start)) * 100);

            const startTime = formatTime(data.current.start);
            const stopTime = formatTime(data.current.stop);

            $("#programTitleDisplay").textContent = data.current.title || "";

            // OSD Overlay
            $("#osdTimeNow").textContent = `${startTime} — ${stopTime}`;
            $("#osdTitleNow").textContent = data.current.title || "Programma sconosciuto";

            if (data.current.desc) {
                $("#osdDescNow").textContent = data.current.desc;
                $("#osdDescNow").style.display = "block";
            } else {
                $("#osdDescNow").textContent = "";
                $("#osdDescNow").style.display = "none";
            }

            $("#osdProgressBar").style.width = `${progress}%`;
            $("#osdEpg").style.display = "block";

            epgCurrent.innerHTML = `
                <div class="epg-now-card" style="--progress: ${progress}%">
                    <div class="epg-now-label">▶ In onda ora</div>
                    <div class="epg-now-title">${data.current.title || "Programma sconosciuto"}</div>
                    <div class="epg-now-time">${startTime} — ${stopTime}</div>
                    ${data.current.desc ? `<div class="epg-now-desc">${data.current.desc}</div>` : ""}
                    <div class="epg-progress"><div class="epg-progress-bar" style="width:${progress}%"></div></div>
                </div>
            `;
        } else {
            $("#programTitleDisplay").textContent = "";
            $("#osdEpg").style.display = "none";
            epgCurrent.innerHTML = '<div class="epg-placeholder">Nessuna informazione EPG per questo canale</div>';
        }

        // Next programs
        if (data.next) {
            let upcoming = [];
            const currentStop = data.current ? new Date(data.current.stop).getTime() / 1000 : 0;

            for (let p of data.programs) {
                const pStart = new Date(p.start).getTime() / 1000;
                if (pStart >= currentStop && upcoming.length < 8) {
                    upcoming.push(p);
                }
            }

            // OSD Next Programs (limit to 2 for overlay)
            $("#osdEpgNext").innerHTML = upcoming.slice(0, 2).map(p => `
                <div class="osd-next-item">
                    <span class="osd-time">${formatTime(p.start)}</span>
                    <span class="osd-next-title">${p.title || "—"}</span>
                </div>
            `).join("");

            epgSchedule.innerHTML = upcoming.map(p => `
                <div class="epg-schedule-item">
                    <span class="epg-schedule-time">${formatTime(p.start)}</span>
                    <span class="epg-schedule-title">${p.title || "—"}</span>
                </div>
            `).join("");
        } else {
            epgSchedule.innerHTML = "";
            $("#osdEpgNext").innerHTML = "";
        }
    } catch (e) {
        epgCurrent.innerHTML = '<div class="epg-placeholder">EPG non disponibile</div>';
        $("#programTitleDisplay").textContent = "";
        $("#osdEpg").style.display = "none";
    }
}

function formatTime(isoStr) {
    if (!isoStr) return "";
    const d = new Date(isoStr);
    return d.toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" });
}

// Auto-refresh EPG every 60s
setInterval(() => {
    if (currentChannel) loadChannelEpg(currentChannel);
}, 60000);

// ============================================================
// Player Controls
// ============================================================

// Play / Pause
$("#btnPlay").addEventListener("click", () => {
    if (video.paused) {
        video.play();
    } else {
        video.pause();
    }
});
video.addEventListener("play", () => {
    $("#btnPlay").innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>';
});
video.addEventListener("pause", () => {
    $("#btnPlay").innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21"/></svg>';
});

// Volume
const volumeSlider = $("#volume");
volumeSlider.addEventListener("input", () => {
    video.volume = parseFloat(volumeSlider.value);
    video.muted = false;
});
video.volume = 0.8;

// Mute
$("#btnMute").addEventListener("click", () => {
    video.muted = !video.muted;
    const icon = video.muted
        ? '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19"/><line x1="23" y1="9" x2="17" y2="15" stroke="currentColor" stroke-width="2"/><line x1="17" y1="9" x2="23" y2="15" stroke="currentColor" stroke-width="2"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" stroke="currentColor" stroke-width="2" fill="none"/></svg>';
    $("#btnMute").innerHTML = icon;
});

// Fullscreen
$("#btnFullscreen").addEventListener("click", () => {
    const container = $("#playerContainer");
    if (!document.fullscreenElement) {
        container.requestFullscreen().catch(() => { });
    } else {
        document.exitFullscreen();
    }
});

// Picture-in-Picture
$("#btnPip").addEventListener("click", () => {
    if (document.pictureInPictureElement) {
        document.exitPictureInPicture();
    } else if (video.requestPictureInPicture) {
        video.requestPictureInPicture().catch(() => { });
    }
});

// Double-click fullscreen
$("#playerContainer").addEventListener("dblclick", () => {
    if (!document.fullscreenElement) {
        $("#playerContainer").requestFullscreen().catch(() => { });
    } else {
        document.exitFullscreen();
    }
});

// ============================================================
// EPG Panel Toggle
// ============================================================
$("#btnGuide").addEventListener("click", () => epgPanel.classList.add("open"));
$("#epgToggle").addEventListener("click", (e) => {
    e.stopPropagation();
    epgPanel.classList.remove("open");
});

// ============================================================
// Subtitles
// ============================================================
$("#btnSubs").addEventListener("click", () => {
    subsModal.classList.add("open");
    if (currentChannel) {
        searchSubtitles();
    }
});
$("#subsClose").addEventListener("click", () => subsModal.classList.remove("open"));
subsModal.addEventListener("click", (e) => {
    if (e.target === subsModal) subsModal.classList.remove("open");
});

// Language tabs
document.querySelectorAll(".sub-tab").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".sub-tab").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        subLang = btn.dataset.lang;
        searchSubtitles();
    });
});

async function searchSubtitles() {
    if (!currentChannel) return;

    // Get current program title from EPG
    let title = "";
    try {
        const epgId = currentChannel.tvg_id || currentChannel.id;
        const res = await fetch(`${API}/api/epg?channel_id=${encodeURIComponent(epgId)}`);
        const data = await res.json();
        title = data.current?.title || currentChannel.name;
    } catch {
        title = currentChannel.name;
    }

    subResults.innerHTML = '<p class="sub-hint">Ricerca sottotitoli...</p>';

    try {
        const res = await fetch(`${API}/api/subtitles?title=${encodeURIComponent(title)}&lang=${subLang}`);
        const data = await res.json();

        if (data.results && data.results.length > 0) {
            subResults.innerHTML = data.results.map(s => `
                <div class="sub-item">
                    <div class="sub-item-info">
                        <div class="sub-item-title">${s.title}</div>
                        <div class="sub-item-meta">${s.year} · ${s.lang} · ⭐ ${s.rating}</div>
                    </div>
                    <button onclick="applySubtitle('${s.download_url}')" class="sub-download">Applica</button>
                </div>
            `).join("");
        } else {
            subResults.innerHTML = `<p class="sub-hint">Nessun sottotitolo trovato per "${title}" (${subLang})</p>`;
        }
    } catch (e) {
        subResults.innerHTML = `<p class="sub-hint">Errore ricerca: ${e.message}</p>`;
    }
}

// Convert SRT to WebVTT format and apply optional time offset (in seconds)
function srtToVtt(srtStr, offsetSeconds = 0) {
    let vtt = "WEBVTT\n\n";

    // Parse times and shift
    const shifted = srtStr.replace(/(\d{2}):(\d{2}):(\d{2}),(\d{3})/g, (match, h, m, s, ms) => {
        let date = new Date(1970, 0, 1, parseInt(h), parseInt(m), parseInt(s), parseInt(ms));
        date.setMilliseconds(date.getMilliseconds() + (offsetSeconds * 1000));

        let outH = String(date.getHours()).padStart(2, '0');
        let outM = String(date.getMinutes()).padStart(2, '0');
        let outS = String(date.getSeconds()).padStart(2, '0');
        let outMs = String(date.getMilliseconds()).padStart(3, '0');

        return `${outH}:${outM}:${outS}.${outMs}`;
    });

    return vtt + shifted;
}

window.applySubtitle = async function (url) {
    subsModal.classList.remove("open");
    const titleEl = $("#programTitleDisplay");
    titleEl.textContent = "Applicazione sottotitolo in corso...";

    try {
        const res = await fetch(API + url);
        if (!res.ok) throw new Error("Errore nel download del sottotitolo");
        currentSrtText = await res.text();
        currentSubOffset = 0;
        $("#subOffsetDisplay").textContent = "0.0s";

        applyVttTrack();

        // Show offset controls
        $("#subOffsetControls").style.display = "block";

        titleEl.textContent = "Sottotitolo applicato!";
        setTimeout(() => { if (currentChannel) loadChannelEpg(currentChannel); }, 2000);
    } catch (e) {
        console.error("Subtitle Apply Error:", e);
        titleEl.textContent = "Errore sottotitolo";
        setTimeout(() => { if (currentChannel) loadChannelEpg(currentChannel); }, 2000);
    }
}

function applyVttTrack() {
    if (!currentSrtText) return;

    const vttText = srtToVtt(currentSrtText, currentSubOffset);
    const blob = new Blob([vttText], { type: "text/vtt" });
    const blobUrl = URL.createObjectURL(blob);

    // Remove old tracks
    Array.from(video.querySelectorAll("track")).forEach(t => t.remove());

    // Attach new track
    const track = document.createElement("track");
    track.kind = "subtitles";
    track.label = "Sottotitoli";
    track.srclang = subLang;
    track.src = blobUrl;
    track.default = true;

    video.appendChild(track);

    // Enable CC Button
    const btnToggle = $("#btnToggleSubs");
    btnToggle.style.display = "flex";
    btnToggle.style.opacity = "1";

    if (video.textTracks && video.textTracks[0]) {
        video.textTracks[0].mode = "showing";
    }
}

window.adjustSubOffset = function (delta) {
    if (!currentSrtText) return;
    currentSubOffset += delta;
    $("#subOffsetDisplay").textContent = (currentSubOffset > 0 ? "+" : "") + currentSubOffset.toFixed(1) + "s";
    applyVttTrack();
}

window.resetSubOffset = function () {
    if (!currentSrtText) return;
    currentSubOffset = 0;
    $("#subOffsetDisplay").textContent = "0.0s";
    applyVttTrack();
}

// CC Button Toggle
$("#btnToggleSubs").addEventListener("click", () => {
    if (video.textTracks && video.textTracks.length > 0) {
        const track = video.textTracks[0];
        if (track.mode === "showing") {
            track.mode = "hidden";
            $("#btnToggleSubs").style.opacity = "0.5";
        } else {
            track.mode = "showing";
            $("#btnToggleSubs").style.opacity = "1";
        }
    }
});

// ============================================================
// Controls Idle/Autohide Logic
// ============================================================
let controlsTimer;
const playerContainer = $("#playerContainer");
const controlsOverlay = $(".controls-overlay");

function resetControlsIdle() {
    controlsOverlay.classList.add("visible");
    playerContainer.classList.remove("idle");

    clearTimeout(controlsTimer);
    controlsTimer = setTimeout(() => {
        controlsOverlay.classList.remove("visible");
        if (document.fullscreenElement) {
            playerContainer.classList.add("idle");
        }
    }, 5000);
}

playerContainer.addEventListener("mousemove", resetControlsIdle);
playerContainer.addEventListener("mousedown", resetControlsIdle);
playerContainer.addEventListener("mouseleave", () => {
    controlsOverlay.classList.remove("visible");
});
video.addEventListener("play", resetControlsIdle);

// ============================================================
// Search
// ============================================================
searchInput.addEventListener("input", () => renderChannels());

// ============================================================
// Mobile Menu Toggle
// ============================================================
const mobileMenuBtn = $("#mobileMenuBtn");
const sidebar = $("#sidebar");
const mobileBackdrop = $("#mobileBackdrop");

function toggleMobileMenu() {
    sidebar.classList.toggle("open");
    mobileBackdrop.classList.toggle("open");
}

if (mobileMenuBtn) mobileMenuBtn.addEventListener("click", toggleMobileMenu);
if (mobileBackdrop) mobileBackdrop.addEventListener("click", toggleMobileMenu);

// Keyboard shortcut: Escape to close modal
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        subsModal.classList.remove("open");
        epgPanel.classList.remove("open");
        sidebar.classList.remove("open");
        if (mobileBackdrop) mobileBackdrop.classList.remove("open");
    }
    if (e.key === "f" && !e.ctrlKey && document.activeElement !== searchInput) {
        e.preventDefault();
        if (!document.fullscreenElement) {
            $("#playerContainer").requestFullscreen().catch(() => { });
        } else {
            document.exitFullscreen();
        }
    }
    if (e.key === " " && document.activeElement !== searchInput) {
        e.preventDefault();
        video.paused ? video.play() : video.pause();
    }
    if (e.key === "m" && document.activeElement !== searchInput) {
        video.muted = !video.muted;
    }
});

// ============================================================
// Fullscreen Auto-Rotation
// ============================================================
document.addEventListener('fullscreenchange', async () => {
    if (document.fullscreenElement) {
        // Entering fullscreen: attempt to lock landscape
        try {
            if (screen.orientation && screen.orientation.lock) {
                await screen.orientation.lock('landscape');
            }
        } catch (err) {
            console.warn("Autolock landscape not supported or denied:", err);
        }
    } else {
        // Exiting fullscreen: unlock orientation
        try {
            if (screen.orientation && screen.orientation.unlock) {
                screen.orientation.unlock();
            }
        } catch (err) {
            console.warn("Orientation unlock error:", err);
        }
    }
});

// ============================================================
// Start
// ============================================================
init();
