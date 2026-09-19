import Image from "next/image";
import { getCategory, PATTERN_IMAGES } from "@/lib/categories";
import type { Article } from "@/lib/api";

function safeImageUrl(url: string | undefined, category: string): string {
  if (!url) return PATTERN_IMAGES[category] || PATTERN_IMAGES.general;
  try {
    const parsed = new URL(url);
    if (!["http:", "https:"].includes(parsed.protocol)) return PATTERN_IMAGES[category] || PATTERN_IMAGES.general;
    return parsed.toString();
  } catch {
    return PATTERN_IMAGES[category] || PATTERN_IMAGES.general;
  }
}

export function ArticleImage({
  article,
  sizes,
  priority = false,
  className = "aspect-[16/9]",
  showBadge = true,
}: {
  article: Article;
  sizes?: string;
  priority?: boolean;
  className?: string;
  showBadge?: boolean;
}) {
  const src = safeImageUrl(article.image_url, article.category);
  const cat = getCategory(article.category);
  return (
    <div className={`relative shrink-0 overflow-hidden bg-black/5 ${className}`}>
      <Image
        src={src}
        alt={article.title}
        fill
        priority={priority}
        sizes={sizes ?? "(max-width: 640px) 100vw, 50vw"}
        className="object-cover transition-transform duration-700 group-hover:scale-[1.04]"
      />
      {showBadge && (
        <span className="absolute left-3 top-3 z-10 rounded bg-accent-soil px-2.5 py-1 text-[10px] font-black uppercase tracking-wider text-white">{cat.label}</span>
      )}
    </div>
  );
}