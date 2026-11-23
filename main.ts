// Monday 23 November 2026 — one front page, 44 stories.
// Node 22, standard library only. draw.py paints entry.png in this
// repository; this program drops that exact file into <output>/entry.png
// so the gate and the judge both see the same bytes. The gate wants a
// single whole PNG or JPEG, at most 1 MiB and at most 1024 by 1024 pixels.
//
// Run outside the grader, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const dest = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

// In the grader /output is a mount point: create it when it is missing,
// never remove it and never empty it wholesale.
mkdirSync(dest, { recursive: true });
const src = join(root, "entry.png");
const written = join(dest, "entry.png");
copyFileSync(src, written);

console.log(`wrote ${written} (${statSync(written).size} bytes)`);
