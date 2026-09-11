import { useMemo, useState } from "react";
import { ReactFlow, Background, Controls, MiniMap } from "@xyflow/react";
import { fraudNetworkData } from "../data/fraudNetworkData";
import "@xyflow/react/dist/style.css";

import FraudNode from "./FraudNode";
import { theme, FONT_UI, FONT_MONO, riskTone } from "../theme";

const nodeTypes = {
  fraud: FraudNode,
};

// Data is stateful so the API integrator can replace it with a fetch call.
// Expected shape: { nodes: Array<{id, type, position, data}>, edges: Array<{id, source, target, label}> }
function FraudNetwork() {
  const [graphData] = useState(fraudNetworkData);
  const { nodes, edges } = graphData;
  const [selectedNode, setSelectedNode] = useState(null);
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("All");

  // Find all nodes directly connected to selected node
  const connectedNodeIds = useMemo(() => {
    if (!selectedNode) return new Set();

    const connected = new Set([selectedNode.id]);

    edges.forEach((edge) => {
      if (edge.source === selectedNode.id) {
        connected.add(edge.target);
      }

      if (edge.target === selectedNode.id) {
        connected.add(edge.source);
      }
    });

    return connected;
  }, [selectedNode]);

  const filteredNodes = useMemo(() => {
    return nodes.filter((node) => {
      const searchText = search.toLowerCase();

      const matchesSearch =
        node.data.value.toLowerCase().includes(searchText) ||
        node.data.type.toLowerCase().includes(searchText);

      let matchesRisk = true;

      if (riskFilter === "Low") {
        matchesRisk = node.data.risk !== undefined && node.data.risk <= 30;
      }

      if (riskFilter === "Medium") {
        matchesRisk =
          node.data.risk !== undefined &&
          node.data.risk >= 31 &&
          node.data.risk <= 70;
      }

      if (riskFilter === "High") {
        matchesRisk = node.data.risk !== undefined && node.data.risk >= 71;
      }

      return matchesSearch && matchesRisk;
    });
  }, [search, riskFilter]);

  const visibleNodeIds = new Set(filteredNodes.map((node) => node.id));

  const filteredEdges = edges.filter(
    (edge) =>
      visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target),
  );

  // Add highlighting to nodes
  const displayNodes = filteredNodes.map((node) => {
    if (!selectedNode) {
      return node;
    }

    const isConnected = connectedNodeIds.has(node.id);

    return {
      ...node,
      style: {
        opacity: isConnected ? 1 : 0.25,
        transition: "opacity 0.2s ease",
      },
    };
  });

  // Highlight connected relationships
  const displayEdges = filteredEdges.map((edge) => {
    if (!selectedNode) {
      return edge;
    }

    const isConnected =
      edge.source === selectedNode.id || edge.target === selectedNode.id;

    return {
      ...edge,
      style: {
        stroke: isConnected ? theme.brand : theme.border,
        strokeWidth: isConnected ? 2.5 : 1,
        opacity: isConnected ? 1 : 0.2,
      },
      labelStyle: {
        fill: isConnected ? theme.text : theme.textFaint,
        fontFamily: FONT_UI,
        fontSize: 11,
        fontWeight: 600,
      },
    };
  });

  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        background: theme.bg,
        color: theme.text,
        fontFamily: FONT_UI,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* HEADER */}
      <header
        style={{
          height: 72,
          minHeight: 72,
          background: theme.panel,
          borderBottom: `1px solid ${theme.border}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
          boxSizing: "border-box",
          zIndex: 20,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 700,
            }}
          >
            Fraud Network
          </div>

          <div
            style={{
              color: theme.textDim,
              fontSize: 12,
              marginTop: 4,
            }}
          >
            Relationship & suspicious activity visualization
          </div>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search entities..."
            style={{
              width: 220,
              height: 38,
              boxSizing: "border-box",
              padding: "0 12px",
              background: theme.surface,
              color: theme.text,
              border: `1px solid ${theme.border}`,
              borderRadius: 8,
              outline: "none",
              fontFamily: FONT_UI,
              fontSize: 12,
            }}
          />

          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            style={{
              height: 38,
              padding: "0 12px",
              background: theme.surface,
              color: theme.text,
              border: `1px solid ${theme.border}`,
              borderRadius: 8,
              outline: "none",
              fontFamily: FONT_UI,
              fontSize: 12,
              cursor: "pointer",
              colorScheme: "dark",
            }}
          >
            <option value="All">All Risk</option>
            <option value="Low">Low Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="High">High Risk</option>
          </select>
        </div>
      </header>

      {/* MAIN */}
      <div
        style={{
          flex: 1,
          minHeight: 0,
          display: "flex",
          overflow: "hidden",
        }}
      >
        {/* GRAPH */}
        <div
          style={{
            flex: 1,
            minWidth: 0,
            minHeight: 0,
            position: "relative",
          }}
        >
          <ReactFlow
            nodes={displayNodes}
            edges={displayEdges}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.05 }}
            minZoom={0.2}
            maxZoom={2}
            onNodeClick={(_, node) => setSelectedNode(node)}
            onPaneClick={() => setSelectedNode(null)}
            defaultEdgeOptions={{
              animated: false,
              style: {
                stroke: theme.borderLight,
                strokeWidth: 1.5,
              },
              labelStyle: {
                fill: theme.text,
                fontFamily: FONT_UI,
                fontSize: 11,
                fontWeight: 600,
              },
              labelBgStyle: {
                fill: theme.panel,
                stroke: theme.border,
                strokeWidth: 1,
              },
              labelBgPadding: [10, 5],
              labelBgBorderRadius: 6,
            }}
          >
            <Background color={theme.border} gap={24} />

            <Controls
              style={{
                background: theme.panel,
                border: `1px solid ${theme.border}`,
                borderRadius: 8,
                overflow: "hidden",
                left: 16,
                bottom: 16,
              }}
            />

            <MiniMap
              nodeColor={(node) => {
                if (node.data?.risk !== undefined) {
                  return riskTone(node.data.risk);
                }

                return theme.brand;
              }}
              maskColor="rgba(13,18,29,0.75)"
              style={{
                background: theme.panel,
                border: `1px solid ${theme.border}`,
                borderRadius: 8,
                right: 16,
                bottom: 16,
              }}
            />
          </ReactFlow>

          {/* EMPTY STATE */}
          {displayNodes.length === 0 && (
            <div
              style={{
                position: "absolute",
                inset: 0,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                zIndex: 10,
                pointerEvents: "none",
              }}
            >
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: theme.textDim,
                }}
              >
                No entities match the current filters
              </div>
              <div
                style={{
                  fontSize: 12,
                  color: theme.textFaint,
                  marginTop: 6,
                }}
              >
                Try adjusting your search or risk filter
              </div>
            </div>
          )}

          {/* RISK LEGEND */}
          <div
            style={{
              position: "absolute",
              top: 16,
              left: 16,
              zIndex: 10,
              display: "flex",
              gap: 12,
              alignItems: "center",
              background: theme.panel,
              border: `1px solid ${theme.border}`,
              borderRadius: 8,
              padding: "8px 12px",
              pointerEvents: "none",
            }}
          >
            <span
              style={{
                fontSize: 10,
                color: theme.textDim,
                fontWeight: 700,
              }}
            >
              RISK
            </span>

            <span style={{ color: theme.low, fontSize: 10 }}>● Low</span>

            <span style={{ color: theme.med, fontSize: 10 }}>● Medium</span>

            <span style={{ color: theme.high, fontSize: 10 }}>● High</span>
          </div>

          {/* STATUS */}
          <div
            style={{
              position: "absolute",
              left: 70,
              bottom: 16,
              zIndex: 10,
              background: theme.panel,
              border: `1px solid ${theme.border}`,
              borderRadius: 8,
              padding: "9px 12px",
              fontSize: 11,
              color: theme.textDim,
              pointerEvents: "none",
            }}
          >
            {filteredNodes.length} entities · {filteredEdges.length}{" "}
            relationships
          </div>
        </div>

        {/* DETAILS */}
        {selectedNode && (
          <aside
            style={{
              width: 300,
              minWidth: 300,
              background: theme.panel,
              borderLeft: `1px solid ${theme.border}`,
              padding: 22,
              boxSizing: "border-box",
              overflowY: "auto",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 20,
              }}
            >
              <div
                style={{
                  color: theme.textDim,
                  fontSize: 11,
                  fontWeight: 700,
                }}
              >
                ENTITY DETAILS
              </div>

              <button
                onClick={() => setSelectedNode(null)}
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 6,
                  border: `1px solid ${theme.border}`,
                  background: theme.surface,
                  color: theme.textDim,
                  cursor: "pointer",
                  fontSize: 16,
                }}
              >
                ×
              </button>
            </div>

            <div
              style={{
                fontSize: 20,
                fontWeight: 700,
                marginBottom: 12,
              }}
            >
              {selectedNode.data.type}
            </div>

            <div
              style={{
                background: theme.surface,
                border: `1px solid ${theme.border}`,
                borderRadius: 8,
                padding: 14,
                fontFamily: FONT_MONO,
                fontSize: 13,
                wordBreak: "break-word",
              }}
            >
              {selectedNode.data.value}
            </div>

            {selectedNode.data.risk !== undefined && (
              <div
                style={{
                  marginTop: 24,
                  paddingTop: 18,
                  borderTop: `1px solid ${theme.border}`,
                }}
              >
                <div
                  style={{
                    color: theme.textDim,
                    fontSize: 10,
                    fontWeight: 700,
                  }}
                >
                  RISK SCORE
                </div>

                <div
                  style={{
                    fontSize: 34,
                    fontWeight: 700,
                    color: riskTone(selectedNode.data.risk),
                    marginTop: 5,
                  }}
                >
                  {selectedNode.data.risk}
                </div>

                <div
                  style={{
                    color: riskTone(selectedNode.data.risk),
                    fontSize: 11,
                    fontWeight: 700,
                  }}
                >
                  {selectedNode.data.risk <= 30
                    ? "LOW RISK"
                    : selectedNode.data.risk <= 70
                      ? "MEDIUM RISK"
                      : "HIGH RISK"}
                </div>
              </div>
            )}

            {/* CONNECTION COUNT */}
            <div
              style={{
                marginTop: 24,
                paddingTop: 18,
                borderTop: `1px solid ${theme.border}`,
              }}
            >
              <div
                style={{
                  color: theme.textDim,
                  fontSize: 10,
                  fontWeight: 700,
                  marginBottom: 8,
                }}
              >
                DIRECT CONNECTIONS
              </div>

              <div
                style={{
                  fontSize: 24,
                  fontWeight: 700,
                }}
              >
                {connectedNodeIds.size - 1}
              </div>

              <div
                style={{
                  color: theme.textDim,
                  fontSize: 11,
                  marginTop: 3,
                }}
              >
                connected entities
              </div>
            </div>
          </aside>
        )}
      </div>

      {/* DARK REACT FLOW OVERRIDES */}
      <style>
        {`
          .react-flow__controls {
            box-shadow: 0 6px 18px rgba(0,0,0,0.25);
          }

          .react-flow__controls-button {
            background: ${theme.panel} !important;
            border-bottom: 1px solid ${theme.border} !important;
            fill: ${theme.textDim} !important;
          }

          .react-flow__controls-button:hover {
            background: ${theme.surfaceHover} !important;
            fill: ${theme.text} !important;
          }

          .react-flow__minimap {
            box-shadow: 0 6px 18px rgba(0,0,0,0.25);
            overflow: hidden;
          }

          .react-flow__attribution {
            background: transparent !important;
            color: ${theme.textFaint} !important;
          }

          .react-flow__attribution a {
            color: ${theme.textFaint} !important;
          }

          .react-flow__edge-text {
            fill: ${theme.text} !important;
            font-family: ${FONT_UI};
            font-size: 11px;
          }

          .react-flow__edge-textbg {
            fill: ${theme.panel} !important;
            stroke: ${theme.border} !important;
            stroke-width: 1;
          }
        `}
      </style>
    </div>
  );
}

export default FraudNetwork;
