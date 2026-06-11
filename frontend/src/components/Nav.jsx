import { NavLink } from "react-router-dom";

const styles = {
  nav: {
    position: "sticky",
    top: 0,
    zIndex: 20,
    display: "flex",
    justifyContent: "center",
    flexWrap: "wrap",
    gap: 8,
    padding: "12px 16px",
    background: "var(--color-surface)",
    borderBottom: "1px solid var(--color-border)",
    boxShadow: "var(--shadow-card)",
  },
  link: {
    fontFamily: "var(--font-body)",
    fontWeight: 600,
    fontSize: 14,
    textDecoration: "none",
    color: "var(--color-text-muted)",
    padding: "8px 16px",
    borderRadius: "var(--radius-pill)",
    transition: "background 0.2s ease, color 0.2s ease",
  },
  linkActive: {
    color: "var(--color-accent-active)",
    background: "var(--color-accent-soft)",
  },
};

const LINKS = [
  { to: "/", label: "Home", end: true },
  { to: "/how-it-works", label: "How it works", end: false },
  { to: "/about", label: "About", end: false },
];

export default function Nav() {
  return (
    <nav style={styles.nav} aria-label="Main navigation">
      {LINKS.map(({ to, label, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          style={({ isActive }) => ({
            ...styles.link,
            ...(isActive ? styles.linkActive : {}),
          })}
        >
          {label}
        </NavLink>
      ))}
    </nav>
  );
}
