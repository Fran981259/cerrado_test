export default function Loading() {
  return (
    <div className="container-custom py-8 animate-pulse">
      <div className="h-6 bg-zinc-200 rounded w-24 mb-4" />
      <div className="h-10 bg-zinc-200 rounded w-3/4 mb-3" />
      <div className="h-4 bg-zinc-200 rounded w-1/2 mb-8" />
      <div className="h-[420px] bg-zinc-200 rounded-2xl mb-8" />
      <div className="space-y-3">
        <div className="h-4 bg-zinc-200 rounded" />
        <div className="h-4 bg-zinc-200 rounded" />
        <div className="h-4 bg-zinc-200 rounded w-5/6" />
      </div>
    </div>
  );
}
