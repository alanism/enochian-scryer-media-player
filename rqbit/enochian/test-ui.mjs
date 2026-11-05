import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import ts from "typescript";
const source = readFileSync(new URL("../crates/librqbit/webui/src/helper/torrentPresentation.ts", import.meta.url), "utf8");
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext } }).outputText;
const { torrentProgress, torrentStatus, pieceCount } = await import("data:text/javascript," + encodeURIComponent(compiled));

test("a download error does not become 100 percent", () => {
  const stats = { state: "error", error: "Disk unavailable", total_bytes: 1000, progress_bytes: 250, finished: false };
  assert.equal(torrentProgress(stats), 25);
  assert.equal(torrentStatus(stats), "Error");
});
test("metadata checking and invalid counters do not imply completion", () => {
  assert.equal(torrentProgress({ total_bytes: 0, finished: false }), 0);
  assert.equal(torrentProgress({ total_bytes: 10, progress_bytes: NaN }), 0);
  assert.equal(torrentProgress({ total_bytes: 10, progress_bytes: 99 }), 100);
  assert.equal(torrentStatus({ state: "initializing" }), "Checking files");
});
test("a completed paused torrent reports its complete piece inventory", () => {
  const stats = { state: "paused", finished: true };
  assert.equal(torrentStatus(stats), "Complete · paused");
  assert.equal(pieceCount(stats, 26), "26/26");
  assert.equal(pieceCount({ finished: false, live: null }, 26), "—/26");
});
