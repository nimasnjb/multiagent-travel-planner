// Shared layout tokens for the top-level pages (Home, How it works, About)
// Solar data cloud style.

export const page = {
  minHeight: "100vh",
  background:
    "radial-gradient(circle at 12% 12%, rgba(255, 183, 3, 0.28), transparent 28%), radial-gradient(circle at 86% 8%, rgba(32, 151, 255, 0.18), transparent 32%), linear-gradient(180deg, var(--color-bg), var(--color-bg-deep))",
  fontFamily: "var(--font-body)",
  color: "var(--color-text)",
};

export const hero = {
  background:
    "linear-gradient(145deg, #ffffff 0%, #f1f7ff 56%, #fff0c2 100%)",
  padding: "70px 16px 60px",
  textAlign: "center",
  borderBottom: "1px solid var(--color-border)",
};

export const heroInner = {
  maxWidth: 780,
  margin: "0 auto",
};

export const eyebrow = {
  fontFamily: "var(--font-display)",
  fontSize: 12,
  fontWeight: 700,
  letterSpacing: "0.2em",
  textTransform: "uppercase",
  color: "var(--color-accent-active)",
  margin: "0 0 14px",
};

export const title = {
  fontFamily: "var(--font-display)",
  fontSize: "clamp(2.35rem, 5vw, 4rem)",
  fontWeight: 700,
  lineHeight: 1.08,
  letterSpacing: "-0.055em",
  margin: "0 0 16px",
  color: "var(--color-text)",
};

export const subtitle = {
  fontSize: 17,
  lineHeight: 1.7,
  color: "var(--color-text-muted)",
  margin: "0 0 34px",
};

export const main = {
  maxWidth: 900,
  margin: "0 auto",
  padding: "36px 16px 72px",
  display: "flex",
  flexDirection: "column",
  gap: 30,
};

export const card = {
  background: "var(--color-surface)",
  border: "1px solid var(--color-border)",
  borderRadius: "var(--radius-lg)",
  boxShadow: "var(--shadow-card)",
  padding: "24px 28px",
};

export const sectionTitle = {
  fontFamily: "var(--font-display)",
  fontSize: "1.42rem",
  fontWeight: 700,
  lineHeight: 1.18,
  letterSpacing: "-0.04em",
  margin: "0 0 10px",
  color: "var(--color-text)",
};

export const bodyText = {
  fontSize: 15,
  lineHeight: 1.72,
  color: "var(--color-text)",
  margin: 0,
};
