"use client";

import { useEffect, useState } from "react";
import { CATEGORY_LIST } from "@/lib/categories";

export default function CuradoriaPage() {
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [pass, setPass] = useState("");
  const [auth, setAuth] = useState(false);

  // Fake auth persistente
  useEffect(() => {
    if (typeof window !== "undefined") {
      const isAuth = localStorage.getItem("cerrado_admin_auth") === "true";
      if (isAuth) {
        setAuth(true);
        fetchArticles();
      } else {
        setLoading(false);
      }
    }
  }, []);

  const handleAuth = (e: any) => {
    e.preventDefault();
    if (pass === "cerrado2024") {
      setAuth(true);
      if (typeof window !== "undefined") {
        localStorage.setItem("cerrado_admin_auth", "true");
      }
      setLoading(true);
      fetchArticles();
    } else {
      setError("Senha incorreta");
    }
  };

  const fetchArticles = async () => {
    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/editorial/review", {
        headers: { "X-API-Key": "cerrado123" }
      });
      if (!res.ok) throw new Error("Falha ao buscar artigos");
      const data = await res.json();
      setArticles(data.articles);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (slug: string, updateData: any) => {
    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + `/editorial/review/${slug}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": "cerrado123"
        },
        body: JSON.stringify(updateData)
      });
      if (!res.ok) throw new Error("Erro ao atualizar");
      
      // Remove from list if published or rejected
      if (updateData.status) {
        setArticles(articles.filter(a => a.slug !== slug));
      }
    } catch (err: any) {
      alert("Erro: " + err.message);
    }
  };

  if (!auth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-zinc-900">
        <form onSubmit={handleAuth} className="p-8 bg-white dark:bg-zinc-800 rounded-xl shadow-xl flex flex-col gap-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Curadoria Manual</h2>
          <input 
            type="password" 
            placeholder="Senha de Acesso"
            value={pass}
            onChange={(e) => setPass(e.target.value)}
            className="p-3 rounded border border-gray-300 dark:border-zinc-700 bg-transparent text-gray-900 dark:text-white"
          />
          {error && <p className="text-red-500">{error}</p>}
          <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded">
            Entrar
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-zinc-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-black text-gray-900 dark:text-white mb-2">Painel de Curadoria</h1>
            <p className="text-gray-600 dark:text-gray-400">Classifique ou rejeite matérias pendentes.</p>
          </div>
          <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full font-bold">
            {articles.length} Pendentes
          </div>
        </header>

        {loading ? (
          <div className="text-center py-20 text-gray-500">Carregando matérias...</div>
        ) : (
          <div className="grid gap-6">
            {articles.map((article) => (
              <div key={article.slug} className="bg-white dark:bg-zinc-800 rounded-xl shadow p-6 border border-gray-200 dark:border-zinc-700">
                <div className="mb-4">
                  <span className="inline-block px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-bold rounded-full mb-3 uppercase tracking-wider">
                    {article.status}
                  </span>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{article.title}</h3>
                  <p className="text-gray-600 dark:text-gray-300 text-sm italic border-l-4 border-gray-300 dark:border-gray-600 pl-4 mb-4">
                    {article.summary}
                  </p>
                  
                  <details className="mt-4 text-sm text-gray-500 dark:text-gray-400">
                    <summary className="cursor-pointer font-semibold text-blue-600 dark:text-blue-400">Ver Corpo Extraído (Original)</summary>
                    <div className="mt-2 p-4 bg-gray-100 dark:bg-zinc-900 rounded whitespace-pre-wrap">
                      {article.original_text?.substring(0, 800)}...
                    </div>
                  </details>
                </div>

                <div className="mt-6 flex flex-wrap gap-4 items-end bg-gray-50 dark:bg-zinc-800/50 p-4 rounded-lg">
                  <div className="flex-1 min-w-[200px]">
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Categoria</label>
                    <select 
                      defaultValue={article.category}
                      onChange={(e) => handleUpdate(article.slug, { category: e.target.value })}
                      className="w-full p-2 rounded border border-gray-300 dark:border-zinc-600 bg-white dark:bg-zinc-700 text-gray-900 dark:text-white"
                    >
                      {CATEGORY_LIST.map(c => (
                        <option key={c.slug} value={c.slug}>{c.label}</option>
                      ))}
                    </select>
                  </div>

                  <div className="w-24">
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Relevância</label>
                    <input 
                      type="number"
                      defaultValue={article.importance_score}
                      onChange={(e) => handleUpdate(article.slug, { importance_score: parseInt(e.target.value) })}
                      className="w-full p-2 rounded border border-gray-300 dark:border-zinc-600 bg-white dark:bg-zinc-700 text-gray-900 dark:text-white text-center"
                    />
                  </div>

                  <div className="w-24">
                    <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Viral</label>
                    <input 
                      type="number"
                      defaultValue={article.engagement_score}
                      onChange={(e) => handleUpdate(article.slug, { engagement_score: parseInt(e.target.value) })}
                      className="w-full p-2 rounded border border-gray-300 dark:border-zinc-600 bg-white dark:bg-zinc-700 text-gray-900 dark:text-white text-center"
                    />
                  </div>
                  
                  <div className="flex gap-2 ml-auto mt-4 sm:mt-0">
                    <button 
                      onClick={() => handleUpdate(article.slug, { status: "rejected" })}
                      className="px-6 py-2 bg-red-100 hover:bg-red-200 text-red-700 font-bold rounded transition-colors"
                    >
                      Descartar
                    </button>
                    <button 
                      onClick={() => handleUpdate(article.slug, { status: "published" })}
                      className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-bold rounded transition-colors shadow"
                    >
                      Publicar
                    </button>
                  </div>
                </div>
              </div>
            ))}

            {articles.length === 0 && (
              <div className="text-center py-12 bg-white dark:bg-zinc-800 rounded-xl">
                <p className="text-xl text-gray-500">Nenhuma matéria pendente de curadoria! 🎉</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
