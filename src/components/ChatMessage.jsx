export default function ChatMessage({ role, content }) {
  const isUser = role === 'user';
  return (
    <div
      className={`max-w-3xl px-4 py-3 rounded-lg ${
        isUser
          ? 'bg-blue-600 text-white self-end ml-auto'
          : 'bg-gray-700 text-gray-100 self-start mr-auto'
      }`}
    >
      {content}
    </div>
  );
}