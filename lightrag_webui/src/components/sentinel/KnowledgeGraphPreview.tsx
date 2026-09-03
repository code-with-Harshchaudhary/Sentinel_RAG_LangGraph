import { useMemo, useState } from 'react'
import { cn } from '@/lib/utils'

type KnowledgeGraphPreviewProps = {
  active?: boolean
  className?: string
  label?: string
}

const nodes = [
  { id: 'knowledge', label: 'Knowledge', color: 'cyan', x: 150, y: 92, r: 18 },
  { id: 'people', label: 'People', color: 'emerald', x: 88, y: 52, r: 13 },
  { id: 'insights', label: 'Insights', color: 'amber', x: 223, y: 49, r: 14 },
  { id: 'actions', label: 'Actions', color: 'fuchsia', x: 274, y: 108, r: 13 },
  { id: 'sources', label: 'Sources', color: 'blue', x: 150, y: 151, r: 13 },
  { id: 'topics', label: 'Topics', color: 'violet', x: 68, y: 111, r: 12 },
  { id: 'person-a', label: 'Entity', color: 'cyan', x: 45, y: 82, r: 5 },
  { id: 'person-b', label: 'Entity', color: 'emerald', x: 112, y: 93, r: 5 },
  { id: 'insight-a', label: 'Finding', color: 'amber', x: 198, y: 87, r: 5 },
  { id: 'insight-b', label: 'Finding', color: 'fuchsia', x: 253, y: 75, r: 5 },
  { id: 'action-a', label: 'Task', color: 'blue', x: 208, y: 153, r: 5 },
  { id: 'topic-a', label: 'Concept', color: 'violet', x: 93, y: 150, r: 5 },
  { id: 'topic-b', label: 'Concept', color: 'cyan', x: 25, y: 133, r: 4 },
  { id: 'action-b', label: 'Task', color: 'emerald', x: 285, y: 149, r: 4 },
  { id: 'source-a', label: 'Document', color: 'blue', x: 118, y: 176, r: 4 }
] as const

const links = [
  ['knowledge', 'people'], ['knowledge', 'insights'], ['knowledge', 'actions'],
  ['knowledge', 'sources'], ['knowledge', 'topics'], ['people', 'person-a'],
  ['people', 'person-b'], ['insights', 'insight-a'], ['insights', 'insight-b'],
  ['actions', 'action-b'], ['actions', 'action-a'], ['sources', 'source-a'],
  ['sources', 'topic-a'], ['topics', 'topic-b'], ['topics', 'topic-a'],
  ['person-b', 'topic-a'], ['insight-a', 'action-a']
] as const

/** Lightweight interactive SVG used by the dashboard. The full graph editor
 * remains in GraphViewer, so this adds no second graph-data request. */
export default function KnowledgeGraphPreview({
  active = false,
  className,
  label = 'Interactive knowledge graph preview'
}: KnowledgeGraphPreviewProps) {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<string>('knowledge')
  const focusedNode = hoveredNode || selectedNode

  const nodeMap = useMemo(
    () => new Map<string, (typeof nodes)[number]>(nodes.map((node) => [node.id, node])),
    []
  )
  const relatedNodes = useMemo(() => {
    const related = new Set<string>([focusedNode])
    links.forEach(([source, target]) => {
      if (source === focusedNode) related.add(target)
      if (target === focusedNode) related.add(source)
    })
    return related
  }, [focusedNode])

  return (
    <svg
      viewBox="0 0 310 200"
      role="group"
      aria-label={label}
      className={cn('sentinel-graph-preview', active && 'is-active', className)}
      onMouseLeave={() => setHoveredNode(null)}
    >
      <defs>
        {['cyan', 'emerald', 'amber', 'fuchsia', 'blue', 'violet'].map((color) => (
          <filter id={`sentinel-glow-${color}`} key={color} x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        ))}
      </defs>
      <g className="sentinel-graph-links">
        {links.map(([sourceId, targetId]) => {
          const source = nodeMap.get(sourceId)!
          const target = nodeMap.get(targetId)!
          const isRelated = sourceId === focusedNode || targetId === focusedNode
          return (
            <path
              key={`${sourceId}-${targetId}`}
              className={cn(isRelated && 'is-related', !isRelated && 'is-dimmed')}
              d={`M ${source.x} ${source.y} Q ${(source.x + target.x) / 2} ${(source.y + target.y) / 2 - 12} ${target.x} ${target.y}`}
            />
          )
        })}
      </g>
      <g className="sentinel-graph-nodes">
        {nodes.map((node, index) => {
          const isFocused = node.id === focusedNode
          const isRelated = relatedNodes.has(node.id)
          return (
            <g
              key={node.id}
              role="button"
              tabIndex={0}
              aria-label={`${node.label} node`}
              aria-pressed={selectedNode === node.id}
              className={cn(`node node-${node.color}`, isFocused && 'is-focused', isRelated && 'is-related', !isRelated && 'is-dimmed')}
              style={{ animationDelay: `${index * 90}ms` }}
              onMouseEnter={() => setHoveredNode(node.id)}
              onFocus={() => setHoveredNode(node.id)}
              onBlur={() => setHoveredNode(null)}
              onClick={() => setSelectedNode(node.id)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault()
                  setSelectedNode(node.id)
                }
              }}
            >
              <circle cx={node.x} cy={node.y} r={node.r + 6} className="node-aura" />
              <circle cx={node.x} cy={node.y} r={node.r} filter={`url(#sentinel-glow-${node.color})`} />
              {node.r > 10 && <circle cx={node.x} cy={node.y} r={node.r - 5} className="node-core" />}
              {isFocused && (
                <g className="node-tooltip" aria-hidden="true">
                  <rect x={node.x - 29} y={node.y - node.r - 24} width="58" height="16" rx="6" />
                  <text x={node.x} y={node.y - node.r - 13}>{node.label}</text>
                </g>
              )}
            </g>
          )
        })}
      </g>
    </svg>
  )
}
