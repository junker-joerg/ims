import { useEffect, useState } from "react";
import { version as frontendVersion } from "../package.json";

export default function ReleaseBadge() {
  const [backendVersion, setBackendVersion] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/version", { cache: "no-store", signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error("Version unavailable");
        const value = await response.json() as { version?: unknown };
        if (typeof value.version !== "string" || !value.version) throw new Error("Invalid version");
        if (!controller.signal.aborted) setBackendVersion(value.version);
      })
      .catch(() => { if (!controller.signal.aborted) setFailed(true); });
    return () => controller.abort();
  }, []);
  const mismatch = backendVersion !== null && backendVersion !== frontendVersion;
  return <div className={`release-badge${mismatch || failed ? " release-warning" : ""}`}
    role="status" aria-live="polite" aria-label="Release-Version" data-testid="release-version">
    <strong>Release {frontendVersion}</strong>
    {mismatch && <span>Anwendung: {backendVersion}. Unterschiedliche Versionen – IMS neu starten und Browserseite neu laden.</span>}
    {failed && <span>Anwendungsversion nicht erreichbar.</span>}
  </div>;
}
