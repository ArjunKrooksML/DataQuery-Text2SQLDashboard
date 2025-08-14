'use client'

import { useDashboardStore } from '@/lib/store';
import Overview from '@/components/dashboard/overview';
import SqlQueryPanel from '@/components/dashboard/sql-query-panel';
import LlmQueryPanel from '@/components/dashboard/llm-query-panel';
import ChartsPanel from '@/components/dashboard/charts-panel';

import ConnectionsPanel from '@/components/dashboard/connections-panel';

export default function DashboardPage() {
  const activeView = useDashboardStore((state) => state.activeView);

  const renderView = () => {
    switch (activeView) {
      case 'overview':
        return <Overview />;
      case 'sql':
        return <SqlQueryPanel />;
      case 'llm':
        return <LlmQueryPanel />;
      case 'charts':
        return <ChartsPanel />;
      case 'logs':
        return <LogsPanel />;
      case 'connections':
        return <ConnectionsPanel />;
      default:
        return <Overview />;
    }
  };

  return (
    <div className="w-full h-full">
      {renderView()}
    </div>
  );
}
