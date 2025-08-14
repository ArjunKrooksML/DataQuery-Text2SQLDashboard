'use client';

import { 
  SidebarHeader, 
  SidebarContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton
} from '@/components/ui/sidebar';
import { useDashboardStore, type View } from '@/lib/store';
import { BarChart2, BrainCircuit, Database, FileText, Home, Settings } from 'lucide-react';

const navItems: { view: View; label: string; icon: React.ElementType }[] = [
  { view: 'overview', label: 'Overview', icon: Home },
  { view: 'llm', label: 'LLM Prompt', icon: BrainCircuit },
  { view: 'sql', label: 'SQL Query', icon: Database },
  { view: 'charts', label: 'Analytics', icon: BarChart2 },
  { view: 'connections', label: 'Connections', icon: Settings },
];

export default function SidebarNav() {
  const { activeView, setActiveView } = useDashboardStore();

  const BrandIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-8 w-8 text-primary">
      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
    </svg>
  );

  return (
    <>
      <SidebarHeader className="p-4">
        <div className="flex items-center gap-2">
            <BrandIcon />
            <h1 className="text-xl font-bold">DataWise</h1>
        </div>
      </SidebarHeader>
      <SidebarContent className="p-2">
        <SidebarMenu>
          {navItems.map((item) => (
            <SidebarMenuItem key={item.view}>
              <SidebarMenuButton
                onClick={() => setActiveView(item.view)}
                isActive={activeView === item.view}
                tooltip={item.label}
              >
                <item.icon />
                <span>{item.label}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>
    </>
  );
}
