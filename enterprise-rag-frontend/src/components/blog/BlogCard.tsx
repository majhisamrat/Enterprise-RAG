interface BlogCardProps {
  category: string;
  title: string;
  summary: string;
  readTime: string;
}

export function BlogCard({ category, title, summary, readTime }: BlogCardProps) {
  return (
    <div className="blog-card" style={{ background: 'white', border: '1px solid var(--line)', borderRadius: '12px', padding: '24px' }}>
      <span className="blog-tag">{category}</span>
      <h3 style={{ fontSize: '18px', margin: '10px 0', letterSpacing: '-0.03em' }}>{title}</h3>
      <p style={{ fontSize: '13px', color: 'var(--muted)', lineHeight: '1.65' }}>{summary}</p>
      <small style={{ display: 'block', color: '#81908b', marginTop: '14px', fontSize: '11px', fontWeight: 600 }}>
        {readTime}
      </small>
    </div>
  );
}
