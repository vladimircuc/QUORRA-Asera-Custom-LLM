import ReactMarkdown from "react-markdown";

export default function ChatMessage({ role, content, time, showTimestamps, compactMode}) {
  const isUser = role === 'user';
  // console.log("ChatMessage content:", content);
  
  const formatTime = (dateString) => {
  if (!dateString) return "N/A";
  const date = new Date(dateString);

  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
  };


  return (
    <div
      className={`rounded-lg whitespace-pre-wrap break-words
        
        ${ compactMode ? 'py-2 px-4 max-w-[90%]' : 'py-3 px-6 max-w-[80%]'}
        ${
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

        {showTimestamps && (
          <div className="text-xs opacity-70 mt-1">{formatTime(time)}</div>
        )}
      </div>
      
    </div>
  );
}