import type { Metadata } from "next";
export const metadata: Metadata = { title: "Contato" };

export default function ContatoPage() {
  return (
    <div className="container-custom py-10 max-w-3xl">
      <h1 className="text-3xl font-black text-zinc-900">Contato</h1>
      <p className="mt-3 text-zinc-600">Fale com a redação. Respondemos em até 24h úteis.</p>

      <div className="mt-8 grid gap-6 md:grid-cols-[1.2fr_0.8fr]">
        <form className="rounded-2xl bg-white p-6 shadow-sm border border-zinc-100 space-y-4">
          <div>
            <label className="text-sm font-bold text-zinc-700">Nome</label>
            <input className="mt-1 w-full rounded-xl border border-zinc-200 px-4 py-3 text-sm outline-none focus:border-[#e63946] focus:ring-2 focus:ring-[#e63946]/20" placeholder="Seu nome" />
          </div>
          <div>
            <label className="text-sm font-bold text-zinc-700">E-mail</label>
            <input type="email" className="mt-1 w-full rounded-xl border border-zinc-200 px-4 py-3 text-sm outline-none focus:border-[#e63946] focus:ring-2 focus:ring-[#e63946]/20" placeholder="seu@email.com" />
          </div>
          <div>
            <label className="text-sm font-bold text-zinc-700">Mensagem</label>
            <textarea rows={5} className="mt-1 w-full rounded-xl border border-zinc-200 px-4 py-3 text-sm outline-none focus:border-[#e63946] focus:ring-2 focus:ring-[#e63946]/20" placeholder="Como podemos ajudar?" />
          </div>
          <button type="button" className="w-full rounded-full bg-[#e63946] py-3 text-sm font-bold text-white hover:bg-[#c1121f]">Enviar mensagem</button>
          <p className="text-xs text-zinc-500">Ao enviar, você concorda com nossa <a href="/privacidade" className="text-[#e63946] font-semibold">Política de Privacidade</a>.</p>
        </form>

        <div className="space-y-4">
          <div className="rounded-2xl bg-[#1a1a2e] text-white p-6">
            <h3 className="font-bold">Redação</h3>
            <p className="mt-2 text-sm opacity-80">contato@portalcerrado.com.br<br />Campo Grande — MS</p>
            <p className="mt-4 text-xs opacity-60">Sugestões de pauta, correções e parcerias comerciais.</p>
          </div>
          <div className="rounded-2xl bg-white border border-zinc-100 p-6">
            <h3 className="font-bold text-zinc-900">Anuncie</h3>
            <p className="mt-2 text-sm text-zinc-600">Alcance leitores de MS com mídia contextual. Fale com nosso comercial.</p>
            <a href="mailto:contato@portalcerrado.com.br?subject=Anúncio" className="mt-4 inline-block rounded-full bg-zinc-900 text-white px-5 py-2.5 text-sm font-bold">Quero anunciar</a>
          </div>
        </div>
      </div>
    </div>
  );
}
