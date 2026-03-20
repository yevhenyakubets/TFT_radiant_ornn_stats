import { useState, useRef, useCallback, useEffect } from "react";

export function useTooltip(delay = 400) {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const timerRef = useRef(null);
  const elementRef = useRef(null);

  useEffect(() => {
    const handleGlobalMove = (e) => {
      if (!visible) return;
      if (!elementRef.current) return;
      const rect = elementRef.current.getBoundingClientRect();
      const inside =
        e.clientX >= rect.left &&
        e.clientX <= rect.right &&
        e.clientY >= rect.top &&
        e.clientY <= rect.bottom;
      if (!inside) {
        clearTimeout(timerRef.current);
        setVisible(false);
      }
    };

    document.addEventListener("mousemove", handleGlobalMove);
    return () => document.removeEventListener("mousemove", handleGlobalMove);
  }, [visible]);

  const handleMouseEnter = useCallback((e) => {
    elementRef.current = e.currentTarget;
    const x = e.clientX;
    const y = e.clientY;
    const tooltipWidth = 320;
    const tooltipHeight = 350;

    const finalX = x + tooltipWidth + 20 > window.innerWidth
      ? Math.max(8, x - tooltipWidth - 12)
      : x + 12;

    const finalY = y + tooltipHeight > window.innerHeight
      ? window.innerHeight - tooltipHeight - 12
      : y;

    setPosition({ x: finalX, y: finalY });
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setVisible(true), delay);
  }, [delay]);

  const handleMouseMove = useCallback((e) => {
    elementRef.current = e.currentTarget;
    const x = e.clientX;
    const y = e.clientY;
    const tooltipWidth = 320;
    const tooltipHeight = 350;

    const finalX = x + tooltipWidth + 20 > window.innerWidth
      ? Math.max(8, x - tooltipWidth - 12)
      : x + 12;

    const finalY = y + tooltipHeight > window.innerHeight
      ? window.innerHeight - tooltipHeight - 12
      : y;

    setPosition({ x: finalX, y: finalY });
  }, []);

  const handleMouseLeave = useCallback((e) => {
    if (e.relatedTarget && e.currentTarget.contains(e.relatedTarget)) return;
    clearTimeout(timerRef.current);
    setVisible(false);
  }, []);

  return { visible, position, handleMouseEnter, handleMouseMove, handleMouseLeave };
}