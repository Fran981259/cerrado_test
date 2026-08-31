export default function Loading() {
  return (
    <div className="container-custom py-8">
      <div className="animate-pulse">
        <div className="h-8 bg-zinc-200 rounded w-1/3 mb-6" />
        <div className="grid lg:grid-cols-[2fr_1fr] gap-6">
          <div className="h-[420px] bg-zinc-200 rounded-2xl" />
          <div className="grid gap-4">
            <div className="h-[95px] bg-zinc-200 rounded-xl" />
            <div className="h-[95px] bg-zinc-200 rounded-xl" />
            <div className="h-[95px] bg-zinc-200 rounded-xl" />
            <div className="h-[95px] bg-zinc-200 rounded-xl" />
          </div>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-[280px] bg-zinc-200 rounded-2xl" />
          ))}
        </div>
      </div>
    </div>
  );
}
