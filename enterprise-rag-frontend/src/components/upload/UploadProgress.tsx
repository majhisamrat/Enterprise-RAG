interface UploadProgressProps {
  progress: number;
  filename: string;
}

export function UploadProgress({ progress, filename }: UploadProgressProps) {
  return (
    <div style={{ width: '100%', maxWidth: '500px', margin: '20px auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px', fontWeight: 600 }}>
        <span>Processing {filename}...</span>
        <span>{progress}%</span>
      </div>
      <div className="progress">
        <span style={{ width: `${progress}%` }}></span>
      </div>
    </div>
  );
}
