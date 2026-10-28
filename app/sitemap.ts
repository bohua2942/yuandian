import type { MetadataRoute } from "next";
import { catalog, site } from "@/lib/data";
import { channels } from "@/lib/content";
export const dynamic = "force-static";
export default function sitemap(): MetadataRoute.Sitemap {
  return ["/", "/about/", "/archive/", ...channels.map(channel => `/${channel.id}/`), ...catalog.items.map(story => `/posts/${story.id}/`), ...catalog.batches.map(batch => `/${batch.channel}/${batch.date}/`)].map(path => ({ url: site.url + path, ...(catalog.updatedAt ? { lastModified: catalog.updatedAt } : {}) }));
}
