import { useState, useRef, useCallback } from "react";

export function useTooltip(delay = 400) {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const timerRef = useRef(null);

  const handleMouseEnter = useCallback((e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const scrollY = window.scrollY;

    // Default: appear to the right of the element
    let x = rect.right + 12;
    let y = rect.top + scrollY;

    // Flip to left if tooltip would overflow viewport
    if (x + 320 > window.innerWidth) {
      x = rect.left - 332;
    }

    setPosition({ x, y });
    timerRef.current = setTimeout(() => setVisible(true), delay);
  }, [delay]);

  const handleMouseLeave = useCallback(() => {
    clearTimeout(timerRef.current);
    setVisible(false);
  }, []);

  return { visible, position, handleMouseEnter, handleMouseLeave };
}