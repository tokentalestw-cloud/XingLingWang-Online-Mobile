/* One viewport coordinator. Loaded in the head, before the game can first paint. */
(function () {
  'use strict';
  const root = document.documentElement;
  const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  window.XLW_IS_IOS = isIOS;
  const touchDevice = () => navigator.maxTouchPoints > 0 ||
    window.matchMedia('(pointer: coarse)').matches || /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  const standalone = () => navigator.standalone === true || window.matchMedia('(display-mode: standalone)').matches;
  const fullscreen = () => document.fullscreenElement || document.webkitFullscreenElement;
  let previous = '';

  function applyOrientation() {
    const portrait = window.innerHeight > window.innerWidth;
    const rotate = portrait && (touchDevice() || window.innerWidth <= 600);
    const width = rotate ? window.innerHeight : window.innerWidth;
    const height = rotate ? window.innerWidth : window.innerHeight;
    const key = `${rotate}:${width}:${height}`;
    root.classList.toggle('xlw-force-landscape', rotate);
    root.classList.toggle('xlw-mobile-viewport', touchDevice() || window.innerWidth <= 1100);
    if (document.body) document.body.classList.toggle('xlw-force-landscape', rotate);
    if (key !== previous) {
      previous = key;
      root.style.setProperty('--xlw-ui-width', width + 'px');
      root.style.setProperty('--xlw-ui-height', height + 'px');
    }
  }

  function refresh() {
    // Update axes synchronously; adjustBoardScale coalesces all events into one frame.
    applyOrientation();
    if (typeof window.adjustBoardScale === 'function') window.adjustBoardScale();
  }
  window.xlwApplyViewportOrientation = applyOrientation;
  window.xlwCheckLandscapeOrientation = refresh;

  let fullscreenPending = null;
  let lockPending = null;
  let lockAttempted = false;
  let lockSucceeded = false;
  function lockLandscape() {
    if (lockPending) return lockPending;
    if (lockAttempted) return Promise.resolve(lockSucceeded);
    if (!fullscreen() && !standalone()) return Promise.resolve(false);
    const orientation = window.screen && window.screen.orientation;
    if (!orientation || typeof orientation.lock !== 'function') return Promise.resolve(false);
    lockAttempted = true;
    try {
      lockPending = Promise.resolve(orientation.lock('landscape')).then(() => { lockSucceeded = true; return true; }, () => false)
        .finally(() => { lockPending = null; refresh(); });
    } catch (_) { lockPending = null; return Promise.resolve(false); }
    return lockPending;
  }

  window.xlwAutoLandscapeFullscreen = function () {
    refresh();
    if (!touchDevice()) return Promise.resolve(false);
    if (fullscreenPending) return fullscreenPending;
    if (fullscreen() || standalone()) return lockLandscape();
    const request = root.requestFullscreen || root.webkitRequestFullscreen || root.webkitRequestFullScreen;
    if (!request || document.fullscreenEnabled === false ||
        (navigator.userActivation && !navigator.userActivation.isActive)) return Promise.resolve(false);
    // Start the native request inside the user's gesture, before awaiting anything.
    try {
      const result = request.call(root, { navigationUI: 'hide' });
      fullscreenPending = Promise.resolve(result).then(() => lockLandscape(), () => false)
        .finally(() => { fullscreenPending = null; refresh(); });
    } catch (_) { return Promise.resolve(false); }
    return fullscreenPending;
  };
  window.xlwRequestFullScreen = window.xlwAutoLandscapeFullscreen;
  window.xlwLockOrientation = window.xlwAutoLandscapeFullscreen;

  function fullscreenChanged() {
    if (fullscreen()) lockLandscape();
    else { lockAttempted = false; lockSucceeded = false; lockPending = null; }
    refresh();
  }
  document.addEventListener('fullscreenchange', fullscreenChanged);
  document.addEventListener('webkitfullscreenchange', fullscreenChanged);
  window.addEventListener('resize', refresh, { passive: true });
  window.addEventListener('orientationchange', refresh, { passive: true });
  window.addEventListener('pageshow', refresh);
  if (window.visualViewport) window.visualViewport.addEventListener('resize', refresh, { passive: true });
  if (window.screen && window.screen.orientation && window.screen.orientation.addEventListener) {
    window.screen.orientation.addEventListener('change', refresh);
  }
  // Touch activation is available on pointerup, rather than touch pointerdown.
  window.addEventListener('pointerup', event => {
    if (event.isTrusted) window.xlwAutoLandscapeFullscreen();
  }, { once: true, passive: true });
  document.addEventListener('DOMContentLoaded', () => {
    refresh();
    if (standalone()) lockLandscape();
  }, { once: true });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
  applyOrientation();
})();
