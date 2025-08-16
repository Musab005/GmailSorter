import { motion } from 'framer-motion';

interface MessageProps {
  sender: 'user' | 'assistant';
  text: string;
}

const Message = ({ sender, text }: MessageProps) => {
  const isUser = sender === 'user';
  return (
    <motion.div
      className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
    >
      <div className={`max-w-xl px-4 py-3 rounded-2xl ${ isUser ? 'bg-blue-600 text-white rounded-br-none' : 'bg-gray-700 text-gray-200 rounded-bl-none' }`}>
        <p className="whitespace-pre-wrap">{text}</p>
      </div>
    </motion.div>
  );
};

export default Message;