export default function ChatMessage({ role, content }) {
  const isUser = role === 'user';

  return (
    <div
      className={`py-4 px-9 rounded-lg max-w-[80%] whitespace-pre-wrap break-words ${
        isUser
          ? 'bg-accent text-white self-end ml-auto'
          : 'bg-diff text-white self-start mr-auto'
      }`}
    >
      {content}
    </div>
  );
}