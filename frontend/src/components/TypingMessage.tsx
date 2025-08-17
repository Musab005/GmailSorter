import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface TypingMessageProps {
  text: string;
}

const TypingMessage = ({ text }: TypingMessageProps) => {
  const [displayedText, setDisplayedText] = useState('');
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (index < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[index]);
        setIndex(index + 1);
      }, 25); // typing speed
      return () => clearTimeout(timeout);
    }
  }, [index, text]);

  return (
    <motion.div
      className="flex w-full justify-start"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
    >
      <div className="max-w-xl px-4 py-3 rounded-2xl bg-gray-800/60 text-gray-200 backdrop-blur-md rounded-bl-none border border-gray-700/40 shadow-md">
        <p className="whitespace-pre-wrap">
          {displayedText}
          {index < text.length && <span className="typing-caret" />}
        </p>
      </div>
    </motion.div>
  );
};

export default TypingMessage;
