/*
 * icons.js — a small hand-drawn SVG icon set for Kaggriculture.
 *
 * Replaces the emoji glyphs with clean, consistent vector art so the game
 * reads as a polished product rather than a toy. All icons share a 24x24
 * viewBox. Crop/nature icons carry their own fills; UI icons use currentColor
 * so CSS can tint them.
 */
(function (root) {
  "use strict";

  function svg(inner, size) {
    var s = size || 28;
    return '<svg viewBox="0 0 24 24" width="' + s + '" height="' + s +
      '" fill="none" xmlns="http://www.w3.org/2000/svg">' + inner + '</svg>';
  }

  // ---- crop stages ------------------------------------------------------- //
  var seed = svg(
    '<path d="M12 21v-6" stroke="#5b8c4e" stroke-width="2" stroke-linecap="round"/>' +
    '<path d="M12 16c-2.4 0-4.3-1.4-4.6-3.6C9.7 12.1 12 13.6 12 16z" fill="#7bb36a"/>' +
    '<path d="M12 15c1.9 0 3.4-1.4 3.6-3.4C13.3 11.8 12 13 12 15z" fill="#93c47d"/>');

  var sprout = svg(
    '<path d="M12 22V9" stroke="#3f7d4a" stroke-width="2" stroke-linecap="round"/>' +
    '<path d="M12 13C8.7 13 6 10.7 5.5 7 9.4 7.4 12 9.7 12 13z" fill="#5fa463"/>' +
    '<path d="M12 11c2.7 0 5-2 5.5-5.4C14 6 12 8 12 11z" fill="#7bc07d"/>');

  var wheat = svg(
    '<path d="M12 22V8" stroke="#8a6a1e" stroke-width="2" stroke-linecap="round"/>' +
    '<g fill="#d9a72e">' +
    '<ellipse cx="12" cy="5" rx="2" ry="3.1"/>' +
    '<ellipse cx="8.6" cy="8.3" rx="1.7" ry="2.8" transform="rotate(-28 8.6 8.3)"/>' +
    '<ellipse cx="15.4" cy="8.3" rx="1.7" ry="2.8" transform="rotate(28 15.4 8.3)"/>' +
    '<ellipse cx="8.9" cy="12" rx="1.7" ry="2.8" transform="rotate(-28 8.9 12)"/>' +
    '<ellipse cx="15.1" cy="12" rx="1.7" ry="2.8" transform="rotate(28 15.1 12)"/></g>');

  var corn = svg(
    '<path d="M8.5 4.5c4-2.2 8 1.6 7.2 8.4C15 19 8 21.5 8 21.5S5 6.5 8.5 4.5z" fill="#3f7d4a"/>' +
    '<ellipse cx="13" cy="12" rx="4.3" ry="7.6" fill="#e8be3c"/>' +
    '<path d="M11 7.5l3.8 1M10.4 10.5l4 1M10.2 13.5l4 1M10.6 16.5l3.6 1" stroke="#c2962a" stroke-width="0.9" stroke-linecap="round"/>');

  var tomato = svg(
    '<circle cx="12" cy="14.5" r="6.8" fill="#d9483a"/>' +
    '<circle cx="9.7" cy="12.5" r="1.9" fill="#e46b5c"/>' +
    '<path d="M12 8l-2.4-3M12 8l2.4-3M12 8V4.4" stroke="#4a8c3f" stroke-width="1.5" stroke-linecap="round"/>' +
    '<path d="M9 7.7c1.2-1 4.8-1 6 0-1.2 1-4.8 1-6 0z" fill="#5aa03f"/>');

  var rice = svg(
    '<path d="M12 22V9" stroke="#7d8a3e" stroke-width="2" stroke-linecap="round"/>' +
    '<g fill="#cdbb5a">' +
    '<ellipse cx="12" cy="6" rx="1.5" ry="2.8"/>' +
    '<ellipse cx="9.2" cy="9" rx="1.3" ry="2.5" transform="rotate(-30 9.2 9)"/>' +
    '<ellipse cx="14.8" cy="9" rx="1.3" ry="2.5" transform="rotate(30 14.8 9)"/>' +
    '<ellipse cx="9.6" cy="12.6" rx="1.3" ry="2.5" transform="rotate(-30 9.6 12.6)"/>' +
    '<ellipse cx="14.4" cy="12.6" rx="1.3" ry="2.5" transform="rotate(30 14.4 12.6)"/></g>');

  var weed = svg(
    '<path d="M12 22V10" stroke="#5a6b2e" stroke-width="2" stroke-linecap="round"/>' +
    '<path d="M12 14c-3.2-.6-5-3.6-5-3.6C10 10 12 11.6 12 14zM12 12.5c3.2-.6 5-3.6 5-3.6C14 8.5 12 10.1 12 12.5z" fill="#7c8a3a"/>' +
    '<circle cx="12" cy="7.5" r="2.3" fill="#9a7ab0"/><circle cx="12" cy="7.5" r="0.9" fill="#c9b3d9"/>');

  // farmer position marker — a straw hat
  var farmer = svg(
    '<ellipse cx="12" cy="16.5" rx="9" ry="3" fill="#caa14a"/>' +
    '<path d="M5.5 15.5c0-4.4 2.9-7.5 6.5-7.5s6.5 3.1 6.5 7.5" fill="#dcb45c"/>' +
    '<path d="M6.5 15.4c2.4-1.1 8.6-1.1 11 0" stroke="#a67d2c" stroke-width="1.1" stroke-linecap="round"/>' +
    '<path d="M5.5 15.5c3.6 1.4 9.9 1.4 13 0" stroke="#a67d2c" stroke-width="1" fill="none"/>', 30);

  var water = svg(
    '<path d="M12 3.5s5.5 6.4 5.5 10.2A5.5 5.5 0 0 1 6.5 13.7C6.5 9.9 12 3.5 12 3.5z" fill="#3f9fd4"/>' +
    '<path d="M9.5 13.5a2.5 2.5 0 0 0 2 2.4" stroke="#bfe3f5" stroke-width="1.2" stroke-linecap="round"/>', 16);

  var CROPS = { WHEAT: wheat, CORN: corn, TOMATO: tomato, RICE: rice };

  // ---- UI icons (currentColor) ------------------------------------------- //
  var soundOn = svg('<path d="M4 9v6h4l5 4V5L8 9H4z" fill="currentColor"/><path d="M16 8.5a4 4 0 0 1 0 7M18.5 6a7 7 0 0 1 0 12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>', 20);
  var soundOff = svg('<path d="M4 9v6h4l5 4V5L8 9H4z" fill="currentColor"/><path d="M17 9l4 6M21 9l-4 6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>', 20);
  var help = svg('<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/><path d="M9.5 9.5a2.5 2.5 0 0 1 4.5 1.5c0 1.6-2 2-2 3.2" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><circle cx="12" cy="17" r="1.1" fill="currentColor"/>', 20);
  var coin = svg('<circle cx="12" cy="12" r="9" fill="#e0b23c" stroke="#b98d22" stroke-width="1.5"/><path d="M12 17V8" stroke="#8a6a16" stroke-width="1.6" stroke-linecap="round"/><g fill="#8a6a16"><ellipse cx="12" cy="7.4" rx="1.1" ry="1.7"/><ellipse cx="10" cy="9.4" rx="0.9" ry="1.5" transform="rotate(-28 10 9.4)"/><ellipse cx="14" cy="9.4" rx="0.9" ry="1.5" transform="rotate(28 14 9.4)"/></g>', 20);

  // ---- achievement badges ------------------------------------------------ //
  var badges = {
    wheat: wheat,
    trophy: svg('<path d="M7 4h10v3a5 5 0 0 1-10 0V4z" fill="#e0b23c"/><path d="M7 5H4.5v1.5A3 3 0 0 0 7 9.4M17 5h2.5v1.5A3 3 0 0 1 17 9.4" stroke="#b98d22" stroke-width="1.4"/><path d="M10 12h4v3h-4z" fill="#c99a2e"/><path d="M8 19h8v1.5H8z" fill="#b98d22"/>', 30),
    leaf: svg('<path d="M5 19c0-8 6-13 14-13 0 8-6 13-14 13z" fill="#5fa463"/><path d="M8 16c3-4 6-6 9-7" stroke="#2f6b3f" stroke-width="1.4" stroke-linecap="round"/>', 30),
    coins: svg('<ellipse cx="10" cy="9" rx="6" ry="2.6" fill="#e0b23c"/><path d="M4 9v3c0 1.4 2.7 2.6 6 2.6s6-1.2 6-2.6V9" stroke="#b98d22" stroke-width="1.3" fill="none"/><ellipse cx="15" cy="15" rx="6" ry="2.6" fill="#e8c25a"/><path d="M9 15v3c0 1.4 2.7 2.6 6 2.6s6-1.2 6-2.6v-3" stroke="#b98d22" stroke-width="1.3" fill="none"/>', 30),
    medal: svg('<path d="M8 3l2 6M16 3l-2 6" stroke="#8a94a6" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="15" r="6" fill="#e0b23c" stroke="#b98d22" stroke-width="1.4"/><path d="M12 12l1 2 2 .3-1.5 1.5.4 2-1.9-1-1.9 1 .4-2L9 14.3l2-.3z" fill="#fff3d0"/>', 30),
    flame: svg('<path d="M12 3c1 3-2 4-2 7 0 1 1 2 2 2s2-1 2-2c2 2 3 4 3 6a5 5 0 0 1-10 0c0-4 3-6 5-9z" fill="#e07a3c"/><path d="M12 20a2.6 2.6 0 0 0 2.6-2.6c0-1.6-2.6-3.4-2.6-3.4s-2.6 1.8-2.6 3.4A2.6 2.6 0 0 0 12 20z" fill="#f3b54a"/>', 30),
    shield: svg('<path d="M12 3l7 2.5V11c0 4.5-3 8-7 9.5C8 19 5 15.5 5 11V5.5L12 3z" fill="#3f7d5c"/><path d="M9 12l2 2 4-4.5" stroke="#eaf5ec" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>', 30),
    basket: svg('<path d="M4 10h16l-1.5 9H5.5L4 10z" fill="#b57b46"/><path d="M4 10h16" stroke="#8a5c30" stroke-width="1.4"/><path d="M8 10l2-5M16 10l-2-5" stroke="#8a5c30" stroke-width="1.5" stroke-linecap="round"/><path d="M8 13v3M12 13v3M16 13v3" stroke="#8a5c30" stroke-width="1.1"/>', 30),
    lock: svg('<rect x="5" y="10" width="14" height="10" rx="2" fill="#9aa1ad"/><path d="M8 10V8a4 4 0 0 1 8 0v2" stroke="#9aa1ad" stroke-width="1.8"/>', 30)
  };

  root.ICONS = {
    svg: svg,
    crop: function (type, ripe) { return ripe ? (CROPS[type] || wheat) : sprout; },
    seed: seed, sprout: sprout, wheat: wheat, weed: weed, farmer: farmer, water: water,
    soundOn: soundOn, soundOff: soundOff, help: help, coin: coin,
    badge: function (key) { return badges[key] || badges.trophy; }
  };
})(typeof window !== "undefined" ? window : this);
