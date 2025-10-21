import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import StockTable from './StockTable';
import StockCharts from './StockCharts';
import { StockItem } from './data';

interface StockOverviewProps {
  activeView: string;
  stockData: StockItem[];
  onUpdate?: () => void;
}

const StockOverview: React.FC<StockOverviewProps> = ({ activeView, stockData, onUpdate }) => {
  return (
    <Card className="bg-black border border-blue-400">
      <CardHeader>
        <CardTitle className="text-blue-400">Stock Overview</CardTitle>
        <CardDescription className="text-blue-300">Comprehensive stock details</CardDescription>
      </CardHeader>
      <CardContent className="text-blue-200">
        {activeView === 'table' ? (
          <StockTable stockData={stockData} onUpdate={onUpdate} />
        ) : (
          <StockCharts stockData={stockData} />
        )}
      </CardContent>
    </Card>
  );
};

export default StockOverview;