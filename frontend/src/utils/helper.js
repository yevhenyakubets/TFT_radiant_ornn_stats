  export const getRarityColor = (cost) => {
    switch (cost) {
      case 1: return "rgb(24, 36, 49)";
      case 2: return "rgb(20, 77, 29)";
      case 3: return "rgb(28, 52, 93)";
      case 4: return "rgb(102, 20, 79)";
      case 5:
      case 7: return "rgb(134, 84, 11)";
      default: return "#ccc";
    }
  };