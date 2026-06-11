import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet";
import { useEffect, useMemo } from "react";

// Leaflet's default marker icons rely on webpack asset URLs that Vite doesn't
// wire up automatically — fix by pointing directly at the CDN copies.
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

// One distinct color per day (cycles if > 6 days).
const DAY_COLORS = ["#e63946", "#2196f3", "#4caf50", "#ff9800", "#9c27b0", "#00bcd4"];

function dayColor(dayIndex) {
  return DAY_COLORS[dayIndex % DAY_COLORS.length];
}

// Inner component: fits map bounds whenever stops change.
function BoundsFitter({ positions }) {
  const map = useMap();
  useEffect(() => {
    if (positions.length > 0) {
      map.fitBounds(L.latLngBounds(positions), { padding: [40, 40] });
    }
  }, [map, positions]);
  return null;
}

export default function ItineraryMap({ plan }) {
  const days = plan?.days ?? [];
  const hasStops = days.some((d) => d.stops?.length > 0);

  // Flat list of [lat, lng] for bounds fitting — includes leg geometry so
  // the fit covers the actual street route, not just the stop pins.
  const allPositions = useMemo(
    () => days.flatMap((d) => (d.stops ?? []).flatMap((s) => {
      const points = [[s.lat, s.lng]];
      if (s.leg_to_next?.geometry?.length) {
        points.push(...s.leg_to_next.geometry.map(([lng, lat]) => [lat, lng]));
      }
      return points;
    })),
    [days],
  );

  if (!hasStops) {
    return (
      <div
        style={{
          padding: "32px 16px",
          color: "var(--color-text-muted)",
          textAlign: "center",
          background: "var(--color-surface)",
          borderRadius: "var(--radius-lg)",
          boxShadow: "var(--shadow-card)",
          fontFamily: "var(--font-body)",
        }}
      >
        We map your trip right here!
      </div>
    );
  }

  // Default center before BoundsFitter runs — first stop.
  const firstStop = days[0].stops[0];
  const defaultCenter = [firstStop.lat, firstStop.lng];

  return (
    <div
      style={{
        background: "var(--color-surface)",
        borderRadius: "var(--radius-lg)",
        boxShadow: "var(--shadow-card)",
        padding: 12,
      }}
    >
      <MapContainer
        center={defaultCenter}
        zoom={13}
        style={{ height: 420, width: "100%", borderRadius: "var(--radius-md)" }}
        scrollWheelZoom={true}
      >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <BoundsFitter positions={allPositions} />

      {days.map((day, di) => {
        const stops = day.stops ?? [];
        const color = dayColor(di);

        return (
          <span key={day.day}>
            {stops.map((stop) => (
              <Marker key={stop.id} position={[stop.lat, stop.lng]}>
                <Popup>
                  <strong>{stop.name}</strong>
                  <br />
                  Day {day.day}
                  {stop.arrival && (
                    <>
                      <br />
                      {stop.arrival} – {stop.depart}
                    </>
                  )}
                  {stop.leg_to_next && (
                    <>
                      <br />
                      {Math.round(stop.leg_to_next.minutes)} min to next stop
                    </>
                  )}
                </Popup>
              </Marker>
            ))}

            {stops.slice(0, -1).map((stop, i) => {
              const next = stops[i + 1];
              const geometry = stop.leg_to_next?.geometry;
              // ORS returns [lng, lat]; Leaflet wants [lat, lng]. Fall back to
              // a straight segment between the two stops if geometry is missing.
              const segment = geometry?.length
                ? geometry.map(([lng, lat]) => [lat, lng])
                : [[stop.lat, stop.lng], [next.lat, next.lng]];

              return (
                <Polyline
                  key={`${stop.id}-leg`}
                  positions={segment}
                  color={color}
                  weight={3}
                  opacity={0.8}
                />
              );
            })}
          </span>
        );
      })}
      </MapContainer>
    </div>
  );
}
