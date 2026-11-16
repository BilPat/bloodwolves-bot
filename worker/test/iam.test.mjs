import { test } from "node:test"; import assert from "node:assert/strict";
import { resolveChar } from "../src/index.js";
// /iam (16 Nov): tracked names link at once; anything else is looked up on Blizzard (here a fake lookup).
const st = { characters: { "us:steel-appeal": { class: "Warrior" }, "us:whizz-aard": { class: "Mage" } } };
const blizz = (found) => async (_env, raw) => (found[raw.toLowerCase()] || null);
const env = { BLIZZARD_REGION: "us" };
test("exact tracked name links without a Blizzard call", async () => {
  let called = false;
  const r = await resolveChar(env, st, "Steel Appeal", async () => { called = true; return null; });
  assert.deepEqual(r, { key: "us:steel-appeal", name: "Steel Appeal", cls: "Warrior", isNew: false });
  assert.equal(called, false);
});
test("an untracked name found on Blizzard is new", async () => {
  const r = await resolveChar(env, st, "Lumi Brightforge", blizz({ "lumi brightforge": { key: "us:lumi-brightforge", name: "Lumi Brightforge", cls: "Priest", level: 22 } }));
  assert.equal(r.isNew, true); assert.equal(r.key, "us:lumi-brightforge"); assert.equal(r.cls, "Priest");
});
test("a first name that is also the start of a tracked name: Blizzard is asked before the partial match", async () => {
  const r = await resolveChar(env, st, "Whizz", blizz({ whizz: { key: "us:whizz", name: "Whizz", cls: "Rogue" } }));
  assert.equal(r.key, "us:whizz"); assert.equal(r.isNew, true);
});
test("a partial tracked name still links when Blizzard has no such character", async () => {
  const r = await resolveChar(env, st, "whi", blizz({}));
  assert.equal(r.key, "us:whizz-aard"); assert.equal(r.isNew, false);
});
test("unknown everywhere: a miss with the cleaned name", async () => {
  const r = await resolveChar(env, st, "  nobody   here ", blizz({}));
  assert.deepEqual(r, { miss: "Nobody Here" });
  assert.equal(await resolveChar(env, st, "   ", blizz({})), null);
});
