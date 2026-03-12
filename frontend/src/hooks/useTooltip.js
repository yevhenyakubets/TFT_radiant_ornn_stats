import { useState, useRef, useCallback } from "react";

export function useTooltip(delay = 400) {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const timerRef = useRef(null);

  const handleMouseEnter = useCallback((e) => {
    const x = e.clientX;
    const y = e.clientY;

    const tooltipWidth = 320;
    const tooltipHeight = 350;

    const finalX = x + tooltipWidth + 20 > window.innerWidth
      ? x - tooltipWidth - 12
      : x + 12;

    const finalY = y + tooltipHeight > window.innerHeight
      ? window.innerHeight - tooltipHeight - 12
      : y;

    setPosition({ x: finalX, y: finalY });
    timerRef.current = setTimeout(() => setVisible(true), delay);
  }, [delay]);

  const handleMouseLeave = useCallback(() => {
    clearTimeout(timerRef.current);
    setVisible(false);
  }, []);

  return { visible, position, handleMouseEnter, handleMouseLeave };
}