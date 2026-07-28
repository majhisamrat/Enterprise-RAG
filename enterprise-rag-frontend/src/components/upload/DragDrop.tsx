import { ReactNode } from 'react';

export function DragDrop({ children }: { children: ReactNode }) {
  return <div className="drag-drop-container">{children}</div>;
}
