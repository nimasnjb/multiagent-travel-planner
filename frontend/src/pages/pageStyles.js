// Shared layout tokens for the top-level pages (Home, How it works, About)
// so each page keeps the same warm travel-magazine look and feel.

export const page = {
  minHeight: "100vh",
  background: "var(--color-bg)",
  fontFamily: "var(--font-body)",
  color: "var(--color-text)",
};

export const hero = {
  background:
    "linear-gradient(160deg, #ffe9d6 0%, #ffd9b8 55%, #ffc9a3 100%)",
  padding: "64px 16px 56px",
  textAlign: "center",
};

export const heroInner = {
  maxWidth: 720,
  margin: "0 auto",
};

export const eyebrow = {
  fontFamily: "var(--font-body)",
  fontSize: 13,
  fontWeight: 700,
  letterSpacing: "0.2em",
  textTransform: "uppercase",
  color: "var(--color-accent-active)",
  margin: "0 0 12px",
};

export const title = {
  fontFamily: "var(--font-display)",
  fontSize: "clamp(2.25rem, 5vw, 3.6rem)",
  fontWeight: 700,
  lineHeight: 1.1,
  margin: "0 0 14px",
  color: "var(--color-text)",
};

export const subtitle = {
  fontSize: 17,
  lineHeight: 1.6,
  color: "var(--color-text-muted)",
  margin: "0 0 32px",
};

export const main = {
  maxWidth: 880,
  margin: "0 auto",
  padding: "32px 16px 64px",
  display: "flex",
  flexDirection: "column",
  gap: 28,
};

export const card = {
  background: "var(--color-surface)",
  borderRadius: "var(--radius-lg)",
  boxShadow: "var(--shadow-card)",
  padding: "20px 24px",
};

export const sectionTitle = {
  fontFamily: "var(--font-display)",
  fontSize: "1.4rem",
  fontWeight: 700,
  margin: "0 0 8px",
  color: "var(--color-text)",
};

export const bodyText = {
  fontSize: 15,
  lineHeight: 1.7,
  color: "var(--color-text)",
  margin: 0,
};
