/*
 * Scoped interaction layer for the existing macOS portfolio.
 * It augments existing dialogs/nodes/dock without replacing their launch logic.
 */
(() => {
  "use strict";

  // Retire the three legacy award badges entirely; CSS hides them before this script runs.
  document.getElementById("awards-stack")?.remove();

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const compactViewport = window.matchMedia("(max-width: 1024px)");
  const dialogSelector = '[role="dialog"]';
  const titlebarSelector = [
    "#caseHubModal .ch-head", "#caseModal .cs-header", "#caseModal2 .cs-header",
    "#collectionModal .cm-head", "#trashModal .trash-head", "#notebookModal .nb-titlebar",
    "#stickiesModal #stickiesHeader", "#aboutModal > div > div:first-child",
    "#servicesModal > div > div:first-child", "#pk01Modal #pk01Card > div:first-child",
    "#chessModal .chm-bar", "#previewModal > div > div:first-child", "#composeModal .cmp-title"
  ].join(",");
  const closeSelector = [
    "#chClose", "#csClose", "#cs2Close", ".trash-close", "#notebookClose", "#chessClose",
    "#stickiesClose", "#aboutClose", "#servicesClose", "#pk01Close", "#pvClose", "#cmpBarClose", ".dot.close"
  ].join(",");

  let windowLayer = 900;
  let activeWindow = null;
  let lastLauncher = null;

  const visible = (element) => {
    const style = window.getComputedStyle(element);
    return style.display !== "none" && style.visibility !== "hidden";
  };

  const activateWindow = (modal, launcher = lastLauncher) => {
    if (!modal || !visible(modal) || modal.classList.contains("macos-window-activating")) return;
    modal.classList.add("macos-window-activating");
    windowLayer += 1;
    document.querySelectorAll(`${dialogSelector}.macos-window-active`).forEach((item) => {
      if (item !== modal) item.classList.remove("macos-window-active");
    });
    modal.classList.remove("macos-window-closing");
    modal.classList.add("macos-window-active");
    modal.style.zIndex = String(windowLayer);
    requestAnimationFrame(() => {
      if (!modal.classList.contains("macos-window-closing")) modal.classList.add("macos-window-visible");
      modal.classList.remove("macos-window-activating");
    });
    activeWindow = modal;
    if (launcher) modal.__macosLauncher = launcher;
  };

  const closeWindow = (modal) => {
    if (!modal || !visible(modal)) return;
    if (reducedMotion.matches) {
      modal.style.display = "none";
      return;
    }
    modal.classList.add("macos-window-closing");
    modal.classList.remove("macos-window-visible", "macos-window-active");
    window.setTimeout(() => {
      modal.style.display = "none";
      modal.__macosLauncher?.focus?.({ preventScroll: true });
    }, 155);
  };

  const prepareDialog = (modal) => {
    modal.classList.add("macos-window");
    modal.setAttribute("aria-modal", "true");
    if (!modal.hasAttribute("tabindex")) modal.tabIndex = -1;
    new MutationObserver(() => {
      if (visible(modal) && !modal.classList.contains("macos-window-visible") && !modal.classList.contains("macos-window-activating") && !modal.classList.contains("macos-window-closing")) activateWindow(modal);
      else if (!visible(modal) && ["macos-window-visible", "macos-window-active", "macos-window-closing", "macos-window-activating"].some((state) => modal.classList.contains(state))) {
        modal.classList.remove("macos-window-visible", "macos-window-active", "macos-window-closing", "macos-window-activating");
      }
    }).observe(modal, { attributes: true, attributeFilter: ["style", "class"] });
    if (visible(modal)) activateWindow(modal);
  };

  document.querySelectorAll(dialogSelector).forEach(prepareDialog);

  document.addEventListener("click", (event) => {
    const control = event.target.closest(closeSelector);
    const modal = control?.closest(dialogSelector);
    if (!modal || !visible(modal)) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    closeWindow(modal);
  }, true);

  // Add title-bar dragging only on wide, pointer-capable desktop surfaces.
  document.querySelectorAll(titlebarSelector).forEach((bar) => {
    bar.classList.add("macos-window-titlebar");
    let drag = null;

    bar.addEventListener("pointerdown", (event) => {
      if (compactViewport.matches || reducedMotion.matches || event.button !== 0) return;
      if (event.target.closest("button, a, input, textarea, select, [role=button]")) return;
      const modal = bar.closest(dialogSelector);
      const panel = bar.parentElement;
      if (!modal || !panel || !visible(modal)) return;

      activateWindow(modal);
      const rect = panel.getBoundingClientRect();
      drag = { panel, pointerId: event.pointerId, x: event.clientX, y: event.clientY, left: rect.left, top: rect.top };
      panel.classList.add("macos-floating-window");
      panel.style.width = `${rect.width}px`;
      panel.style.position = "fixed";
      panel.style.left = `${rect.left}px`;
      panel.style.top = `${rect.top}px`;
      panel.style.right = "auto";
      panel.style.bottom = "auto";
      panel.style.margin = "0";
      panel.style.transform = "translate3d(0,0,0)";
      bar.classList.add("macos-window-dragging");
      bar.setPointerCapture(event.pointerId);
      event.preventDefault();
    });

    bar.addEventListener("pointermove", (event) => {
      if (!drag || event.pointerId !== drag.pointerId) return;
      const dx = event.clientX - drag.x;
      const dy = event.clientY - drag.y;
      drag.panel.style.transform = `translate3d(${dx}px, ${dy}px, 0)`;
    });

    const release = (event) => {
      if (!drag || event.pointerId !== drag.pointerId) return;
      const dx = event.clientX - drag.x;
      const dy = event.clientY - drag.y;
      drag.panel.style.left = `${Math.round(drag.left + dx)}px`;
      drag.panel.style.top = `${Math.round(drag.top + dy)}px`;
      drag.panel.style.transform = "";
      drag.panel.classList.remove("macos-floating-window");
      bar.classList.remove("macos-window-dragging");
      try { bar.releasePointerCapture(event.pointerId); } catch (_) { /* no-op */ }
      drag = null;
    };
    bar.addEventListener("pointerup", release);
    bar.addEventListener("pointercancel", release);
  });

  // Existing desktop artwork becomes keyboard-operable without changing its launch handlers.
  document.querySelectorAll(".node:not(.photos-mobile)").forEach((node) => {
    node.classList.add("macos-launcher");
    node.tabIndex = 0;
    node.setAttribute("role", "button");
    if (!node.getAttribute("aria-label")) node.setAttribute("aria-label", node.dataset.label || "Open desktop item");
    node.addEventListener("pointerdown", () => { lastLauncher = node; }, { passive: true });
    node.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      lastLauncher = node;
      node.dispatchEvent(new MouseEvent("dblclick", { bubbles: true, cancelable: true, view: window }));
    });
  });

  // Dock proximity uses transforms only, avoiding the original margin-based reflow.
  const dock = document.getElementById("dock");
  if (dock) {
    const items = Array.from(dock.querySelectorAll(".di"));
    let dockFrame = 0;
    const resetDock = () => items.forEach((item) => {
      const icon = item.querySelector(".di-icon");
      if (icon) icon.style.transform = "";
    });
    dock.addEventListener("mousemove", (event) => event.stopImmediatePropagation(), true);
    dock.addEventListener("pointermove", (event) => {
      if (compactViewport.matches || reducedMotion.matches) return;
      if (dockFrame) cancelAnimationFrame(dockFrame);
      dockFrame = requestAnimationFrame(() => {
        items.forEach((item) => {
          const icon = item.querySelector(".di-icon");
          if (!icon) return;
          const box = item.getBoundingClientRect();
          const distance = Math.abs(event.clientX - (box.left + box.width / 2));
          const influence = Math.max(0, 1 - distance / 112);
          const eased = Math.sin(influence * Math.PI / 2);
          icon.style.transform = `translate3d(0, ${Math.round(-10 * eased)}px, 0) scale(${(1 + .28 * eased).toFixed(3)})`;
        });
      });
    });
    dock.addEventListener("pointerleave", resetDock);
    items.forEach((item) => {
      item.tabIndex = 0;
      item.setAttribute("role", "button");
      item.setAttribute("aria-label", `${item.dataset.name || "Tool"} in tech stack`);
      const select = () => {
        items.forEach((other) => {
          other.classList.toggle("macos-dock-active", other === item);
          other.setAttribute("aria-pressed", String(other === item));
        });
      };
      item.addEventListener("click", select);
      item.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        select();
      });
    });
  }

  // Apple-style controls backed by the user's complete YouTube playlist.
  (() => {
    const widget = document.getElementById("music-widget");
    const playerRoot = document.getElementById("ytPlayer");
    if (!widget || !playerRoot) return;

    const PLAYLIST_ID = "PLJ-7-5isEZNPF5XvAZnIN1bDVNxabK_HR";
    const PLAYLIST = [
      { id:"t7tq5lKj5PM", title:"2Pac - Close my Eyes", artist:"Promonkey82", duration:251 },
      { id:"7v0_uipNGao", title:"TOXIC", artist:"AP DHILLON · INTENSE", duration:187 },
      { id:"ou_KeozfhgQ", title:"My Heart, My Life", artist:"Nusrat Fateh Ali Khan · Michael Brook", duration:332 },
      { id:"4dkss90fdPc", title:"TU", artist:"TALWIINDER · SANJOY", duration:132 },
      { id:"3cchY1q44bk", title:"Gustakhiyan", artist:"Davi Singh · The Landers", duration:161 },
      { id:"fKYjJRFTefU", title:"Dil - BOHEMIA (Official Audio)", artist:"BOHEMIA · Devika", duration:297 },
      { id:"90FfrXh7cD4", title:"Chehra Gulabi Nazrein Sharabi", artist:"StudioNCR", duration:195 },
      { id:"dlvuzoECCwg", title:"Chinnamma Chilakkamma", artist:"A.R. Rahman", duration:144 }
    ];
    const track = document.getElementById("ytTrack");
    const artist = document.getElementById("ytArtist");
    const cover = document.getElementById("ytCover");
    const elapsed = document.getElementById("ytElapsed");
    const remaining = document.getElementById("ytRemaining");
    const progress = document.getElementById("ytProgress");
    const previous = document.getElementById("ytPrevious");
    const play = document.getElementById("ytPlay");
    const next = document.getElementById("ytNext");
    const open = document.getElementById("ytOpen");
    const glyph = play?.querySelector(".mp-play-glyph");
    const controls = [previous, play, next].filter(Boolean);
    let player = null;
    let progressTimer = 0;
    let scrubbing = false;
    let currentIndex = 1;
    let restrictedSkips = 0;
    let resumeAfterChange = false;
    let pendingAutoStart = Boolean(window.__macosAutoplayRequested);

    const formatTime = (seconds) => {
      const safe = Math.max(0, Math.floor(Number(seconds) || 0));
      return `${Math.floor(safe / 60)}:${String(safe % 60).padStart(2, "0")}`;
    };

    const updateMetadata = () => {
      const item = PLAYLIST[currentIndex];
      if (track) track.textContent = item.title;
      if (artist) artist.textContent = item.artist;
      if (cover) cover.src = `https://i.ytimg.com/vi/${item.id}/hqdefault.jpg`;
      if (open) open.href = `https://www.youtube.com/watch?v=${item.id}&list=${PLAYLIST_ID}&index=${currentIndex + 1}`;
      widget.dataset.youtubeIndex = String(currentIndex);
    };

    const updateTimeline = () => {
      if (!player?.getDuration || !progress) return;
      const duration = Number(player.getDuration()) || PLAYLIST[currentIndex].duration;
      const current = Number(player.getCurrentTime()) || 0;
      const ratio = duration > 0 ? Math.min(1, current / duration) : 0;
      if (!scrubbing) progress.value = String(Math.round(ratio * 1000));
      progress.style.setProperty("--progress", `${ratio * 100}%`);
      if (elapsed) elapsed.textContent = formatTime(current);
      if (remaining) remaining.textContent = `−${formatTime(duration - current)}`;
    };

    const setPlaying = (isPlaying) => {
      widget.classList.toggle("playing", isPlaying);
      if (glyph) glyph.textContent = "";
      if (play) play.setAttribute("aria-label", isPlaying ? "Pause" : "Play");
      window.clearInterval(progressTimer);
      progressTimer = window.setInterval(updateTimeline, isPlaying ? 250 : 800);
      updateTimeline();
    };

    const selectTrack = (nextIndex, autoplay = false) => {
      currentIndex = (nextIndex + PLAYLIST.length) % PLAYLIST.length;
      resumeAfterChange = autoplay;
      restrictedSkips = 0;
      setPlaying(false);
      updateMetadata();
      if (progress) {
        progress.value = "0";
        progress.style.setProperty("--progress", "0%");
      }
      if (elapsed) elapsed.textContent = "0:00";
      if (remaining) remaining.textContent = `−${formatTime(PLAYLIST[currentIndex].duration)}`;
      if (!player) return;
      if (autoplay) player.loadVideoById(PLAYLIST[currentIndex].id);
      else player.cueVideoById(PLAYLIST[currentIndex].id);
    };

    window.__startYouTubePlaylist = () => {
      window.__macosAutoplayRequested = true;
      pendingAutoStart = true;
      resumeAfterChange = true;
      if (player) selectTrack(currentIndex, true);
    };
    window.__pauseYouTubePlaylist = () => {
      window.__macosAutoplayRequested = false;
      pendingAutoStart = false;
      resumeAfterChange = false;
      player?.pauseVideo?.();
    };

    const onReady = (event) => {
      player = event.target;
      window.__youtubePlaylistPlayer = player;
      widget.dataset.youtubeState = "ready";
      controls.forEach((control) => { control.disabled = false; });
      selectTrack(currentIndex, pendingAutoStart);
      pendingAutoStart = false;
    };

    const onStateChange = (event) => {
      const state = window.YT?.PlayerState;
      setPlaying(event.data === state?.PLAYING);
      if (event.data === state?.PLAYING) {
        restrictedSkips = 0;
        resumeAfterChange = true;
      }
      if (event.data === state?.ENDED) selectTrack(currentIndex + 1, true);
      if ([state?.CUED, state?.PLAYING, state?.PAUSED, state?.ENDED].includes(event.data)) {
        widget.classList.add("youtube-visual-ready");
        delete widget.dataset.youtubeError;
        updateMetadata();
      }
    };

    const onError = (event) => {
      window.__youtubePlaylistError = event?.data;
      widget.dataset.youtubeError = String(event?.data ?? "unknown");
      setPlaying(false);
      if ([101, 150].includes(event?.data) && restrictedSkips < PLAYLIST.length - 1) {
        restrictedSkips += 1;
        currentIndex = (currentIndex + 1) % PLAYLIST.length;
        updateMetadata();
        if (artist) artist.textContent += " · loading";
        window.setTimeout(() => {
          if (resumeAfterChange) event.target?.loadVideoById?.(PLAYLIST[currentIndex].id);
          else event.target?.cueVideoById?.(PLAYLIST[currentIndex].id);
        }, 260);
        return;
      }
      if (track) track.textContent = "Open playlist on YouTube";
      if (artist) artist.textContent = "Playback unavailable in this browser";
    };

    const createPlayer = () => {
      if (player || !window.YT?.Player) return;
      player = new window.YT.Player("ytPlayer", {
        width: "640",
        height: "360",
        videoId: PLAYLIST[currentIndex].id,
        playerVars: {
          controls: 0,
          disablekb: 1,
          fs: 0,
          playsinline: 1,
          rel: 0,
          origin: window.location.origin
        },
        events: { onReady, onStateChange, onError }
      });
    };

    previous?.addEventListener("click", () => selectTrack(currentIndex - 1, widget.classList.contains("playing")));
    next?.addEventListener("click", () => selectTrack(currentIndex + 1, widget.classList.contains("playing")));
    play?.addEventListener("click", () => {
      if (!player?.getPlayerState) return;
      const isPlaying = player.getPlayerState() === window.YT?.PlayerState?.PLAYING;
      if (isPlaying) {
        resumeAfterChange = false;
        setPlaying(false);
        player.pauseVideo();
      } else {
        resumeAfterChange = true;
        setPlaying(true);
        player.playVideo();
      }
    });
    progress?.addEventListener("input", () => {
      scrubbing = true;
      const ratio = Number(progress.value) / 1000;
      progress.style.setProperty("--progress", `${ratio * 100}%`);
      const duration = Number(player?.getDuration?.()) || 0;
      if (elapsed) elapsed.textContent = formatTime(duration * ratio);
      if (remaining) remaining.textContent = `−${formatTime(duration * (1 - ratio))}`;
    });
    progress?.addEventListener("change", () => {
      const duration = Number(player?.getDuration?.()) || 0;
      player?.seekTo?.(duration * (Number(progress.value) / 1000), true);
      scrubbing = false;
      updateTimeline();
    });

    if (window.YT?.Player) createPlayer();
    else {
      const previousReady = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = () => {
        if (typeof previousReady === "function") previousReady();
        createPlayer();
      };
      if (!document.querySelector('script[src="https://www.youtube.com/iframe_api"]')) {
        const script = document.createElement("script");
        script.src = "https://www.youtube.com/iframe_api";
        script.async = true;
        document.head.appendChild(script);
      }
    }
  })();

  // A compact profile disclosure: click/tap reveals a concise introduction,
  // while a portrait-anchored coachmark keeps the interaction discoverable.
  const profile = document.getElementById("brand-stack");
  const profileTrigger = document.getElementById("heroProfileTrigger");
  const profileDetails = document.getElementById("heroProfileDetails");
  const profileCoachmark = document.getElementById("heroProfileCoachmark");
  const setProfileCoachmarkVisible = (visible) => {
    profile?.classList.toggle("coachmark-visible", visible);
    profileCoachmark?.setAttribute("aria-hidden", String(!visible));
  };
  const setProfileOpen = (open) => {
    if (!profile || !profileTrigger || !profileDetails) return;
    profile.classList.toggle("profile-open", open);
    profileTrigger.setAttribute("aria-expanded", String(open));
    profileTrigger.setAttribute("aria-label", `AI Engineer profile, ${open ? "hide" : "show"} details`);
    profileDetails.setAttribute("aria-hidden", String(!open));
    setProfileCoachmarkVisible(!open && document.body.classList.contains("desktop-unlocked"));
    window.requestAnimationFrame(() => window.__syncBrandStack?.());
  };

  profileTrigger?.addEventListener("click", () => setProfileOpen(!profile?.classList.contains("profile-open")));
  document.addEventListener("click", (event) => {
    if (profile?.classList.contains("profile-open") && !profile.contains(event.target)) setProfileOpen(false);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && profile?.classList.contains("profile-open")) {
      setProfileOpen(false);
      profileTrigger?.focus({ preventScroll: true });
    }
  });
  const profileUnlockObserver = new MutationObserver(() => {
    if (document.body.classList.contains("desktop-unlocked")) {
      setProfileCoachmarkVisible(!profile?.classList.contains("profile-open"));
    }
    else {
      setProfileCoachmarkVisible(false);
      if (profile?.classList.contains("profile-open")) setProfileOpen(false);
    }
  });
  profileUnlockObserver.observe(document.body, { attributes: true, attributeFilter: ["class"] });
  setProfileCoachmarkVisible(document.body.classList.contains("desktop-unlocked") && !profile?.classList.contains("profile-open"));

  // Simple, intentionally non-app-like widgets requested for the desktop.
  const toggleDesktopWidget = (event) => {
    const widget = event.currentTarget;
    const selected = widget.classList.toggle("is-selected");
    const button = widget.querySelector("button");
    button?.setAttribute("aria-pressed", String(selected));
  };
  document.getElementById("map-widget")?.addEventListener("click", toggleDesktopWidget);
  document.getElementById("photo-widget")?.addEventListener("click", toggleDesktopWidget);

  // A live local clock, aligned to real minute boundaries and refreshed on tab return.
  const clockTime = document.getElementById("appleClock");
  const clockDate = document.getElementById("appleClockDate");
  let clockTimer = 0;
  const updateClock = () => {
    if (!clockTime || !clockDate) return;
    const now = new Date();
    clockTime.textContent = new Intl.DateTimeFormat(undefined, {
      hour: "numeric", minute: "2-digit", hour12: false
    }).format(now);
    clockTime.dateTime = now.toISOString();
    clockDate.textContent = new Intl.DateTimeFormat(undefined, {
      weekday: "short", month: "short", day: "numeric"
    }).format(now);
    document.getElementById("clock-widget")?.setAttribute("aria-label", `Local time ${clockTime.textContent}`);
    window.clearTimeout(clockTimer);
    clockTimer = window.setTimeout(updateClock, 60000 - (Date.now() % 60000) + 25);
  };
  updateClock();
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) updateClock();
  });

  // Keep the new desktop objects in the existing mobile widget drawer at compact widths.
  const widgetStack = document.getElementById("apple-widget-stack");
  const mobileDrawerBody = document.getElementById("mdBody");
  if (widgetStack && mobileDrawerBody) {
    const origin = { parent: widgetStack.parentNode, next: widgetStack.nextSibling };
    const moveWidgetStack = () => {
      if (compactViewport.matches) mobileDrawerBody.appendChild(widgetStack);
      else if (origin.next?.parentNode === origin.parent) origin.parent.insertBefore(widgetStack, origin.next);
      else origin.parent.appendChild(widgetStack);
    };
    moveWidgetStack();
    compactViewport.addEventListener?.("change", moveWidgetStack);
  }
})();
