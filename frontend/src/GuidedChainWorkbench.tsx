import { useEffect, useRef, useState } from "react";

type Chain = { period_count: number; chain_id: string; content_digest: string; period_chain_input: Record<string, unknown> };
type Build = { valid: boolean; content_digest: string; bundle_id: string; candidate_count: number; chains: Chain[] };
type Source = { scenario_id: string; variant_id: string; source_note: string; period_contexts: { period: number; profile: { context: { rng_seed: number } }; candidate_input: Record<string, unknown> }[] };
type Reference = { chain_id: string; expected_content_digest: string; expected_result_digest: string };
const BASE = "/api/strategies/guided-period-chain";

async function post(url: string, value: unknown) {
  const response = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(value) });
  const body = await response.json();
  if (!response.ok || body.valid === false) throw new Error(body.issues?.[0]?.message || body.message || "Die Kettenaktion ist fehlgeschlagen.");
  if (url.startsWith(BASE) && body.content_digest && response.headers.get("etag") !== `"${body.content_digest}"`) throw new Error("Antwortnachweis passt nicht zum geprüften Quellenvertrag.");
  return body;
}

export default function GuidedChainWorkbench({ onStored, seminarSource }: { onStored: () => void; seminarSource?: unknown }) {
  const [seed, setSeed] = useState("1300"), [runIndex, setRunIndex] = useState("0");
  const [source, setSource] = useState<Source | null>(null), [expert, setExpert] = useState("");
  const [dirty, setDirty] = useState(false), [checked, setChecked] = useState<Build | null>(null);
  const [stored, setStored] = useState<Build | null>(null), [storageRelease, setStorageRelease] = useState(false);
  const [runRelease, setRunRelease] = useState(false), [prefixReady, setPrefixReady] = useState(false);
  const [actor, setActor] = useState("workbench-ui"), [reason, setReason] = useState("Deklarierten Workshopfall über stabile Prefixe prüfen");
  const [busy, setBusy] = useState(false), [error, setError] = useState<string | null>(null);
  const revision = useRef(0);
  function invalidate() {
    revision.current++; setChecked(null); setStored(null); setStorageRelease(false); setRunRelease(false); setPrefixReady(false); setError(null);
  }
  useEffect(() => {
    if (seminarSource) { invalidate(); setSource(seminarSource as Source); setExpert(JSON.stringify(seminarSource, null, 2)); setDirty(false); setBusy(false); }
  }, [seminarSource]);
  async function act(work: (version: number) => Promise<void>) {
    const version = revision.current;
    setBusy(true); setError(null);
    try { await work(version); }
    catch (failure) { if (version === revision.current) setError(failure instanceof Error ? failure.message : "Kettenaktion fehlgeschlagen."); }
    finally { if (version === revision.current) setBusy(false); }
  }
  async function generate() {
    invalidate();
    await act(async version => {
      const result = await post(`${BASE}/workshop-case`, { seed: Number(seed), run_index: Number(runIndex) });
      if (revision.current === version) { setSource(result.source_input); setExpert(JSON.stringify(result.source_input, null, 2)); setDirty(false); }
    });
  }
  async function check() {
    await act(async version => {
      const next = dirty ? JSON.parse(expert) : source;
      const result = await post(`${BASE}/build`, next);
      if (revision.current === version) { setSource(next); setExpert(JSON.stringify(next, null, 2)); setDirty(false); setChecked(result); setStored(null); setStorageRelease(false); }
    });
  }
  async function save() {
    if (!checked || !source || !storageRelease) return;
    await act(async version => {
      const result = await post(`${BASE}/store`, { schema_version: "ims.guided-period-chain-store-request.v1", source_input: source, expected_content_digest: checked.content_digest, stored_at: new Date().toISOString(), explicit_storage_release: true });
      if (result.content_digest !== checked.content_digest || result.stored !== true) throw new Error("Speichernachweis hat sich geändert.");
      if (revision.current === version) { setStored(result); setStorageRelease(false); onStored(); }
    });
  }
  async function references() {
    if (!stored || !runRelease || !actor.trim() || !reason.trim()) return;
    await act(async version => {
      const two = stored.chains.find(c => c.period_count === 2)!;
      const five = stored.chains.find(c => c.period_count === 5)!;
      function release(chain: Chain) {
        return { schema_version: "ims.strategy-execution-period-chain-run-control-request.v1", chain_id: chain.chain_id, expected_content_digest: chain.content_digest, idempotency_key: `guided-reference-${crypto.randomUUID()}`, explicit_run_control_release: true, released_by: actor.trim(), released_at: new Date().toISOString(), release_reason: reason.trim() };
      }
      async function existing(chain: Chain, prefix: string): Promise<Reference | null> {
        const response = await fetch(`/api/run-control/${prefix}-result/${encodeURIComponent(chain.chain_id)}`);
        const body = await response.json();
        if (!response.ok) throw new Error(body.message || "Gespeicherter Prefix kann nicht geprüft werden.");
        if (!body.result_available) return null;
        const record = body.record;
        if (!record || record.chain_id !== chain.chain_id || record.content_digest !== chain.content_digest || !record.result_digest) throw new Error("Prefixnachweis hat sich geändert.");
        return { chain_id: record.chain_id, expected_content_digest: record.content_digest, expected_result_digest: record.result_digest };
      }
      let twoRef = await existing(two, "strategy-period-chain-effect-probe");
      if (!twoRef) {
        const result = await post("/api/run-control/strategy-period-chain-effect-probe-start", { schema_version: "ims.strategy-execution-period-chain-effect-probe-request.v1", release: release(two), explicit_two_period_effect_probe_execution: true });
        twoRef = { chain_id: result.record.chain_id, expected_content_digest: result.record.content_digest, expected_result_digest: result.record.result_digest };
      }
      if (twoRef.chain_id !== two.chain_id || twoRef.expected_content_digest !== two.content_digest || !twoRef.expected_result_digest) throw new Error("Zwei-Perioden-Nachweis passt nicht zur freigegebenen Kette.");
      if (revision.current !== version) return;
      let fiveRef = await existing(five, "strategy-period-chain-five-period-effect-probe");
      if (!fiveRef) {
        const result = await post("/api/run-control/strategy-period-chain-five-period-effect-probe-start", { schema_version: "ims.strategy-execution-five-period-effect-probe-start-request.v1", effect_probe_request: { schema_version: "ims.strategy-execution-five-period-effect-probe-request.v1", period_chain_input: five.period_chain_input, prefix_baseline: twoRef, explicit_five_period_effect_probe_execution: true }, release: release(five), explicit_five_period_effect_probe_start: true });
        fiveRef = { chain_id: result.record.chain_id, expected_content_digest: result.record.content_digest, expected_result_digest: result.record.result_digest };
      }
      if (fiveRef.chain_id !== five.chain_id || fiveRef.expected_content_digest !== five.content_digest || !fiveRef.expected_result_digest) throw new Error("Fünf-Perioden-Nachweis passt nicht zur freigegebenen Kette.");
      if (revision.current === version) { setPrefixReady(true); setRunRelease(false); onStored(); }
    });
  }
  return <section className="panel ict-workbench guided-chain" data-testid="guided-chain-workbench" aria-label="Geführter 100-Perioden-Aufbau">
    <h2>100-Perioden-Fall selbst aufbauen</h2>
    <p>Ein deklarierter synthetischer Vdefmd6-Fall mit einem VU und einem VN. Die zwei historischen Positionen haben hier keine Kfz-/Sach-Zuordnung. Erzeugung, Prüfung, Speicherung und Lauf bleiben getrennte Aktionen.</p>
    {error && <p role="alert" className="ict-error">{error}</p>}
    <div className="ict-fields"><label>Seed<input aria-label="100er Seed" type="number" min="0" max="2147483647" disabled={busy} value={seed} onChange={e => { invalidate(); setSeed(e.target.value); setSource(null); setDirty(false); }} /></label><label>Laufindex<input aria-label="100er Laufindex" type="number" min="0" max="0" disabled={busy} value={runIndex} onChange={e => { invalidate(); setRunIndex(e.target.value); setSource(null); setDirty(false); }} /></label></div>
    <p>Der Assistent verwendet Laufindex 0. Der historische Globalperiodenexport hängt bei weiteren Laufindizes vom Horizont ab; dafür besteht hier noch kein gemeinsamer Prefixvertrag. Eigenständige Fälle erhalten verschiedene Seeds und Kettennachweise.</p>
    <button type="button" disabled={busy || !seed.trim() || !runIndex.trim()} onClick={generate}>100 vollständige Kontexte erzeugen</button>
    {source && <><p>{source.source_note}</p><p>Periode 1: Seed {source.period_contexts[0].profile.context.rng_seed}; Periode 100: Seed {source.period_contexts[99].profile.context.rng_seed}. Keine Periodenkopie oder neu gezogene Zufallsfolge beim Start.</p>
      <details><summary>Expertenmodus: alle Periodenkontexte, Schocks und Zuweisungen</summary><p>Alle 100 Profile, Regelparameter, Zufallswerte und 99 Carryover-Übergänge sind ausdrücklich enthalten. Änderungen werden vollständig neu materialisiert und geprüft. Ungültige Eingaben speichern keine Teilkette.</p><label>100er Quellenvertrag<textarea aria-label="100er Quellenvertrag" rows={12} disabled={busy} value={expert} onChange={e => { invalidate(); setExpert(e.target.value); setDirty(true); }} /></label></details>
      <button type="button" disabled={busy} onClick={check}>Alle Periodenkontexte prüfen</button>
    </>}
    {checked && <div data-testid="guided-chain-checked"><p>100 Kontexte und {checked.candidate_count} frisch gebaute Kandidaten für die 2-, 5- und 100-Perioden-Ketten geprüft. Nachweis: <code>{checked.content_digest}</code></p>
      <label><input type="checkbox" disabled={busy} checked={storageRelease} onChange={e => setStorageRelease(e.target.checked)} />Die geprüften Kandidaten und Ketten unveränderlich lokal speichern.</label>
      <button type="button" disabled={busy || !storageRelease} onClick={save}>Geprüftes Bündel atomar speichern</button>
    </div>}
    {stored && <div data-testid="guided-chain-stored"><p>Unveränderliches Bündel gespeichert: <code>{stored.bundle_id}</code>. Wiederholung prüft vorhandene Inhalte und erzeugt keine Dubletten.</p><div className="ict-fields"><label>Verantwortlich<input aria-label="Prefix Verantwortlich" disabled={busy} value={actor} onChange={e => { setActor(e.target.value); setRunRelease(false); }} /></label><label>Grund<input aria-label="Prefix Grund" disabled={busy} value={reason} onChange={e => { setReason(e.target.value); setRunRelease(false); }} /></label></div>
      <label><input type="checkbox" disabled={busy} checked={runRelease} onChange={e => setRunRelease(e.target.checked)} />Referenzläufe 1–2 und 1–5 ausführen und ihre unveränderlichen Ergebnisse speichern; vorhandene Nachweise erneut prüfen.</label>
      <button type="button" disabled={busy || !runRelease || !actor.trim() || !reason.trim()} onClick={references}>Referenzläufe kontrolliert vorbereiten</button>
    </div>}
    {prefixReady && <p role="status" data-testid="guided-prefix-ready">Prefix 1–5 ist bereit. Starten Sie darunter die geprüfte 100-Perioden-Kette mit ihrer eigenen Laufbestätigung. Ergebnisse und Vergleiche bleiben an die jeweilige Kette gebunden.</p>}
    {busy && <p role="status">Kontexte und Nachweise werden geprüft …</p>}
  </section>;
}
