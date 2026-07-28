import ReactMarkdown from 'react-markdown';

export function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div className="markdown-body" style={{ fontSize: '14px', lineHeight: '1.75' }}>
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}
