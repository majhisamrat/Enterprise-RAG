import { useState } from 'react';

export function useEmbeddings() {
  const [model] = useState('BAAI/bge-small-en-v1.5');
  const [dimension] = useState(384);
  const [status] = useState('ready');

  return { model, dimension, status };
}
