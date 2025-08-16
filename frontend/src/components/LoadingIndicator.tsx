import { motion } from 'framer-motion';

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
    <motion.span
      className="w-3 h-3 bg-blue-400 rounded-full"
      variants={dotVariants}
      style={{ transitionDelay: "0s" }}
    />
    <motion.span
      className="w-3 h-3 bg-blue-400 rounded-full"
      variants={dotVariants}
      style={{ transitionDelay: "0.2s" }}
    />
    <motion.span
      className="w-3 h-3 bg-blue-400 rounded-full"
      variants={dotVariants}
      style={{ transitionDelay: "0.4s" }}
    />
  </motion.div>
);

export default LoadingIndicator;
