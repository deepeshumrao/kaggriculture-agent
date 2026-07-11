/*
 * profiles.js — client-side player profiles for Kaggriculture.
 *
 * GitHub Pages is static, so profiles live in localStorage (per browser).
 * No server, no password hashing over a network — this is a friendly local
 * "who's playing" system with persistent stats, avatars, and achievements,
 * not a security boundary. A 4-digit PIN is optional and only gates profile
 * switching on a shared device.
 *
 * Exposes window.Profiles with a small CRUD + stats API.
 */
(function (root) {
  "use strict";

  var STORE_KEY = "kagg_profiles_v1";
  var ACTIVE_KEY = "kagg_active_profile_v1";

  // Avatars are refined color swatches; the UI renders a monogram disc from the
  // player's initial on top of the chosen color (no emoji).
  var AVATARS = ["#3a7d5c", "#2b6cb0", "#b7791f", "#9b3d5e", "#6b4fa0",
                 "#2c7a7b", "#a8552c", "#4a5568", "#5a7d2c", "#8a3b3b"];

  // Achievement catalog. `icon` is a key resolved by ICONS.badge() in the UI.
  var ACHIEVEMENTS = [
    { id: "first_harvest", icon: "wheat", name: "First Harvest", desc: "Harvest your first crop.",
      check: function (s) { return s.totalHarvests >= 1; } },
    { id: "first_win", icon: "trophy", name: "First Victory", desc: "Win your first game.",
      check: function (s) { return s.wins >= 1; } },
    { id: "green_thumb", icon: "leaf", name: "Green Thumb", desc: "Harvest 100 crops in total.",
      check: function (s) { return s.totalHarvests >= 100; } },
    { id: "rich_farmer", icon: "coins", name: "Rich Farmer", desc: "Finish a game with score 3000+.",
      check: function (s) { return s.bestScore >= 3000; } },
    { id: "veteran", icon: "medal", name: "Veteran", desc: "Play 10 games.",
      check: function (s) { return s.games >= 10; } },
    { id: "streak3", icon: "flame", name: "On Fire", desc: "Win 3 games in a row.",
      check: function (s) { return s.bestStreak >= 3; } },
    { id: "beat_hard", icon: "shield", name: "No Sweat", desc: "Beat the AI on Hard difficulty.",
      check: function (s, c) { return c && c.won && c.difficulty === "hard" && c.mode === "single"; } },
    { id: "crop_master", icon: "basket", name: "Crop Master", desc: "Harvest every crop type at least once.",
      check: function (s) { var k = Object.keys(s.cropsHarvested || {}); return k.length >= 4; } }
  ];

  // ---- storage helpers --------------------------------------------------- //
  function readAll() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY)) || {}; }
    catch (e) { return {}; }
  }
  function writeAll(map) {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(map)); } catch (e) {}
  }
  function uid() {
    return "p_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 7);
  }

  function blankStats() {
    return {
      games: 0, wins: 0, losses: 0, ties: 0,
      totalHarvests: 0, totalEarnings: 0,
      bestScore: 0, bestStreak: 0, currentStreak: 0,
      cropsHarvested: {}   // { WHEAT: n, CORN: n, ... }
    };
  }

  // ---- public API -------------------------------------------------------- //
  var Profiles = {
    AVATARS: AVATARS,
    ACHIEVEMENTS: ACHIEVEMENTS,

    list: function () {
      var map = readAll();
      return Object.keys(map).map(function (id) { return map[id]; })
        .sort(function (a, b) { return (b.lastPlayed || 0) - (a.lastPlayed || 0); });
    },

    get: function (id) { return readAll()[id] || null; },

    create: function (name, avatar, pin) {
      name = (name || "").trim().slice(0, 20) || "Farmer";
      var map = readAll();
      var id = uid();
      map[id] = {
        id: id, name: name, avatar: avatar || AVATARS[0],
        pin: pin || "", created: Date.now(), lastPlayed: Date.now(),
        stats: blankStats(), achievements: []
      };
      writeAll(map);
      return map[id];
    },

    rename: function (id, name) {
      var map = readAll();
      if (map[id]) { map[id].name = (name || "").trim().slice(0, 20) || map[id].name; writeAll(map); }
      return map[id];
    },

    setAvatar: function (id, avatar) {
      var map = readAll();
      if (map[id]) { map[id].avatar = avatar; writeAll(map); }
      return map[id];
    },

    remove: function (id) {
      var map = readAll();
      delete map[id];
      writeAll(map);
      if (this.getActiveId() === id) this.clearActive();
    },

    checkPin: function (id, pin) {
      var p = this.get(id);
      if (!p) return false;
      if (!p.pin) return true;           // no pin set
      return p.pin === String(pin || "");
    },

    // active-profile session
    getActiveId: function () { try { return localStorage.getItem(ACTIVE_KEY) || null; } catch (e) { return null; } },
    setActive: function (id) { try { localStorage.setItem(ACTIVE_KEY, id); } catch (e) {} },
    clearActive: function () { try { localStorage.removeItem(ACTIVE_KEY); } catch (e) {} },
    getActive: function () { var id = this.getActiveId(); return id ? this.get(id) : null; },

    /*
     * Record a finished game against the active profile.
     * result = { won:bool, tie:bool, score:num, harvests:num,
     *            earnings:num, crops:{CROP:n}, mode, difficulty }
     * Returns { profile, newAchievements: [...] }.
     */
    recordGame: function (id, result) {
      var map = readAll();
      var p = map[id];
      if (!p) return { profile: null, newAchievements: [] };
      var s = p.stats || blankStats();

      s.games += 1;
      if (result.tie) { s.ties += 1; s.currentStreak = 0; }
      else if (result.won) { s.wins += 1; s.currentStreak += 1; s.bestStreak = Math.max(s.bestStreak, s.currentStreak); }
      else { s.losses += 1; s.currentStreak = 0; }

      s.totalHarvests += (result.harvests || 0);
      s.totalEarnings += (result.earnings || 0);
      s.bestScore = Math.max(s.bestScore, result.score || 0);
      s.cropsHarvested = s.cropsHarvested || {};
      var crops = result.crops || {};
      for (var c in crops) { if (crops[c] > 0) s.cropsHarvested[c] = (s.cropsHarvested[c] || 0) + crops[c]; }

      p.stats = s;
      p.lastPlayed = Date.now();

      // evaluate achievements
      var earned = p.achievements || [];
      var newly = [];
      var ctx = { won: !!result.won, difficulty: result.difficulty, mode: result.mode };
      ACHIEVEMENTS.forEach(function (a) {
        if (earned.indexOf(a.id) === -1 && a.check(s, ctx)) { earned.push(a.id); newly.push(a); }
      });
      p.achievements = earned;

      writeAll(map);
      return { profile: p, newAchievements: newly };
    },

    winRate: function (p) {
      if (!p || !p.stats || p.stats.games === 0) return 0;
      return Math.round((p.stats.wins / p.stats.games) * 100);
    }
  };

  root.Profiles = Profiles;
  if (typeof module !== "undefined" && module.exports) module.exports = Profiles;
})(typeof window !== "undefined" ? window : this);
