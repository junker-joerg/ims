import { useRef } from "react";

export type WorkspaceTab = { id: string; label: string };

/** Local view selection only: mounted panels retain inputs and results. */
export default function WorkspaceTabs({ id, label, tabs, selected, onSelect }: {
  id: string; label: string; tabs: WorkspaceTab[]; selected: string;
  onSelect: (id: string) => void;
}) {
  const buttons = useRef<Record<string, HTMLButtonElement | null>>({});
  return <div className="workspace-tabs" role="tablist" aria-label={label}>
    {tabs.map((tab, index) => <button key={tab.id} type="button" role="tab"
      id={`${id}-tab-${tab.id}`} aria-controls={`${id}-panel-${tab.id}`}
      aria-selected={selected === tab.id} tabIndex={selected === tab.id ? 0 : -1}
      ref={node => { buttons.current[tab.id] = node; }}
      onClick={() => onSelect(tab.id)} onKeyDown={event => {
        const next = event.key === "ArrowRight" ? (index + 1) % tabs.length
          : event.key === "ArrowLeft" ? (index + tabs.length - 1) % tabs.length
          : event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 : null;
        if (next === null) return;
        event.preventDefault(); onSelect(tabs[next].id); buttons.current[tabs[next].id]?.focus();
      }}>{tab.label}</button>)}
  </div>;
}
