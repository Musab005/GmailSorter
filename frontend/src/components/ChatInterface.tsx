import { useState, useRef, useEffect, type FormEvent } from 'react';
import Message from './Message';
import LoadingIndicator from './LoadingIndicator';
import TypingMessage from './TypingMessage';
import { motion } from 'framer-motion';

interface IMessage {
  sender: 'user' | 'assistant';
  text: string;
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<IMessage[]>([
    { sender: 'assistant', text: "Hello! I’m Zephyr — ask me anything about your emails." }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: IMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input }),
      });

      if (!response.ok) throw new Error('Network response failed');
      const data = await response.json();

      setMessages(prev => [...prev, { sender: 'assistant', text: data.answer }]);
    } catch (error) {
      console.error("API call failed:", error);
      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: "Sorry, I'm having trouble connecting. Please try again."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="zephyr-bg" />
      <div
          className="w-full max-w-3xl h-[90vh] bg-gray-900/40 backdrop-blur-xl rounded-3xl shadow-2xl flex flex-col border border-gray-700/40">
        {/* Header */}
        <div className="p-4 border-b border-gray-700/40 text-center">
          <h1 className="zephyr-title">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-7 h-7 text-cyan-400 animate-pulse" fill="none"
                 viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M3 12a9 9 0 0118 0v0a9 9 0 01-18 0v0zm9-9v18"/>
            </svg>
            Zephyr
          </h1>
        </div>

        {/* Messages */}
        <div className="flex-1 p-6 space-y-6 overflow-y-auto chat-scroll">

          {messages.map((msg, index) =>
              msg.sender === 'assistant' ? (
                  <TypingMessage key={index} text={msg.text}/>
              ) : (
                  <Message key={index} sender={msg.sender} text={msg.text}/>
              )
          )}
          {isLoading && <div className="flex justify-start"><LoadingIndicator/></div>}
          <div ref={messagesEndRef}/>
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-700/40">
          <form onSubmit={handleSubmit} className="flex items-center space-x-4">
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about your emails..."
                className="flex-1 bg-gray-800/70 text-gray-200 placeholder-gray-400 rounded-full px-5 py-3 outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-60 transition-shadow duration-300"
                disabled={isLoading}
            />
            <motion.button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400 text-white rounded-full p-3 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                whileHover={{scale: isLoading ? 1 : 1.1}}
                whileTap={{scale: isLoading ? 1 : 0.95}}
            >
              <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 transform -rotate-90"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
            </motion.button>
          </form>
        </div>

      </div>
    </>
  );
};

export default ChatInterface;
