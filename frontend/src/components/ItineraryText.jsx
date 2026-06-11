import ReactMarkdown from "react-markdown";

const styles = {
  container: {
    maxWidth: 720,
    margin: "0 auto",
    padding: "24px 28px",
    lineHeight: 1.6,
    background: "var(--color-surface)",
    borderRadius: "var(--radius-lg)",
    boxShadow: "var(--shadow-card)",
    fontFamily: "var(--font-body)",
    color: "var(--color-text)",
  },
  empty: {
    padding: "32px 16px",
    color: "var(--color-text-muted)",
    textAlign: "center",
    background: "var(--color-surface)",
    borderRadius: "var(--radius-lg)",
    boxShadow: "var(--shadow-card)",
    fontFamily: "var(--font-body)",
  },
};

export default function ItineraryText({ plan }) {
  const narrative = plan?.narrative;

  if (!narrative) {
    return (
      <div style={styles.empty}>
        Read the detailed itinerary and instructions.
      </div>
    );
  }

  return (
    <div className="itinerary-text" style={styles.container}>
      <ReactMarkdown>{narrative}</ReactMarkdown>
    </div>
  );
}
