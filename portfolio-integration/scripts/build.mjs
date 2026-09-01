import { cp, mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { customizeResearchCard, writePapersPage } from "./papers.mjs";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const dist = join(root, "dist");
const client = join(dist, "client");
const interfacePublic = join(root, "frontend", "interface", "public");
const macosPublic = join(root, "frontend", "macos", "public");
const macosIndex = join(root, "frontend", "macos", "index.html");
const worker = join(root, "backend", "worker", "index.js");

await rm(dist, { recursive: true, force: true });
await mkdir(client, { recursive: true });

for (const entry of await readdir(interfacePublic, { withFileTypes: true })) {
  await cp(join(interfacePublic, entry.name), join(client, entry.name), {
    recursive: entry.isDirectory(),
  });
}

const landingIntro =
  "I'm Harsh Chaudhary, leading AI Engineering and AI exploration at UPES, engineering, and AI at scale. Outside work, I build for team efficiency.";
const aboutLeadOriginal =
  "I explore how to shape AI-era workflows with craft and taste, building the next generation of digital products.";
const aboutLeadUpdated =
  "I explore how to shape AI-era workflows with craft and taste, building the next generation of software developers.";
const aboutCareerClient =
  'children:(0,s.jsxs)("span",{children:["I’m building ",(0,s.jsx)("span",{style:{color:"#fff"},children:"Models"}),", and previously worked in ",(0,s.jsx)("span",{style:{color:"#0033a0"},children:"IBM"}),", ",(0,s.jsx)("span",{style:{color:"#ff7a00"},children:"Capital Boon"}),", ",(0,s.jsx)("span",{style:{color:"#fff"},children:"Indian EXPO"})," and 100offer."]})';
const aboutCareerHtml =
  '<span>I’m building <span style="color:#fff">Models</span>, and previously worked in <span style="color:#0033a0">IBM</span>, <span style="color:#ff7a00">Capital Boon</span>, <span style="color:#fff">Indian EXPO</span> and 100offer.</span>';

const customizeLandingPage = async (directory) => {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) {
      await customizeLandingPage(path);
      continue;
    }

    if (!entry.name.endsWith(".html") && !entry.name.endsWith(".js")) continue;

    const original = await readFile(path, "utf8");
    let customized = original
      .replaceAll("curiosity.wen@gmail.com", "harshch310702@gmail.com")
      .replaceAll("https://twitter.com/wenhaoqi", "https://www.instagram.com/chaudhary_harsh_2002/?hl=en")
      .replaceAll("Twitter/X", "Insta")
      .replaceAll("https://www.figma.com/@wenhaoqi", "https://www.linkedin.com/in/harsh-chaudhary-78ba9a312/")
      .replaceAll("Figma", "LinkedIn")
      .replaceAll("https://github.com/wenhaoqiasd", "https://github.com/code-with-Harshchaudhary")
      .replaceAll("Reunimos™", "Mac OS")
      .replaceAll("/work/reunimos01.png", "/work/macos01.png")
      .replaceAll("/work/reunimos02.png", "/work/macos02.png")
      .replaceAll('href="/reunimos"', 'href="/macos"')
      .replaceAll('href:"/reunimos"', 'href:"/macos"')
      .replaceAll("2024-2026", "2026")
      .replaceAll("/work/inspire_mono_01.png", "/work/sentinel-rag-card-v2.png")
      .replaceAll("/work/inspire_mono_02.png", "/work/sentinel-rag-card-hover.png")
      .replaceAll("/work/wasm01.png", "/work/sentinel-ops-card-v2.png")
      .replaceAll("/work/wasm02.png", "/work/sentinel-ops-card-hover.png")
      .replaceAll("DarkSide", "Capital Boon")
      .replaceAll("/work/ds01.png", "/work/capitalboon01.png")
      .replaceAll("/work/ds02.png", "/work/capitalboon02.png")
      .replaceAll(
        "https://www.figma.com/community/plugin/986289377230504703/darkside",
        "https://www.capitalboon.in/about-us",
      )
      .replace('text:"Design &",startDelayMs:300,letterDelayMs:10', 'text:"Engineering &",startDelayMs:300,letterDelayMs:10')
      .replace('text:"Engineering",startDelayMs:300,letterDelayMs:10', 'text:"Design",startDelayMs:300,letterDelayMs:10')
      .replace('text:"to digital work",startDelayMs:700', 'text:"to Software World",startDelayMs:700')
      .replace(
        /let n=\(0,cQ\.usePasscodeAllowed\)\(cq\),i=\(0,u\.useMemo\)\(\(\)=>\["I'm Harsh Chaudhary, leading Design Engineering and AI exploration at ",\{length:c1,scramble:n\?c0:\(0,cZ\.passcodeLockedPlaceholderText\)\(\),className:n\?void 0:cZ\.PASSCODE_LOCKED_SCRAMBLE_CLASS,settled:\(0,s\.jsx\)\(c2,\{\}\)\},", engineering, and AI at scale\. Outside work, I build design tools for team efficiency\."\],\[n\]\)/,
        `i=(0,u.useMemo)(()=>[${JSON.stringify(landingIntro)}],[])`,
      )
      .replace("<span>Design &amp;</span></span><br/><span style=\"opacity:0\"><span>Engineering</span>", "<span>Engineering &amp;</span></span><br/><span style=\"opacity:0\"><span>Design</span>")
      .replace("<span>to digital work</span>", "<span>to Software World</span>")
      .replace(aboutLeadOriginal, aboutLeadUpdated)
      .replace(
        /children:\(0,s\.jsxs\)\("span",\{children:\["I’m building"," ",[\s\S]*?", and 100offer\."\]\}\)/,
        aboutCareerClient,
      )
      .replace(
        /<span>I’m building<!-- -->[\s\S]*?, and 100offer\.<\/span>/,
        aboutCareerHtml,
      )
      .replace(
        /(<span class="col-span-12 lg:col-span-6 xl:col-span-4 lg:col-start-7 xl:col-start-9 mt-auto lg:mt-0 p-2" style="opacity:0">)[\s\S]*?(<\/span><\/div><div class="flex flex-col self-end)/,
        `$1<span>${landingIntro}</span>$2`,
      );

    customized = customizeResearchCard(customized, entry.name);
    if (customized !== original) await writeFile(path, customized);
  }
};

await customizeLandingPage(client);
await writePapersPage({ root, client });

await cp(macosPublic, join(client, "macos"), { recursive: true });
await cp(macosIndex, join(client, "macos", "index.html"));

await mkdir(join(dist, "server"), { recursive: true });
await cp(worker, join(dist, "server", "index.js"));
await mkdir(join(dist, ".openai"), { recursive: true });
await cp(join(root, ".openai", "hosting.json"), join(dist, ".openai", "hosting.json"));
