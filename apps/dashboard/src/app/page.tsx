import { KnowledgeGraph } from "@/components/graph/KnowledgeGraph";
import { DashboardOverlay } from "@/components/dashboard/DashboardOverlay";

export default function Home() {
  return (
    <div className="flex h-full w-full relative">
      <DashboardOverlay />
      <KnowledgeGraph />
    </div>
  );
}
