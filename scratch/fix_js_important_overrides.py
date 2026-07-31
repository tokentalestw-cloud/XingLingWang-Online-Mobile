# -*- coding: utf-8 -*-
import sys, re

def apply_overrides():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    idx_path = 'static/index.html'

    js_content = open(js_path, encoding='utf-8').read()

    # 1. Update window.xlwChooseMode to use style.setProperty
    old_choose_mode = """window.xlwChooseMode = function(mode) {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.classList.add("xlw-welcome-fadeout");
    setTimeout(() => {
      overlay.style.display = "none";
    }, 450);
  }"""

    new_choose_mode = """window.xlwChooseMode = function(mode) {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.classList.add("xlw-welcome-fadeout");
    setTimeout(() => {
      overlay.style.setProperty("display", "none", "important");
    }, 450);
  }"""

    # 2. Update window.xlwReturnToTitle to use style.setProperty
    old_return_title = """window.xlwReturnToTitle = function() {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.classList.remove("xlw-welcome-fadeout");
    overlay.style.display = "flex";
  }"""

    new_return_title = """window.xlwReturnToTitle = function() {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.classList.remove("xlw-welcome-fadeout");
    overlay.style.setProperty("display", "flex", "important");
  }"""

    # 3. Update showWelcomeOverlayOnLoad to use style.setProperty
    old_onload = """function showWelcomeOverlayOnLoad() {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.style.display = "flex";
    console.log("Welcome overlay displayed on load!");
  }
}"""

    new_onload = """function showWelcomeOverlayOnLoad() {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.style.setProperty("display", "flex", "important");
    console.log("Welcome overlay displayed on load!");
  }
}"""

    # Perform replacements
    js_content = js_content.replace(old_choose_mode, new_choose_mode)
    js_content = js_content.replace(old_return_title, new_return_title)
    js_content = js_content.replace(old_onload, new_onload)

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Applied style.setProperty overrides to game_v8.js successfully!")

    # Update cache-buster in static/index.html to v=17.80-js-important-forced
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=17.80-js-important-forced', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=17.80-js-important-forced', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_overrides()
