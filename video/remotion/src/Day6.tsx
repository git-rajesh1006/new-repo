import React from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame } from "remotion";
import { getLength, getPointAtLength, evolvePath } from "@remotion/paths";
import { C, FPS, H, MONO, PH, SANS, T, W, DURATION_SEC, bounce, captionChunks, clamp01, easeOut, lerp, pop } from "./lib";
import { Background, Confetti, Header, Pill, Scene, Txt } from "./primitives";
import { BugIcon, BulbIcon, CodeIcon, GearIcon, PlanIcon, RocketIcon, UsersIcon } from "./icons";

const useT = () => { const frame = useCurrentFrame(); return { frame, t: frame / FPS }; };

// ---------------------------------------------------------------- 1. hook
const SceneHook: React.FC = () => {
  const { frame, t } = useT();
  const cFast = T(0, "fast"), cCoding = T(1, "coding"), cOnly = T(1, "okkate"), cNot = T(1, "saripodu");
  const sw = pop(t, T(0, "software"), 0.5);
  const fast = bounce(frame, cFast, 9, 150);
  const shake = t > cNot ? Math.sin(t * 70) * 10 * Math.exp(-(t - cNot) * 6) : 0;
  return (
    <>
      <Txt y={430} size={140} scale={bounce(frame, 0.1)} rotate={Math.sin(t * 8) * 4}>🔥</Txt>
      <Txt y={620} size={110} opacity={sw} tx={(1 - sw) * -320}>SOFTWARE</Txt>
      {t > cFast && [0, 1, 2, 3, 4].map((i) => {
        const p = ((t - cFast) * 2.2 + i * 0.2) % 1;
        return <div key={i} style={{ position: "absolute", left: 80 + p * 300 - 200, top: 770 + i * 24, width: 220 * (1 - p), height: 5, borderRadius: 3, background: C.green, opacity: (1 - p) * 0.8 }} />;
      })}
      <Txt y={800} size={190} color={C.green} scale={fast} glow={C.green} opacity={clamp01(fast)}>FAST</Txt>
      <Txt y={965} size={54} color={C.text2} weight={700} opacity={pop(t, T(0, "develop"))}>develop cheyali ante…</Txt>
      <Txt y={1220} size={160} scale={bounce(frame, cCoding, 8, 170)} opacity={(clamp01(bounce(frame, cCoding)) * (t > cNot ? 0.4 : 1))} tx={shake} glow={t > cNot ? undefined : C.white}>CODING</Txt>
      <Txt y={1370} size={70} color={C.text2} opacity={pop(t, cOnly)} ty={(1 - pop(t, cOnly)) * 30}>okkate…</Txt>
      <Txt y={1480} size={86} color={C.red} scale={bounce(frame, cNot, 8, 180)} opacity={clamp01(pop(t, cNot, 0.2))} tx={shake} glow={C.red}>✕ NOT ENOUGH</Txt>
    </>
  );
};

// ---------------------------------------------------------------- 2. idea -> users, SDLC reveal
const JOURNEY = "M270 640 Q540 330 810 640";
const JLEN = getLength(JOURNEY);
const SceneJourney: React.FC = () => {
  const { frame, t } = useT();
  const cIdea = T(2, "idea"), cUsers = T(2, "users"), cDag = T(2, "daggariki"), cProc = T(2, "process"), cSDLC = T(3, "SDLC");
  const out = 1 - pop(t, cSDLC - 0.35, 0.3);
  const drawP = clamp01((t - cDag) / 1.0);
  const e = evolvePath(drawP, JOURNEY);
  const dotP = clamp01((t - T(2, "reach")) / 1.4);
  const dot = getPointAtLength(JOURNEY, JLEN * dotP);
  const letters = ["S", "D", "L", "C"], words = ["Software", "Development", "Life", "Cycle"];
  const wcue = [T(4, "Software"), T(4, "Development"), T(4, "Life"), T(4, "Cycle")];
  const ring = clamp01((t - cSDLC) / 0.9);
  return (
    <>
      <div style={{ opacity: out }}>
        <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0 }}>
          <path d={JOURNEY} stroke={C.dim} strokeWidth={6} fill="none" strokeDasharray="4 16" strokeLinecap="round" />
          <path d={JOURNEY} stroke={C.green} strokeWidth={8} fill="none" strokeLinecap="round" {...e} style={{ filter: `drop-shadow(0 0 10px ${C.green})` }} />
          {dotP > 0 && dotP < 1 && <circle cx={dot.x} cy={dot.y} r={16} fill={C.white} style={{ filter: `drop-shadow(0 0 14px ${C.green})` }} />}
        </svg>
        <div style={{ position: "absolute", left: 270 - 75, top: 640 - 75 }}><BulbIcon t={t} cue={cIdea} /></div>
        <div style={{ position: "absolute", left: 810 - 75, top: 640 - 75 }}><UsersIcon t={t} cue={cUsers} /></div>
        <Txt x={270} y={770} size={40} color={C.white} opacity={pop(t, cIdea)}>IDEA</Txt>
        <Txt x={810} y={770} size={40} color={C.white} opacity={pop(t, cUsers)}>USERS</Txt>
        <div style={{ position: "absolute", left: 540 - 55, top: 455 - 55, opacity: pop(t, cProc), transform: `scale(${bounce(frame, cProc)})` }}><GearIcon t={t} size={110} /></div>
        <Txt y={900} size={70} color={C.green} opacity={pop(t, T(2, "proper"))} glow={C.green}>PROPER PROCESS</Txt>
      </div>
      {t > cSDLC - 0.1 && (
        <>
          <div style={{ position: "absolute", left: 540 - 700 * ring, top: 800 - 700 * ring, width: 1400 * ring, height: 1400 * ring, borderRadius: "50%", border: `6px solid ${C.green}`, opacity: (1 - ring) * 0.9 }} />
          <Txt y={520} size={72} color={C.green} opacity={pop(t, cSDLC)} scale={bounce(frame, cSDLC)}>WHAT IS SDLC?</Txt>
          {letters.map((l, i) => {
            const c = cSDLC + i * 0.12;
            const wp = pop(t, wcue[i]);
            const x = 195 + i * 230;
            return (
              <React.Fragment key={l}>
                <div style={{ position: "absolute", left: x - 100, top: 700, width: 200, height: 200, boxSizing: "border-box", borderRadius: 40, border: `5px solid ${C.green}`,
                  background: `rgba(0,255,160,${0.08 + 0.16 * wp})`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: SANS, fontWeight: 800, fontSize: 150,
                  color: C.green, transform: `scale(${bounce(frame, c, 9, 150)}) rotate(${(1 - clamp01(bounce(frame, c))) * -20}deg)`, boxShadow: `0 0 ${30 + 40 * wp}px ${C.green}66` }}>{l}</div>
                <Txt x={x} y={960} size={33} opacity={wp} ty={(1 - wp) * 20}><span style={{ color: C.green }}>{words[i][0]}</span>{words[i].slice(1)}</Txt>
              </React.Fragment>
            );
          })}
        </>
      )}
    </>
  );
};

// ---------------------------------------------------------------- 3. recap + question
const SceneRecap: React.FC = () => {
  const { frame, t } = useT();
  const cDay = T(5, "Day"), cAgile = T(5, "Agile"), cSDLC = T(6, "SDLC"), cWork = T(6, "work"), cGear = T(6, "avuthundo");
  const slide = pop(t, cSDLC - 0.6, 0.35);
  return (
    <>
      <div style={{ transform: `translateX(${-slide * 1300}px)` }}>
        <Txt y={640} size={170} opacity={pop(t, cDay)} scale={bounce(frame, cDay)}>DAY 5 <span style={{ color: C.green }}>✓</span></Txt>
        <Txt y={800} size={72} color={C.green} opacity={pop(t, cAgile)} ty={(1 - pop(t, cAgile)) * 30}>Agile + DevOps</Txt>
      </div>
      <Txt y={720} size={250} color={C.green} scale={bounce(frame, cSDLC, 9, 150)} opacity={clamp01(bounce(frame, cSDLC))} glow={C.green}>SDLC</Txt>
      <div style={{ position: "absolute", left: 540 - 80, top: 1000, opacity: pop(t, cGear), transform: `scale(${bounce(frame, cGear)})` }}><GearIcon t={t} size={160} speed={70} /></div>
      <Txt y={1240} size={62} opacity={pop(t, cWork)} ty={(1 - pop(t, cWork)) * 25}>ela work avuthundo?</Txt>
    </>
  );
};

// ---------------------------------------------------------------- 4. roadmap (the five SDLC phases)
const NODES = [{ x: 300, y: 500 }, { x: 780, y: 730 }, { x: 300, y: 960 }, { x: 780, y: 1190 }, { x: 300, y: 1420 }];
const seg = (a: { x: number; y: number }, b: { x: number; y: number }) => {
  const mx = (a.x + b.x) / 2;
  return `C ${mx} ${a.y} ${mx} ${b.y} ${b.x} ${b.y}`;
};
const SEGS = NODES.slice(0, -1).map((n, i) => `M ${n.x} ${n.y} ${seg(n, NODES[i + 1])}`);
const FULL = `M ${NODES[0].x} ${NODES[0].y} ` + NODES.slice(0, -1).map((n, i) => seg(n, NODES[i + 1])).join(" ");
const FULL_LEN = getLength(FULL);
const PHASES = [
  { name: "PLANNING", sub: "features decide" },
  { name: "DESIGN & DEV", sub: "design + code" },
  { name: "TESTING", sub: "bug check" },
  { name: "DEPLOYMENT", sub: "release → users" },
  { name: "MAINTENANCE", sub: "monitor • fix" },
];

const SceneRoadmap: React.FC = () => {
  const { frame, t } = useT();
  const cues = [T(8, "Planning"), T(11, "Design"), T(15, "Testing"), T(18, "Deployment"), T(20, "Maintenance")];
  const intro = T(7);                       // "SDLC lo first,"
  const sDLC = T(23, "SDLC"), cPlan = T(23, "plan"), cMaint = T(23, "maintain"), cComplete = T(24, "complete");
  const flash = (cue: number) => Math.max(0, 1 - Math.abs(t - cue - 0.15) / 0.45);
  const done = t >= cComplete;
  const dotStart = sDLC, dotP = Math.max(0, ((t - dotStart) / 2.6) % 1);
  const dot = getPointAtLength(FULL, FULL_LEN * dotP);
  const showDot = t >= dotStart && t < cComplete + 1.2;
  const iconOf = (i: number) => {
    const c = cues[i];
    if (i === 0) return <PlanIcon t={t} cue={c} size={100} />;
    if (i === 1) return <CodeIcon t={t} cue={c} size={100} />;
    if (i === 2) return <BugIcon t={t} cue={T(16, "bugs")} fixCue={T(16, "check")} size={100} />;
    if (i === 3) return <RocketIcon t={t} cue={T(19, "release")} size={100} />;
    return <GearIcon t={t} size={100} speed={60} />;
  };
  const chips = [["MONITOR", T(21, "monitor")], ["FIX", T(22, "fix")], ["IMPROVE", T(22, "improve")]] as const;
  return (
    <>
      <Txt y={270} size={120} color={C.green} glow={C.green} opacity={pop(t, intro)} scale={bounce(frame, intro)}>SDLC</Txt>
      <Txt y={375} size={34} color={done ? C.green : C.grey} weight={700} mono opacity={pop(t, intro + 0.2)}>
        {done ? "COMPLETE PROCESS ✓" : "5 PHASES"}
      </Txt>
      <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0 }}>
        {SEGS.map((d, i) => (
          <React.Fragment key={i}>
            <path d={d} stroke={C.dim} strokeWidth={6} fill="none" strokeDasharray="4 16" strokeLinecap="round" opacity={pop(t, intro + 0.3 + i * 0.1)} />
            <path d={d} stroke={C.green} strokeWidth={done ? 11 + 3 * Math.sin(t * 6) : 8} fill="none" strokeLinecap="round"
              {...evolvePath(clamp01((t - (cues[i] + 0.3)) / Math.max(0.6, cues[i + 1] - cues[i] - 0.5)), d)}
              style={{ filter: `drop-shadow(0 0 ${done ? 16 : 8}px ${C.green})` }} />
          </React.Fragment>
        ))}
        {showDot && <circle cx={dot.x} cy={dot.y} r={15} fill={C.white} style={{ filter: `drop-shadow(0 0 16px ${C.green})` }} />}
      </svg>
      {NODES.map((n, i) => {
        const appear = pop(t, intro + 0.1 * i, 0.4);
        const act = t >= cues[i];
        const spr = act ? bounce(frame, cues[i], 9, 170) : 0;
        const f = flash(i === 0 ? cPlan : i === 4 ? cMaint : -99);
        const sc = appear * (act ? 0.85 + 0.2 * spr : 0.82) * (1 + 0.12 * f);
        const ring = clamp01((t - cues[i]) / 0.9);
        return (
          <React.Fragment key={i}>
            {act && ring < 1 && <div style={{ position: "absolute", left: n.x - 72 - 90 * ring, top: n.y - 72 - 90 * ring, width: 144 + 180 * ring, height: 144 + 180 * ring, borderRadius: "50%", border: `5px solid ${C.green}`, opacity: 1 - ring }} />}
            <div style={{
              position: "absolute", left: n.x - 72, top: n.y - 72, width: 144, height: 144, boxSizing: "border-box", borderRadius: "50%",
              border: `6px solid ${act ? C.green : C.dim}`, background: act ? "rgba(0,255,160,.12)" : "#0e0e0e", transform: `scale(${sc})`,
              boxShadow: act ? `0 0 ${40 + 40 * f}px rgba(0,255,160,${0.45 + 0.4 * f})` : "none", display: "flex", alignItems: "center", justifyContent: "center", opacity: appear,
            }}>{act ? iconOf(i) : <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 60, color: C.dim }}>{i + 1}</div>}</div>
            <Txt x={n.x} y={n.y + 112} size={40} color={act ? C.white : C.grey} opacity={appear} scale={act ? 1 : 0.9}>{PHASES[i].name}</Txt>
            <Txt x={n.x} y={n.y + 152} size={28} color={act ? C.green : C.dim} weight={700} opacity={appear}>{PHASES[i].sub}</Txt>
          </React.Fragment>
        );
      })}
      {chips.map(([lab, cue], i) => (
        <Pill key={lab} x={680 + i * 135} y={1455} w={124} h={58} label={lab} size={22} radius={20}
          opacity={pop(t, cue, 0.3)} scale={bounce(frame, cue, 10, 170)} fill={clamp01(1 - (t - cue) / 0.8)} />
      ))}
    </>
  );
};

// ---------------------------------------------------------------- 5. Day 6 done
const SceneDay6: React.FC = () => {
  const { frame, t } = useT();
  const cDay = T(25, "Day"), c100 = T(25, "100"), cSix = T(25, "6!");
  const n = Math.round(6 * pop(t, cDay, 0.7));
  return (
    <>
      <Txt y={760} size={190} opacity={pop(t, T(25)) } scale={bounce(frame, T(25), 9)}>DAY 6 <span style={{ color: C.green }}>✓</span></Txt>
      <Txt y={960} size={48} color={C.green} opacity={pop(t, c100)}>100 DAYS OF DEVOPS</Txt>
      <div style={{ position: "absolute", left: 140, top: 1030, width: 800, height: 40, borderRadius: 20, background: C.dim, opacity: pop(t, c100) }}>
        <div style={{ width: 800 * 0.06 * pop(t, cDay, 1.0) + 30, height: 40, borderRadius: 20, background: C.green, boxShadow: `0 0 20px ${C.green}` }} />
      </div>
      <Txt y={1140} size={48} color={C.text2} mono opacity={pop(t, c100)}>{n} / 100</Txt>
      <Confetti t={t} cue={cSix} y={780} />
    </>
  );
};

// ---------------------------------------------------------------- 6. Day 7 teaser
const SceneDay7: React.FC = () => {
  const { frame, t } = useT();
  const cDay = T(26, "Day"), cS = T(26, "SDLC"), cD = T(26, "DevOps"), cConn = T(26, "connection");
  const link = pop(t, cConn - 0.3, 0.5);
  return (
    <>
      <Txt y={560} size={210} opacity={pop(t, cDay)} scale={bounce(frame, cDay, 9)}>DAY 7</Txt>
      <Pill x={270} y={980} w={400} h={170} label="SDLC" size={84} opacity={pop(t, cS)} scale={bounce(frame, cS, 10)} />
      <Pill x={810} y={980} w={400} h={170} label="DEVOPS" size={72} opacity={pop(t, cD)} scale={bounce(frame, cD, 10)} color={C.green} fill={0.0} />
      {link > 0 && (
        <>
          <div style={{ position: "absolute", left: 480, top: 976, width: 120 * link, height: 8, background: C.green, borderRadius: 4, boxShadow: `0 0 18px ${C.green}` }} />
          {[0, 1, 2].map((i) => <div key={i} style={{ position: "absolute", left: 480 + (((t * 1.6) + i / 3) % 1) * 120, top: 966, width: 16, height: 16, borderRadius: 8, background: C.white, opacity: link }} />)}
          <Txt y={1170} size={130} color={C.green} scale={link * (1 + 0.05 * Math.sin(t * 6))} glow={C.green}>?</Txt>
        </>
      )}
      <Txt y={1330} size={56} opacity={pop(t, cConn)}>connection enti?</Txt>
    </>
  );
};

// ---------------------------------------------------------------- 7. CTA
const SceneCTA: React.FC = () => {
  const { frame, t } = useT();
  const cJ = T(27, "journey"), cCont = T(27, "continue"), cF = T(27, "Follow");
  const f = bounce(frame, cF, 7, 160);
  return (
    <>
      <Txt y={640} size={92} color={C.green} glow={C.green} opacity={pop(t, T(27))} ty={(1 - pop(t, T(27))) * 40}>DEVOPS JOURNEY</Txt>
      <Txt y={790} size={66} opacity={pop(t, cCont)} tx={Math.sin(t * 5) * 8}>continues →</Txt>
      {t > cF - 0.05 && (
        <div style={{ position: "absolute", left: 540 - 330, top: 950, width: 660, height: 150, borderRadius: 75, background: C.green, transform: `scale(${f * (1 + 0.02 * Math.sin(t * 6))})`,
          display: "flex", alignItems: "center", justifyContent: "center", fontFamily: MONO, fontWeight: 800, fontSize: 76, color: "#000", boxShadow: `0 0 60px ${C.green}` }}>FOLLOW</div>
      )}
      <Txt y={1260} size={150} scale={bounce(frame, cF + 0.15)} rotate={Math.sin(t * 8) * 5}>🔥</Txt>
      <Confetti t={t} cue={cF} y={1020} />
    </>
  );
};

// ---------------------------------------------------------------- captions (karaoke)
const CHUNKS = captionChunks();
const Captions: React.FC = () => {
  const { t } = useT();
  const ch = CHUNKS.find((c) => t >= c.start && t < c.end);
  if (!ch) return null;
  const activeIdx = ch.words.reduce((a, w, i) => (t >= w.t - 0.02 ? i : a), -1);
  return (
    <div style={{ position: "absolute", left: 50, right: 50, bottom: 90, padding: "22px 30px", borderRadius: 30, background: "#000", border: "3px solid #282828", textAlign: "center",
      fontFamily: SANS, fontWeight: 800, fontSize: 46, lineHeight: 1.3, display: "flex", flexWrap: "wrap", justifyContent: "center", columnGap: 16 }}>
      {ch.words.map((w, i) => (
        <span key={i} style={{ color: i === activeIdx ? C.green : i < activeIdx ? C.white : "#8d8d8d", display: "inline-block",
          transform: i === activeIdx ? "scale(1.08)" : "scale(1)", textShadow: i === activeIdx ? `0 0 18px ${C.green}88` : "none" }}>{w.w}</span>
      ))}
    </div>
  );
};

// ---------------------------------------------------------------- root
export const Day6: React.FC = () => {
  const { frame, t } = useT();
  const shake = (cue: number, amp = 14) => (t > cue ? amp * Math.exp(-(t - cue) * 9) * Math.sin((t - cue) * 70) : 0);
  const sx = shake(T(1, "coding")) + shake(T(3, "SDLC")) + shake(T(6, "SDLC")) + shake(T(25, "6!"), 10);
  const sy = shake(T(3, "SDLC"), 10) + shake(T(6, "SDLC"), 10);
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Audio src={staticFile("day6-voiceover.mp3")} />
      <Background />
      <AbsoluteFill style={{ transform: `translate(${sx}px,${sy}px)` }}>
        <Scene a={0} b={5.2}><SceneHook /></Scene>
        <Scene a={5.2} b={14.0}><SceneJourney /></Scene>
        <Scene a={14.0} b={19.95}><SceneRecap /></Scene>
        <Scene a={19.95} b={53.0} fade={0.35}><SceneRoadmap /></Scene>
        <Scene a={53.0} b={56.4}><SceneDay6 /></Scene>
        <Scene a={56.4} b={61.15}><SceneDay7 /></Scene>
        <Scene a={61.15} b={DURATION_SEC + 1}><SceneCTA /></Scene>
      </AbsoluteFill>
      <Header progress={t / DURATION_SEC} />
      <Captions />
    </AbsoluteFill>
  );
};
