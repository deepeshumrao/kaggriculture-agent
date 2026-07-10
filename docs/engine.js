/*
 * engine.js — a faithful browser/Node port of the Kaggriculture real-protocol
 * simulator (src/kaggriculture_agent/real/local_env.py) and decision policy
 * (real/brain.py). Pure, dependency-free, deterministic-by-seed.
 *
 * The RNG is a port of CPython's Mersenne Twister (MT19937) with the same
 * seeding (init_by_array), the same random() (genrand_res53) and the same
 * choice() (_randbelow via getrandbits). This makes the in-browser game
 * reproduce the exact scores documented for the Python build (e.g. seed 0 ->
 * 3005 vs idle 100), so the online demo and the write-up agree.
 *
 * Works both as an ES-less global (browser <script>) and via module.exports
 * (Node, for the validation test).
 */
(function (root) {
  "use strict";

  // ---- 32-bit unsigned multiply without precision loss ------------------- //
  function mul32(a, b) {
    var aHi = (a >>> 16) & 0xffff, aLo = a & 0xffff;
    return (((aHi * b) << 16) + aLo * b) >>> 0;
  }

  // ---- MT19937, matching CPython's _randommodule ------------------------- //
  var N = 624, M = 397,
    MATRIX_A = 0x9908b0df, UPPER = 0x80000000, LOWER = 0x7fffffff;

  function MT(seed) {
    this.mt = new Uint32Array(N);
    this.mti = N + 1;
    this.seedInt(seed >>> 0);
  }
  MT.prototype.initGenrand = function (s) {
    var mt = this.mt;
    mt[0] = s >>> 0;
    for (var i = 1; i < N; i++) {
      var prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = (mul32(1812433253, prev) + i) >>> 0;
    }
    this.mti = N;
  };
  // init_by_array with the key CPython builds for a non-negative int seed.
  MT.prototype.seedInt = function (n) {
    var key = n === 0 ? [0] : [];
    while (n > 0) { key.push(n >>> 0); n = Math.floor(n / 4294967296); }
    this.initByArray(key);
  };
  MT.prototype.initByArray = function (key) {
    this.initGenrand(19650218);
    var mt = this.mt, i = 1, j = 0;
    var k = Math.max(N, key.length);
    for (; k; k--) {
      var p = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = (((mt[i] ^ mul32(p, 1664525)) >>> 0) + key[j] + j) >>> 0;
      i++; j++;
      if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
      if (j >= key.length) j = 0;
    }
    for (k = N - 1; k; k--) {
      var q = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = (((mt[i] ^ mul32(q, 1566083941)) >>> 0) - i) >>> 0;
      i++;
      if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
    }
    mt[0] = 0x80000000;
  };
  MT.prototype.genrandInt32 = function () {
    var mt = this.mt, y, kk;
    if (this.mti >= N) {
      for (kk = 0; kk < N - M; kk++) {
        y = (mt[kk] & UPPER) | (mt[kk + 1] & LOWER);
        mt[kk] = (mt[kk + M] ^ (y >>> 1) ^ ((y & 1) ? MATRIX_A : 0)) >>> 0;
      }
      for (; kk < N - 1; kk++) {
        y = (mt[kk] & UPPER) | (mt[kk + 1] & LOWER);
        mt[kk] = (mt[kk + (M - N)] ^ (y >>> 1) ^ ((y & 1) ? MATRIX_A : 0)) >>> 0;
      }
      y = (mt[N - 1] & UPPER) | (mt[0] & LOWER);
      mt[N - 1] = (mt[M - 1] ^ (y >>> 1) ^ ((y & 1) ? MATRIX_A : 0)) >>> 0;
      this.mti = 0;
    }
    y = mt[this.mti++];
    y ^= y >>> 11;
    y = (y ^ ((y << 7) & 0x9d2c5680)) >>> 0;
    y = (y ^ ((y << 15) & 0xefc60000)) >>> 0;
    y ^= y >>> 18;
    return y >>> 0;
  };
  MT.prototype.random = function () {
    var a = this.genrandInt32() >>> 5, b = this.genrandInt32() >>> 6;
    return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0);
  };
  MT.prototype.getrandbits = function (k) { // k <= 32
    return this.genrandInt32() >>> (32 - k);
  };
  MT.prototype.randbelow = function (n) {
    if (n <= 0) return 0;
    var k = n.toString(2).length; // bit_length
    var r = this.getrandbits(k);
    while (r >= n) r = this.getrandbits(k);
    return r;
  };
  MT.prototype.choice = function (seq) { return seq[this.randbelow(seq.length)]; };

  // ---- protocol constants ------------------------------------------------ //
  var P = {
    NORTH: "NORTH", SOUTH: "SOUTH", EAST: "EAST", WEST: "WEST",
    WATER: "WATER", HARVEST: "HARVEST", DIG: "DIG", PLANT: "PLANT", PASS: "PASS",
    KIND_PLANT: "PLANT", KIND_WEED: "WEED", BUY_SEED: "BUY_SEED", SELL: "SELL"
  };
  P.MOVES = [P.NORTH, P.SOUTH, P.EAST, P.WEST];
  function stepToward(fx, fy, tx, ty) {
    if (fx < tx) return P.EAST;
    if (fx > tx) return P.WEST;
    if (fy < ty) return P.SOUTH;
    if (fy > ty) return P.NORTH;
    return P.PASS;
  }

  // ---- mechanics (mirrors local_env.Mechanics) --------------------------- //
  var MECH = {
    farm_size: 5, turns_per_day: 24, max_days: 30, mature_days: 2,
    weed_prob_per_day: 0.30, dry_yield_factor: 0.5,
    crops: {
      WHEAT: { seed_cost: 10.0, sell_price: 15.0, base_yield: 3.0, grow_days: 2 },
      CORN: { seed_cost: 15.0, sell_price: 26.0, base_yield: 3.0, grow_days: 3 },
      TOMATO: { seed_cost: 20.0, sell_price: 35.0, base_yield: 2.5, grow_days: 4 },
      RICE: { seed_cost: 12.0, sell_price: 18.0, base_yield: 3.5, grow_days: 3 }
    },
    start_money: 100.0, start_seeds: { WHEAT: 4 }
  };

  function setDifficulty(level) {
    if (level === 'easy') {
      MECH.start_money = 150.0;
      MECH.weed_prob_per_day = 0.20;
      MECH.crops.WHEAT.sell_price = 18.0;
      MECH.crops.CORN.sell_price = 30.0;
      MECH.crops.TOMATO.sell_price = 40.0;
      MECH.crops.RICE.sell_price = 22.0;
    } else if (level === 'hard') {
      MECH.start_money = 80.0;
      MECH.weed_prob_per_day = 0.45;
      MECH.crops.WHEAT.sell_price = 12.0;
      MECH.crops.CORN.sell_price = 22.0;
      MECH.crops.TOMATO.sell_price = 30.0;
      MECH.crops.RICE.sell_price = 15.0;
    } else { // medium (default)
      MECH.start_money = 100.0;
      MECH.weed_prob_per_day = 0.30;
      MECH.crops.WHEAT.sell_price = 15.0;
      MECH.crops.CORN.sell_price = 26.0;
      MECH.crops.TOMATO.sell_price = 35.0;
      MECH.crops.RICE.sell_price = 18.0;
    }
  }

  // ---- environment ------------------------------------------------------- //
  function Env(seed, nPlayers) {
    this.mech = MECH;
    this.nPlayers = nPlayers || 2;
    this.rng = new MT((seed || 0) >>> 0);
    this.maxTurns = this.mech.turns_per_day * this.mech.max_days;
    this.reset();
  }
  Env.prototype.reset = function () {
    var n = this.mech.farm_size;
    this.turn = 0; this.day = 1; this.farms = [];
    for (var p = 0; p < this.nPlayers; p++) {
      var tiles = [];
      for (var y = 0; y < n; y++) { var row = []; for (var x = 0; x < n; x++) row.push(null); tiles.push(row); }
      this.farms.push({
        farmer: [0, 0], money: this.mech.start_money, tiles: tiles,
        seeds: Object.assign({}, this.mech.start_seeds), shed: {}
      });
    }
  };
  Env.prototype.done = function () { return this.turn >= this.maxTurns || this.day > this.mech.max_days; };
  Env.prototype.observe = function (player) {
    var self = this;
    return {
      player: player, day: this.day,
      farms: this.farms.map(function (f) { return self._publicFarm(f); }),
      private: {
        seeds: Object.assign({}, this.farms[player].seeds),
        shed: Object.assign({}, this.farms[player].shed)
      }
    };
  };
  Env.prototype._publicFarm = function (farm) {
    return {
      farmer: farm.farmer.slice(), money: farm.money,
      tiles: farm.tiles.map(function (row) {
        return row.map(function (t) {
          if (t === null) return null;
          if (t.kind === P.KIND_PLANT)
            return { kind: P.KIND_PLANT, planted_day: t.planted_day, watered_today: t.watered_today };
          return { kind: t.kind };
        });
      })
    };
  };
  Env.prototype.step = function (actions) {
    if (this.done()) return;
    for (var p = 0; p < actions.length; p++) {
      var a = actions[p];
      if (!a) continue;
      this._applyMarket(p, a.market || []);
      this._applyFarmer(p, (a.farmer && a.farmer.length) ? a.farmer : [P.PASS]);
    }
    this.turn += 1;
    if (this.turn % this.mech.turns_per_day === 0) this._endOfDay();
  };
  Env.prototype._applyMarket = function (p, ops) {
    var farm = this.farms[p];
    for (var i = 0; i < ops.length; i++) {
      var op = ops[i]; if (!op || !op.length) continue;
      var kind = op[0];
      if (kind === P.BUY_SEED && op.length >= 3) {
        var crop = op[1], qty = parseInt(op[2], 10);
        var spec = this.mech.crops[crop];
        if (!spec || qty <= 0) continue;
        var cost = qty * spec.seed_cost;
        if (farm.money >= cost) { farm.money -= cost; farm.seeds[crop] = (farm.seeds[crop] || 0) + qty; }
      } else if (kind === P.SELL && op.length >= 3) {
        var c = op[1], want = parseInt(op[2], 10);
        var sp = this.mech.crops[c]; var have = farm.shed[c] || 0;
        var q = Math.min(want, have);
        if (!sp || q <= 0) continue;
        farm.shed[c] = have - q; farm.money += q * sp.sell_price;
      }
    }
  };
  Env.prototype._applyFarmer = function (p, cmd) {
    if (!cmd || !cmd.length) return;
    var farm = this.farms[p], fx = farm.farmer[0], fy = farm.farmer[1];
    var verb = cmd[0], n = this.mech.farm_size;
    if (P.MOVES.indexOf(verb) !== -1) {
      if (verb === P.EAST) fx = Math.min(n - 1, fx + 1);
      else if (verb === P.WEST) fx = Math.max(0, fx - 1);
      else if (verb === P.SOUTH) fy = Math.min(n - 1, fy + 1);
      else if (verb === P.NORTH) fy = Math.max(0, fy - 1);
      farm.farmer = [fx, fy]; return;
    }
    var tile = farm.tiles[fy][fx];
    if (verb === P.WATER) {
      if (tile && tile.kind === P.KIND_PLANT && !tile.watered_today) { tile.watered_today = true; tile._waterings += 1; }
    } else if (verb === P.HARVEST) {
      var grow = (this.mech.crops[tile && tile.crop] || {}).grow_days || this.mech.mature_days;
      if (tile && tile.kind === P.KIND_PLANT && (this.day - tile.planted_day) >= grow) {
        var crop = tile.crop, spec = this.mech.crops[crop];
        var need = Math.max(1, grow);
        var waterRatio = Math.min(1.0, tile._waterings / need);
        var factor = this.mech.dry_yield_factor + (1.0 - this.mech.dry_yield_factor) * waterRatio;
        var amount = spec.base_yield * factor;
        farm.shed[crop] = (farm.shed[crop] || 0) + amount;
        farm.tiles[fy][fx] = null;
      }
    } else if (verb === P.DIG) {
      if (tile && tile.kind === P.KIND_WEED) farm.tiles[fy][fx] = null;
    } else if (verb === P.PLANT && cmd.length >= 2) {
      var cr = cmd[1];
      if (tile === null && (farm.seeds[cr] || 0) > 0) {
        farm.seeds[cr] -= 1;
        farm.tiles[fy][fx] = { kind: P.KIND_PLANT, crop: cr, planted_day: this.day, watered_today: false, _waterings: 0 };
      }
    }
  };
  Env.prototype._endOfDay = function () {
    this.day += 1;
    var n = this.mech.farm_size;
    for (var p = 0; p < this.farms.length; p++) {
      var farm = this.farms[p];
      for (var y = 0; y < n; y++) for (var x = 0; x < n; x++) {
        var t = farm.tiles[y][x];
        if (t && t.kind === P.KIND_PLANT) t.watered_today = false;
      }
      if (this.rng.random() < this.mech.weed_prob_per_day) {
        var empties = [];
        for (var yy = 0; yy < n; yy++) for (var xx = 0; xx < n; xx++)
          if (farm.tiles[yy][xx] === null) empties.push([xx, yy]);
        if (empties.length) {
          var cell = this.rng.choice(empties);
          farm.tiles[cell[1]][cell[0]] = { kind: P.KIND_WEED };
        }
      }
    }
  };
  Env.prototype.score = function (p) {
    var farm = this.farms[p], shedVal = 0;
    for (var c in farm.shed) if (this.mech.crops[c]) shedVal += farm.shed[c] * this.mech.crops[c].sell_price;
    return Math.round((farm.money + shedVal) * 100) / 100;
  };

  // ---- FarmBrain (mirrors real/brain.py) --------------------------------- //
  function FarmBrain(opts) {
    opts = opts || {};
    this.crops = opts.crops || ["WHEAT"];
    this.seedRestockThreshold = opts.seedRestockThreshold || 4;
    this.seedRestockQty = opts.seedRestockQty || 4;
  }
  FarmBrain.prototype.decide = function (obs) {
    var farm = obs.farms[obs.player], priv = obs["private"];
    var fx = farm.farmer[0], fy = farm.farmer[1], day = obs.day;
    var market = this._planMarket(farm, priv);
    var plan = this._planFarmer(farm, priv, day, fx, fy);
    var target = plan[0], cmd = plan[1];
    if (target === null) return { farmer: [P.PASS], hands: [], market: market };
    if (fx === target[0] && fy === target[1]) return { farmer: cmd, hands: [], market: market };
    return { farmer: [stepToward(fx, fy, target[0], target[1])], hands: [], market: market };
  };
  FarmBrain.prototype._planMarket = function (farm, priv) {
    var ops = [], seeds = priv.seeds, shed = priv.shed;
    for (var i = 0; i < this.crops.length; i++) {
      var crop = this.crops[i];
      if ((seeds[crop] || 0) < this.seedRestockThreshold) ops.push([P.BUY_SEED, crop, this.seedRestockQty]);
    }
    for (var c in shed) { var qty = Math.floor(shed[c]); if (qty > 0) ops.push([P.SELL, c, qty]); }
    return ops;
  };
  FarmBrain.prototype._planFarmer = function (farm, priv, day, fx, fy) {
    var tiles = farm.tiles, seeds = priv.seeds, size = tiles.length;
    var harvest = [], water = [], weed = [], plant = [];
    for (var y = 0; y < size; y++) for (var x = 0; x < size; x++) {
      var tile = tiles[y][x];
      if (tile === null) plant.push([x, y]);
      else if (tile && typeof tile === "object") {
        if (tile.kind === P.KIND_PLANT) {
          if (day - tile.planted_day >= 2) harvest.push([x, y]);
          else if (!tile.watered_today) water.push([x, y]);
        } else if (tile.kind === P.KIND_WEED) weed.push([x, y]);
      }
    }
    var haveSeed = this.crops.some(function (cr) { return (seeds[cr] || 0) > 0; });
    if (harvest.length) return [nearest(fx, fy, harvest), [P.HARVEST]];
    if (water.length) return [nearest(fx, fy, water), [P.WATER]];
    if (weed.length) return [nearest(fx, fy, weed), [P.DIG]];
    if (plant.length && haveSeed) {
      var crop = null;
      for (var k = 0; k < this.crops.length; k++) if ((seeds[this.crops[k]] || 0) > 0) { crop = this.crops[k]; break; }
      return [nearest(fx, fy, plant), [P.PLANT, crop]];
    }
    return [null, [P.PASS]];
  };
  function nearest(fx, fy, cells) {
    var best = cells[0], bestD = Infinity;
    for (var i = 0; i < cells.length; i++) {
      var d = Math.abs(cells[i][0] - fx) + Math.abs(cells[i][1] - fy);
      if (d < bestD) { bestD = d; best = cells[i]; }
    }
    return best;
  }
  function passAction() { return { farmer: [P.PASS], hands: [], market: [] }; }
  function describe(action) {
    var parts = [(action.farmer || [P.PASS]).join(" ")];
    (action.market || []).forEach(function (op) { parts.push(op.join(" ")); });
    return parts.join(" | ");
  }

  var API = { MT: MT, Env: Env, FarmBrain: FarmBrain, P: P, passAction: passAction, describe: describe, MECH: MECH, setDifficulty: setDifficulty };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.Kaggriculture = API;
})(typeof window !== "undefined" ? window : this);
