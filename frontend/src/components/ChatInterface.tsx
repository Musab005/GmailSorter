import { useState, useRef, useEffect, type FormEvent } from 'react';
import Message from './Message';
import LoadingIndicator from './LoadingIndicator';
import { motion } from 'framer-motion';

interface IMessage { sender: 'user' | 'assistant'; text: string; }

const ChatInterface = () => {
  const [messages, setMessages] = useState<IMessage[]>([
    { sender: 'assistant', text: "Hello! Ask me anything about your emails." }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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
      setMessages(prev => [...prev, { sender: 'assistant', text: "Sorry, I'm having trouble connecting. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-3xl h-[90vh] bg-gray-800/50 backdrop-blur-lg rounded-2xl shadow-2xl flex flex-col border border-gray-700">
      <div className="p-4 border-b border-gray-700 text-center"><h1 className="text-xl font-bold text-gray-200">Zephyr</h1></div>
      <div className="flex-1 p-6 overflow-y-auto space-y-6">
        {messages.map((msg, index) => <Message key={index} sender={msg.sender} text={msg.text} />)}
        {isLoading && <div className="flex justify-start"><LoadingIndicator /></div>}
        <div ref={messagesEndRef} />
      </div>
      <div className="p-4 border-t border-gray-700">
        <form onSubmit={handleSubmit} className="flex items-center space-x-4">
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask about your emails..." className="flex-1 bg-gray-700 text-gray-200 rounded-full px-5 py-3 outline-none focus:ring-2 focus:ring-blue-500 transition-shadow duration-300" disabled={isLoading}/>
          <motion.button type="submit" disabled={isLoading} className="bg-blue-600 text-white rounded-full p-3 disabled:bg-gray-600 disabled:cursor-not-allowed" whileHover={{ scale: isLoading ? 1 : 1.1 }} whileTap={{ scale: isLoading ? 1 : 0.95 }}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 transform -rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
          </motion.button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;