'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BrainCircuit, Database, BarChart2, FileText } from "lucide-react";
import { useDashboardStore, type View } from '@/lib/store';

const features: { icon: React.ElementType; title: string; description: string; view: View }[] = [
  {
    icon: BrainCircuit,
    title: "LLM Prompt",
    description: "Interact with an AI to get natural language answers about your data.",
    view: 'llm',
  },
  {
    icon: Database,
    title: "SQL Query",
    description: "Run SQL queries directly and view results in a table.",
    view: 'sql',
  },
  {
    icon: BarChart2,
    title: "Visualizations",
    description: "Explore your data through interactive charts and graphs.",
    view: 'charts',
  },
  {
    icon: FileText,
    title: "Query Logs",
    description: "Review your recent activity and query history.",
    view: 'logs',
  },
];

export default function Overview() {
  const setActiveView = useDashboardStore((state) => state.setActiveView);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Welcome to DataWise</h1>
        <p className="text-muted-foreground mt-2">
          Your intelligent data dashboard. Select a tool below or from the sidebar to get started.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {features.map((feature) => (
          <Card 
            key={feature.title} 
            className="cursor-pointer hover:bg-muted/50 transition-colors"
            onClick={() => setActiveView(feature.view)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{feature.title}</CardTitle>
              <feature.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">{feature.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
