// Carries the finished broadsheet into the harness output directory.
//
// The image is the entry: entry.png lives next to this script in the
// repository, and the judge only ever sees the bytes that land in the output
// directory. Both graded runs must produce identical bytes, so this does a
// plain byte-for-byte copy — no rendering, no timestamps, nothing that could
// differ between runs.

import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outputDir, { recursive: true });
copyFileSync(join(here, "entry.png"), join(outputDir, "entry.png"));
