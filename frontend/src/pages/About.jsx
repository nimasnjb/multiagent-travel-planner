import * as s from "./pageStyles.js";

const REPO_URL = "https://github.com/nimasnjb/multiagent-travel-planner";
const AUTHOR_NAME = "NimaSNJB";
const GITHUB_PROFILE_URL = "https://github.com/nimasnjb";

const styles = {
  list: {
    display: "flex",
    flexDirection: "column",
    gap: 12,
    margin: "12px 0 0",
    padding: 0,
    listStyle: "none",
  },
  link: {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    color: "var(--color-accent-active)",
    fontWeight: 600,
    textDecoration: "none",
    fontSize: 15,
  },
};

export default function About() {
  return (
    <div style={s.page}>
      <header style={s.hero}>
        <div style={s.heroInner}>
          <p style={s.eyebrow}>About this project</p>
          <h1 style={s.title}>About</h1>
          <p style={s.subtitle}>
            A small showcase of a real LangGraph multi-agent pipeline,
            planning trips end to end with OpenRouteService and OR-Tools.
          </p>
        </div>
      </header>

      <main style={s.main}>
        <div style={s.card}>
          <h2 style={s.sectionTitle}>Built by</h2>
          <p style={s.bodyText}>{AUTHOR_NAME}</p>

          <ul style={styles.list}>
            <li>
              <a style={styles.link} href={REPO_URL} target="_blank" rel="noreferrer">
                Project repo on GitHub ↗
              </a>
            </li>
            <li>
              <a style={styles.link} href={GITHUB_PROFILE_URL} target="_blank" rel="noreferrer">
                GitHub profile ↗
              </a>
            </li>
          </ul>
        </div>
      </main>
    </div>
  );
}
