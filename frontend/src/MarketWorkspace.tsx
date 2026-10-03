import { useState } from "react";
import MarketExplorerWorkbench from "./MarketExplorerWorkbench";
import MarketShockWorkbench from "./MarketShockWorkbench";
import MarketWorkbench from "./MarketWorkbench";
import WorkspaceTabs from "./WorkspaceTabs";

const modes = [
  { id: "explore", label: "Markt verstehen" },
  { id: "shock", label: "Schock bearbeiten" },
  { id: "source", label: "Quellen und Handfälle" },
];

export default function MarketWorkspace() {
  const [mode, setMode] = useState("explore");
  return <div className="market-workspace">
    <WorkspaceTabs id="market-mode" label="Markt-Arbeitsbereich" tabs={modes} selected={mode} onSelect={setMode} />
    <div role="tabpanel" id="market-mode-panel-explore" aria-labelledby="market-mode-tab-explore" hidden={mode !== "explore"}><MarketExplorerWorkbench /></div>
    <div role="tabpanel" id="market-mode-panel-shock" aria-labelledby="market-mode-tab-shock" hidden={mode !== "shock"}>
      <p className="workspace-context">Hier ändern Sie einen Schockfall und prüfen seine Wirkung. Dieser Arbeitsbereich behält seine eigenen Eingaben und Ergebnisse.</p><MarketShockWorkbench />
    </div>
    <div role="tabpanel" id="market-mode-panel-source" aria-labelledby="market-mode-tab-source" hidden={mode !== "source"}>
      <p className="workspace-context">Hier prüfen Sie die BaFin-Quelle und kleine Handfälle. Dieser Arbeitsbereich behält seine eigenen Eingaben und Ergebnisse.</p><MarketWorkbench />
    </div>
  </div>;
}
