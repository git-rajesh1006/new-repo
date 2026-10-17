// Usage:  node render.mjs still <seconds> out.png   |   node render.mjs stills "t1,t2,..." outDir   |   node render.mjs video out.mp4
import path from "node:path";
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";

const CHROME = process.env.CHROME_PATH || "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell";
const [mode, a, b] = process.argv.slice(2);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const opts = { serveUrl, browserExecutable: CHROME, chromiumOptions: { gl: "angle", disableWebSecurity: false }, logLevel: "warn" };
const composition = await selectComposition({ ...opts, id: "Day6" });
if (mode === "stills") {
  for (const sec of a.split(",")) await renderStill({ ...opts, composition, frame: Math.round(Number(sec) * composition.fps), output: path.resolve(b, `f_${sec}.png`) });
} else if (mode === "still") {
  await renderStill({ ...opts, composition, frame: Math.round(Number(a) * composition.fps), output: path.resolve(b) });
} else {
  await renderMedia({ ...opts, composition, codec: "h264", audioCodec: "aac", outputLocation: path.resolve(a), crf: 20, concurrency: 4,
    onProgress: ({ progress }) => process.stdout.write(`\r${(progress * 100).toFixed(0)}%`) });
}
console.log("\ndone");
