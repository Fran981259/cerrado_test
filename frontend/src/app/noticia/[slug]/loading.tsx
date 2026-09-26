export default function Loading() {
  return (
    <div className="container-custom py-8 animate-pulse">
      <div className="h-[560px] rounded-[2rem] bg-black/10" />
      <div className="-mt-10 grid gap-8 lg:grid-cols-[minmax(0,1fr)_360px]">
        <article className="rounded-[2rem] bg-surface p-6">
          <div className="flex items-center gap-4 border-b border-black/5 pb-6"><div className="h-14 w-14 rounded-full bg-black/10" /><div className="h-5 w-40 rounded bg-black/10" /></div>
          <div className="my-8 h-72 rounded-2xl bg-black/10" />
          <div className="space-y-4">{["w-full", "w-11/12", "w-4/5", "w-full", "w-9/12", "w-10/12", "w-3/4"].map((width) => <div key={width} className={`h-4 rounded bg-black/10 ${width}`} />)}</div>
        </article>
        <aside className="hidden h-96 rounded-2xl bg-black/10 lg:block" />
      </div>
    </div>
  );
}
