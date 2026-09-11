export const theme = {
  bg: "#0D121D",
  panel: "#131a29",
  surface: "#161f31",
  surfaceHover: "#1b2438",

  border: "#232d43",
  borderLight: "#303c58",

  text: "#E7EAF3",
  textDim: "#8992AA",
  textFaint: "#5B6480",

  brand: "#5B7FFF",
  brandDim: "rgba(91,127,255,0.13)",

  low: "#33D69F",
  lowDim: "rgba(51,214,159,0.13)",

  med: "#F5A623",
  medDim: "rgba(245,166,35,0.14)",

  high: "#FF5C72",
  highDim: "rgba(255,92,114,0.14)",
};

export const FONT_UI = "'Inter', ui-sans-serif, system-ui, sans-serif";

export const FONT_MONO =
  "'IBM Plex Mono', ui-monospace, SFMono-Regular, monospace";

export function riskTone(score) {
  if (score <= 30) return theme.low;
  if (score <= 70) return theme.med;
  return theme.high;
}
