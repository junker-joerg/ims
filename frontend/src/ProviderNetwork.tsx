import { amountUnits } from "./seminarPresentation";
import { str, type Row } from "./marketExplorerPresentation";

/** Declared edges and actual lost hours. Geometry is only a network projection. */
export default function ProviderNetwork({ assets, actual, selected, onSelect }: {
  assets: Row[]; actual: Row[]; selected: string; onSelect: (id: string) => void;
}) {
  const upper=assets.filter(a=>Array.isArray(a.depends_on)&&a.depends_on.length), lower=assets.filter(a=>!Array.isArray(a.depends_on)||!a.depends_on.length);
  const nodes=[...upper.map((a,i)=>({asset:a,x:90+i*640/Math.max(1,upper.length-1),y:100})),...lower.map((a,i)=>({asset:a,x:70+i*680/Math.max(1,lower.length-1),y:270}))];
  const lost=(id:unknown)=>amountUnits(str(actual.find(r=>r.asset_id===id),"lost_equivalent_hours"));
  return <figure className="network-figure"><figcaption><strong>Abhängigkeiten werden Geschäftswirkung.</strong><span>Auswahl anklicken · tatsächliche Ausfallstunden dieser Periode</span></figcaption>
    <svg viewBox="0 0 820 380" role="group" aria-label="ICT-Abhängigkeitsnetz mit tatsächlichem Ausfallstatus" className="provider-network">
      <defs><linearGradient id="network-plane" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stopColor="#132b42"/><stop offset="100%" stopColor="#071625"/></linearGradient></defs>
      <path d="M20 48L795 28L810 180L35 200Z" fill="url(#network-plane)" stroke="#244966"/>
      <path d="M20 225L795 205L810 345L35 365Z" fill="url(#network-plane)" stroke="#244966"/>
      <text x="34" y="68" className="network-layer">PROZESS- UND ERSATZPFADE</text><text x="34" y="245" className="network-layer">DEKLARIERTE VORLEISTUNGEN</text>
      {nodes.flatMap(node=>(Array.isArray(node.asset.depends_on)?node.asset.depends_on as string[]:[]).map(id=>{const target=nodes.find(n=>n.asset.asset_id===id);return target&&<path key={`${node.asset.asset_id}-${id}`} d={`M${node.x} ${node.y+18}C${node.x} ${node.y+110},${target.x} ${target.y-100},${target.x} ${target.y-8}`} className={lost(id)>0n?"network-edge affected":"network-edge"}/>;}))}
      {nodes.map(({asset,x,y})=>{const id=String(asset.asset_id),failure=lost(id)>0n;return <g key={id} className={`network-node ${failure?"affected":"available"} ${selected===id?"selected":""}`} role="button" tabIndex={0} aria-pressed={selected===id} aria-label={`${asset.label}: ${failure?"betroffen":"keine Ausfallstunden"}; Abhängigkeit prüfen`} onClick={()=>onSelect(id)} onKeyDown={e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();onSelect(id);}}}>
        <title>{String(asset.label)} · {str(actual.find(r=>r.asset_id===id),"lost_equivalent_hours")} ausgefallene Stunden</title>
        <ellipse cx={x} cy={y+23} rx="39" ry="12" className="network-halo"/>
        <path d={`M${x-28} ${y-12}L${x+3} ${y-23}L${x+31} ${y-12}L${x} ${y}Z`} className="node-top"/>
        <path d={`M${x-28} ${y-12}L${x} ${y}L${x} ${y+23}L${x-28} ${y+11}Z`} className="node-left"/>
        <path d={`M${x} ${y}L${x+31} ${y-12}L${x+31} ${y+11}L${x} ${y+23}Z`} className="node-right"/>
        <text x={x} y={y+48} textAnchor="middle" className="node-name">{id}</text><text x={x} y={y+67} textAnchor="middle" className="node-state">{failure?`${str(actual.find(r=>r.asset_id===id),"lost_equivalent_hours")} h betroffen`:"keine Ausfallstunden"}</text>
      </g>;})}
    </svg><div className="network-legend"><span><i/>Kein Ausfall in P</span><span><i className="affected"/>Tatsächlich betroffen</span><span>Linie = deklarierte Abhängigkeit · gemeinsame Ressourcen einmal gezählt</span></div>
  </figure>;
}
