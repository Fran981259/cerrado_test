import type { Metadata } from "next";
import { EditorialDashboard } from "@/components/admin/EditorialDashboard";

export const metadata: Metadata = { title: "Mesa editorial", robots: { index: false, follow: false } };

/** Protected client workspace for content administration. */
export default function EditorialAdminPage() {
  return <EditorialDashboard />;
}
