export default function ChatMessage({ role, content }) {
  const isUser = role === 'user';

  return (
    <div
      className={`py-4 px-9 rounded-lg ${
        isUser
          ? 'w-2xl bg-accent text-white self-end ml-auto'
          : 'w-3xl bg-diff text-white self-start mr-auto'
      }`}
    >
      {content}
    </div>
  );
}