import { Handle, Position } from "@xyflow/react";
import { theme, FONT_UI, FONT_MONO, riskTone } from "../theme";

function FraudNode({ data }) {
  const hasRisk = data.risk !== undefined;

  return (
    <div
      style={{
        width: 190,
        background: theme.surface,
        border: `1px solid ${
          hasRisk ? riskTone(data.risk) : theme.borderLight
        }`,
        borderRadius: 12,
        padding: 14,
        fontFamily: FONT_UI,
        boxShadow: "0 8px 25px rgba(0,0,0,0.3)",
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
        style={{
          background: theme.brand,
          border: `2px solid ${theme.surface}`,
        }}
      />

      <div
        style={{
          fontSize: 11,
          color: theme.textDim,
          textTransform: "uppercase",
          marginBottom: 7,
          letterSpacing: "0.5px",
        }}
      >
        {data.type}
      </div>

      <div
        style={{
          color: theme.text,
          fontFamily: FONT_MONO,
          fontSize: 13,
          fontWeight: 600,
          wordBreak: "break-word",
        }}
      >
        {data.value}
      </div>

      {hasRisk && (
        <div
          style={{
            display: "inline-block",
            marginTop: 12,
            padding: "4px 8px",
            borderRadius: 6,
            background:
              data.risk <= 30
                ? theme.lowDim
                : data.risk <= 70
                  ? theme.medDim
                  : theme.highDim,
            color: riskTone(data.risk),
            fontSize: 11,
            fontWeight: 700,
          }}
        >
          {data.risk <= 30 ? "LOW" : data.risk <= 70 ? "MEDIUM" : "HIGH"} ·{" "}
          {data.risk}
        </div>
      )}

      <Handle
        type="source"
        position={Position.Right}
        style={{
          background: theme.brand,
          border: `2px solid ${theme.surface}`,
        }}
      />
    </div>
  );
}

export default FraudNode;
