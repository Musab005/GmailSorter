
interface MessageProps {
  sender: 'user' | 'assistant';
  text: string;
}

const Message = ({ sender, text }: MessageProps) => {
  const isUser = sender === 'user';
  return (
      <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}>

        <div
            className={`max-w-xl px-4 py-3 rounded-2xl shadow-md ${
                isUser
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-none shadow-blue-500/30'
                    : 'bg-gray-700/60 text-gray-200 backdrop-blur-md rounded-bl-none border border-gray-600/40'
            }`}>
          <p className="whitespace-pre-wrap">{text}</p>
        </div>
    </div>
  );
};

export default Message;