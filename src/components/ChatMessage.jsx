export default function ChatMessage({ role, content }) {
  const isUser = role === 'user';

  return (
    <div
      className={`max-w-3xl w-full py-4 px-9 rounded-lg ${
        isUser
          ? 'bg-accent text-white self-end ml-auto'
          : 'bg-diff text-white self-start mr-auto'
      }`}
    >
      {content}
    </div>
  );
}