export default function PageHeader({ title, subtitle, children }) {
  return (
    <div className="flex items-start justify-between mb-8">
      <div>
        <h1 className="text-3xl font-display text-stone-900">{title}</h1>
        {subtitle && (
          <p className="mt-2 text-stone-500 text-sm max-w-2xl">{subtitle}</p>
        )}
      </div>
      {children && <div className="flex items-center gap-3">{children}</div>}
    </div>
  );
}
