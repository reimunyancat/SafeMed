import type { CSSProperties } from "react";

const wrapStyle: CSSProperties = {
  margin: "0 20px 12px",
  padding: "10px 12px",
  borderRadius: 10,
  border: "1px solid #ececec",
  borderLeft: "3px solid #ff7a3d",
  backgroundColor: "#fff",
  fontSize: 12,
  lineHeight: 1.5,
  color: "#777777",
};

export function Disclaimer() {
  return (
    <div style={wrapStyle} role="note" aria-label="안내사항">
      이 서비스는 의학적 진단·처방을 대체하지 않아요. 약 복용 전에는 의사·약사와 상의해 주세요.
      <br />입력하신 정보는 서버에 저장되지 않고 분석 즉시 사라져요.
    </div>
  );
}
