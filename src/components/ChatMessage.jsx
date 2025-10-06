export default function ChatMessage({ role, content }) {
  const isUser = role === 'user';

  return (
    <div
      className={`py-4 px-9 rounded-lg max-w-[80%] whitespace-pre-wrap break-words ${
        isUser
          ? 'bg-accent white-text self-end ml-auto'
          : 'bg-diff white-text self-start mr-auto'
      }`}
    >
      {content}
    </div>
  );
}