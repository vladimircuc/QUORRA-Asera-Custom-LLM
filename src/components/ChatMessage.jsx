import ReactMarkdown from "react-markdown";

export default function ChatMessage({ role, content }) {
  const isUser = role === 'user';
  // console.log("ChatMessage content:", content);
  

  return (
    <div
      className={`py-3 px-6 rounded-lg max-w-[80%] whitespace-pre-wrap break-words ${
        isUser
          ? 'bg-accent white-text self-end ml-auto'
          : 'bg-diff white-text self-start mr-auto'
      }`}
    >
      <div className="prose prose-invert">
<ReactMarkdown>
  {typeof content === "string"
    ? content
    : content?.text || content?.raw_text || ""}
</ReactMarkdown>
      </div>
    </div>
  );
}