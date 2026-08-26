#!/usr/bin/env node
"use strict";

/**
 * Strict PR review poster.
 *
 * Like post_review.js but FAILS with actionable errors when comments
 * can't be placed on valid diff lines (>5 lines away).
 * The calling agent sees the errors, fixes line numbers, and retries.
 */

const fs = require("fs");
const os = require("os");
const path = require("path");
const crypto = require("crypto");
const { execFileSync } = require("child_process");

const HUNK_HEADER_RE = /^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@/;
const MAX_LINE_DISTANCE = 5;
const MAX_RETRIES = 5;
const INITIAL_BACKOFF_MS = 1000;

const REDACT_PATTERNS = [
  /Bearer\s+\S+/gi,
  /token\s+\S+/gi,
  /ghp_[A-Za-z0-9_]+/g,
  /gho_[A-Za-z0-9_]+/g,
  /ghs_[A-Za-z0-9_]+/g,
  /ghr_[A-Za-z0-9_]+/g,
  /ghu_[A-Za-z0-9_]+/g,
  /github_pat_[A-Za-z0-9_]+/g,
  /Authorization:[^\n]*/gi,
];

function redact(text) {
  return REDACT_PATTERNS.reduce((s, re) => s.replace(re, "[REDACTED]"), text);
}

function log(msg) {
  console.log(redact(String(msg)));
}

function logError(msg) {
  process.stderr.write(redact(String(msg)) + "\n");
}

// ── Diff parsing ──

function stripDiffPath(p) {
  if (p === "/dev/null" || p === "") return p;
  if (p.startsWith("a/") || p.startsWith("b/")) return p.slice(2);
  return p;
}

function parseUnifiedDiff(diffText) {
  const files = [];
  let currentOldPath = "";
  let currentNewPath = "";
  let currentFileKey = "";
  let currentHunks = [];

  function flush() {
    if (!currentFileKey) return;
    const oldPath = currentOldPath;
    const newPath = currentNewPath;
    let status = "modified";
    if (oldPath === "/dev/null" && newPath !== "/dev/null") status = "added";
    else if (oldPath !== "/dev/null" && newPath === "/dev/null") status = "deleted";
    else if (oldPath !== newPath) status = "renamed";
    files.push({ path: currentFileKey, status, hunks: currentHunks });
    currentOldPath = "";
    currentNewPath = "";
    currentFileKey = "";
    currentHunks = [];
  }

  for (const rawLine of diffText.split("\n")) {
    const line = rawLine.replace(/\r$/, "");
    if (line.startsWith("diff --git ")) {
      flush();
      const gitDiffMatch = line.match(/^diff --git (a\/.+) (b\/.+)$/);
      if (gitDiffMatch) {
        currentOldPath = stripDiffPath(gitDiffMatch[1]);
        currentNewPath = stripDiffPath(gitDiffMatch[2]);
        currentFileKey = currentNewPath;
      } else {
        currentOldPath = "";
        currentNewPath = "";
        currentFileKey = "";
      }
      currentHunks = [];
      continue;
    }
    if (line.startsWith("--- ")) {
      currentOldPath = stripDiffPath(line.slice(4).trim());
      continue;
    }
    if (line.startsWith("+++ ")) {
      currentNewPath = stripDiffPath(line.slice(4).trim());
      currentFileKey = currentNewPath !== "/dev/null" ? currentNewPath : currentOldPath;
      continue;
    }
    const match = line.match(HUNK_HEADER_RE);
    if (match) {
      currentHunks.push({
        old_start: parseInt(match[1], 10),
        old_count: parseInt(match[2] ?? "1", 10),
        new_start: parseInt(match[3], 10),
        new_count: parseInt(match[4] ?? "1", 10),
      });
    }
  }
  flush();
  return files;
}

function isLineInHunk(hunk, line, side) {
  if (side === "LEFT") {
    return line >= hunk.old_start && line < hunk.old_start + hunk.old_count;
  }
  return line >= hunk.new_start && line < hunk.new_start + hunk.new_count;
}

function findNearestValidLine(hunks, line, side) {
  let bestLine = null;
  let bestDist = Infinity;
  for (const hunk of hunks) {
    const count = side === "LEFT" ? hunk.old_count : hunk.new_count;
    const hunkStart = side === "LEFT" ? hunk.old_start : hunk.new_start;
    if (count === 0) continue;
    const hunkEnd = hunkStart + count - 1;
    if (isLineInHunk(hunk, line, side)) {
      return { line, distance: 0 };
    }
    if (line < hunkStart) {
      const dist = hunkStart - line;
      if (dist < bestDist) { bestDist = dist; bestLine = hunkStart; }
    } else if (line > hunkEnd) {
      const dist = line - hunkEnd;
      if (dist < bestDist) { bestDist = dist; bestLine = hunkEnd; }
    }
  }
  if (bestLine !== null) return { line: bestLine, distance: bestDist };
  return null;
}

// ── Comment validation (strict) ──

function validateComments(payload, hunkMap) {
  const fileMap = new Map();
  for (const f of hunkMap) fileMap.set(f.path, f);

  const validComments = [];
  const errors = [];
  let adjustedCount = 0;

  for (const comment of payload.comments || []) {
    const fileEntry = fileMap.get(comment.path);
    const side = comment.side || "RIGHT";
    const normalizedComment = { ...comment, side };

    if (!fileEntry || fileEntry.hunks.length === 0) {
      // File not in diff at all
      const hunkRanges = fileEntry
        ? fileEntry.hunks.map(h => `${h.new_start}-${h.new_start + h.new_count - 1}`).join(", ")
        : "none";
      errors.push({
        path: comment.path,
        line: comment.line,
        reason: `File "${comment.path}" has no diff hunks. The file may not be changed in this PR.`,
        validRanges: hunkRanges,
      });
      continue;
    }

    const nearest = findNearestValidLine(fileEntry.hunks, normalizedComment.line, side);

    if (!nearest) {
      const hunkRanges = fileEntry.hunks
        .map(h => `${h.new_start}-${h.new_start + h.new_count - 1}`)
        .join(", ");
      errors.push({
        path: comment.path,
        line: comment.line,
        reason: `Line ${comment.line} has no nearby diff hunk.`,
        validRanges: hunkRanges,
      });
      continue;
    }

    if (nearest.distance === 0) {
      validComments.push(normalizedComment);
    } else if (nearest.distance <= MAX_LINE_DISTANCE) {
      adjustedCount++;
      validComments.push({
        ...normalizedComment,
        line: nearest.line,
        body: `> _Original location: line ${normalizedComment.line} (adjusted to nearest diff line)_\n\n${normalizedComment.body}`,
      });
    } else {
      // Too far — report error with actionable info
      const hunkRanges = fileEntry.hunks
        .map(h => `${h.new_start}-${h.new_start + h.new_count - 1}`)
        .join(", ");
      errors.push({
        path: comment.path,
        line: comment.line,
        nearestValidLine: nearest.line,
        distance: nearest.distance,
        reason: `Line ${comment.line} is ${nearest.distance} lines away from nearest diff hunk (max allowed: ${MAX_LINE_DISTANCE}). Nearest valid line: ${nearest.line}.`,
        validRanges: hunkRanges,
      });
    }
  }

  return { validComments, errors, adjustedCount };
}

// ── GitHub API ──

function ghApi(endpoint, method, inputFile) {
  return execFileSync("gh", ["api", endpoint, "--method", method, "--input", inputFile], {
    encoding: "utf-8",
    stdio: ["pipe", "pipe", "pipe"],
    timeout: 60000,
  });
}

function parseApiError(err) {
  let jsonBody = null;
  if (err.stdout) {
    try { jsonBody = JSON.parse(err.stdout); } catch (_) {}
  }
  let httpStatus = null;
  let apiResponseMessage = null;
  if (jsonBody && jsonBody.status != null) {
    const parsed = parseInt(jsonBody.status, 10);
    if (!isNaN(parsed)) httpStatus = parsed;
    const msgParts = [];
    if (jsonBody.message) msgParts.push(jsonBody.message);
    const errors = Array.isArray(jsonBody.errors) ? jsonBody.errors : [];
    for (const e of errors) {
      const text = typeof e === "string" ? e : (e && e.message ? e.message : "");
      if (text) msgParts.push(text);
    }
    if (msgParts.length > 0) apiResponseMessage = msgParts.join(": ");
  }
  if (httpStatus === null) {
    for (const text of [err.stderr, err.message]) {
      if (!text) continue;
      const match = text.match(/HTTP (\d{3})/i);
      if (match) { httpStatus = parseInt(match[1], 10); break; }
    }
  }
  if (!apiResponseMessage) {
    const parts = [];
    if (err.message) parts.push(`message: ${err.message}`);
    if (err.stdout) parts.push(`stdout: ${err.stdout}`);
    if (err.stderr) parts.push(`stderr: ${err.stderr}`);
    apiResponseMessage = parts.join("\n\n") || "unknown error";
  }
  return { httpStatus, apiResponseMessage, jsonBody };
}

function isRecoverableError(err) {
  const { httpStatus, apiResponseMessage } = parseApiError(err);
  if (httpStatus !== null && (httpStatus >= 500 || httpStatus === 429)) return true;
  const msg = (apiResponseMessage || "").toLowerCase();
  return msg.includes("econnreset") || msg.includes("etimedout") || msg.includes("econnrefused")
    || msg.includes("socket hang up") || msg.includes("network error");
}

function logApiError(err, context) {
  logError(JSON.stringify({
    context,
    message: err.message ?? undefined,
    stdout: err.stdout ?? undefined,
    stderr: err.stderr ?? undefined,
    status: err.status ?? undefined,
  }));
}

function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function postWithRetry(endpoint, payloadFile) {
  let lastErr;
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      return ghApi(endpoint, "POST", payloadFile);
    } catch (err) {
      lastErr = err;
      logApiError(err, `POST ${endpoint} attempt ${attempt + 1}/${MAX_RETRIES}`);
      if (!isRecoverableError(err)) throw err;
      if (attempt < MAX_RETRIES - 1) {
        const backoff = INITIAL_BACKOFF_MS * Math.pow(2, attempt);
        log(`  Retrying in ${backoff}ms...`);
        sleep(backoff);
      }
    }
  }
  throw lastErr || new Error("Max retries exceeded");
}

function submitPendingReview(endpoint, response) {
  let parsed;
  try { parsed = JSON.parse(response); } catch (_) { return response; }
  if (parsed.state !== "PENDING" || !parsed.id) return response;

  const submitEndpoint = `${endpoint}/${parsed.id}/events`;
  const tmpFile = path.join(os.tmpdir(), `review_submit_${crypto.randomBytes(6).toString("hex")}.json`);
  try {
    fs.writeFileSync(tmpFile, JSON.stringify({ event: "COMMENT" }));
    return postWithRetry(submitEndpoint, tmpFile);
  } catch (e) {
    logApiError(e, "submit PENDING review");
    logError("Error: failed to submit PENDING review — review may not be visible");
    throw e;
  } finally {
    try { fs.unlinkSync(tmpFile); } catch (_) {}
  }
}

// ── Main ──

function parseArgs(args) {
  if (args.length < 4 || args.includes("--help") || args.includes("-h")) {
    logError(
      "Usage: node post_review_strict.js <OWNER/REPO> <PR_NUMBER> <diff-file> <payload-file>\n\n" +
      "Validates comment line numbers against the diff. If any comment is >5 lines\n" +
      "from a diff hunk, exits with error and prints actionable fix instructions.\n" +
      "On success, posts the review."
    );
    process.exit(args.includes("--help") || args.includes("-h") ? 0 : 1);
  }

  const ownerRepo = args[0];
  const prNumber = args[1];
  if (!/^[\w.-]+\/[\w.-]+$/.test(ownerRepo)) {
    logError(`Error: invalid OWNER/REPO format: ${ownerRepo}`);
    process.exit(1);
  }
  if (!/^\d+$/.test(prNumber)) {
    logError(`Error: PR_NUMBER must be a positive integer: ${prNumber}`);
    process.exit(1);
  }

  const diffFilePath = path.resolve(args[2]);
  const payloadFilePath = path.resolve(args[3]);
  if (!fs.existsSync(diffFilePath)) {
    logError(`Error: diff file not found: ${diffFilePath}`);
    process.exit(1);
  }
  if (!fs.existsSync(payloadFilePath)) {
    logError(`Error: payload file not found: ${payloadFilePath}`);
    process.exit(1);
  }

  return { ownerRepo, prNumber, diffFilePath, payloadFilePath };
}

function main() {
  const { ownerRepo, prNumber, diffFilePath, payloadFilePath } = parseArgs(process.argv.slice(2));

  let payload;
  try {
    payload = JSON.parse(fs.readFileSync(payloadFilePath, "utf-8"));
  } catch (e) {
    logError(`Error reading/parsing payload file: ${e.message}`);
    process.exit(1);
  }
  let diffText;
  try {
    diffText = fs.readFileSync(diffFilePath, "utf-8");
  } catch (e) {
    logError(`Error reading diff file: ${e.message}`);
    process.exit(1);
  }
  const hunkMap = parseUnifiedDiff(diffText);

  // ── Validate ──
  const { validComments, errors, adjustedCount } = validateComments(payload, hunkMap);

  if (errors.length > 0) {
    logError(`\nERROR: ${errors.length} comment(s) have invalid line numbers.\n`);
    logError("Fix these comments in the payload and re-run:\n");
    for (const e of errors) {
      logError(`  ${e.path}:${e.line} — ${e.reason}`);
      logError(`    Valid diff ranges for this file: [${e.validRanges}]`);
      logError("");
    }
    process.exit(1);
  }

  if (adjustedCount > 0) {
    log(`${adjustedCount} comment(s) adjusted to nearest diff line (within ${MAX_LINE_DISTANCE} lines)`);
  }

  // ── Post ──
  const adjustedPayload = { ...payload, comments: validComments };
  fs.writeFileSync(payloadFilePath, JSON.stringify(adjustedPayload, null, 2));

  const endpoint = `repos/${ownerRepo}/pulls/${prNumber}/reviews`;
  log(`Posting review with ${validComments.length} inline comment(s)...`);

  try {
    const response = postWithRetry(endpoint, payloadFilePath);
    const finalResponse = submitPendingReview(endpoint, response);
    log(finalResponse);
    log("Review posted successfully.");

  } catch (e) {
    logError(JSON.stringify({ error: e.message, details: String(e.details || e.message) }));
    logError("Review posting failed.");
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}
