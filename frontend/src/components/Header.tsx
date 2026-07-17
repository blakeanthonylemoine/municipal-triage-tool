import type { ReactNode } from 'react';

interface HeaderProps {
  label?: string;
  children?: ReactNode;
}

export default function Header({ label, children }: HeaderProps) {
  return (
    <header className="h-14 flex-none bg-[oklch(0.27_0.06_250)] flex items-center px-6 gap-4 text-white">
      <div className="font-serif font-semibold text-lg tracking-tight">CivicTriage</div>
      {label && (
        <>
          <div className="w-px h-6 bg-white/20" />
          <span className="text-sm text-white/75">{label}</span>
        </>
      )}
      <div className="flex-1" />
      {children}
    </header>
  );
}
