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
test("selected-file completion cannot fabricate the full piece inventory", () => {
  const stats = { state: "paused", finished: true };
  assert.equal(torrentStatus(stats), "Complete · paused");
  assert.equal(pieceCount(null, 26), "—/26");
  assert.equal(pieceCount(new Uint8Array([0xff, 0x80]), 10), "9/10");
  assert.equal(pieceCount(new Uint8Array([0xff, 0xff]), 10), "10/10");
  assert.equal(pieceCount(new Uint8Array([0xff]), 10), "—/10");
});

const intervalSource = readFileSync(new URL("../crates/librqbit/webui/src/helper/customSetInterval.ts", import.meta.url), "utf8");
const intervalCompiled = ts.transpileModule(intervalSource, { compilerOptions: { module: ts.ModuleKind.ESNext } }).outputText;
const { customSetInterval } = await import("data:text/javascript," + encodeURIComponent(intervalCompiled));
test("closing a view during its in-flight request stops future polling", async () => {
  let release;
  let started;
  const request = new Promise(resolve => { release = resolve; });
  const firstCall = new Promise(resolve => { started = resolve; });
  let calls = 0;
  const stop = customSetInterval(async () => {
    calls++;
    started();
    await request;
    return 1;
  }, 0);
  await firstCall;
  stop();
  release();
  await new Promise(resolve => setTimeout(resolve, 30));
  stop();
  assert.equal(calls, 1);
});

const bytesSource = readFileSync(new URL("../crates/librqbit/webui/src/helper/formatBytes.ts", import.meta.url), "utf8");
const bytesCompiled = ts.transpileModule(bytesSource, { compilerOptions: { module: ts.ModuleKind.ESNext } }).outputText;
const { formatBytes } = await import("data:text/javascript," + encodeURIComponent(bytesCompiled));
test("binary sizes use binary unit labels and invalid values stay unknown", () => {
  assert.equal(formatBytes(1024), "1 KiB");
  assert.equal(formatBytes(1048576), "1 MiB");
  assert.equal(formatBytes(0), "0 Bytes");
  assert.equal(formatBytes(NaN), "—");
  assert.equal(formatBytes(-1), "—");
});
