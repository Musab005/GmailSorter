import { motion } from "framer-motion";

const dotVariants = {
  initial: { y: 0 },
  animate: {
    y: [0, -10, 0],
    transition: {
      duration: 1.2,
      ease: "easeInOut" as const,
      repeat: Infinity,
    },
  },
};

const LoadingIndicator = () => (
  <motion.div
    className="flex items-center space-x-2"
    initial="initial"
    animate="animate"
  >
    {[0, 1, 2].map((i) => (
      <motion.span
        key={i}
        className="w-3 h-3 rounded-full"
        variants={dotVariants}
        style={{
          transitionDelay: `${i * 0.2}s`,
          background: `conic-gradient(from 0deg, hsl(${i * 120}, 80%, 70%), hsl(${(i * 120 + 60) % 360}, 80%, 70%))`,
          animation: "hueShift 4s linear infinite",
        }}
      />
    ))}
    <style>
      {`
        @keyframes hueShift {
          0%   { filter: hue-rotate(0deg); }
          100% { filter: hue-rotate(360deg); }
        }
      `}
    </style>
  </motion.div>
);

export default LoadingIndicator;
