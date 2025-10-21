import React, { useState } from 'react';
import { ArrowUpRight, Edit, Trash2, Save, X } from 'lucide-react';
import { StockItem } from './data';
import { API_URL, fetchWithAuth } from '@/utils/auth_fn';

interface StockTableProps {
  stockData: StockItem[];
  onUpdate?: () => void;
}

const StockTable: React.FC<StockTableProps> = ({ stockData, onUpdate }) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValues, setEditValues] = useState<Partial<StockItem>>({});
  const [isLoading, setIsLoading] = useState<string | null>(null);

  // Utility function to safely convert to number
  const safeToNumber = (value: any): number => {
    if (value === null || value === undefined || value === '') return 0;
    const num = parseFloat(String(value));
    return isNaN(num) ? 0 : num;
  };

  // Utility function to format currency
  const formatCurrency = (value: any): string => {
    return `₹${safeToNumber(value).toFixed(2)}`;
  };

  const handleEdit = (item: StockItem) => {
    setEditingId(String(item.productId || item.productName));
    setEditValues({
      available: item.available,
      price: safeToNumber(item.price),
      total_required_quantity: item.total_required_quantity || 0
    });
  };

  const handleSave = async (item: StockItem) => {
    setIsLoading(String(item.productId || item.productName));
    try {
      const response = await fetchWithAuth(`${API_URL}/products/${item.productId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          available_quantity: editValues.available,
          price: editValues.price,
          total_required_quantity: editValues.total_required_quantity
        })
      });

      if (response.ok) {
        setEditingId(null);
        setEditValues({});
        if (onUpdate) onUpdate();
      } else {
        throw new Error('Failed to update product');
      }
    } catch (error) {
      console.error('Error updating product:', error);
      alert('Failed to update product. Please try again.');
    } finally {
      setIsLoading(null);
    }
  };

  const handleDelete = async (item: StockItem) => {
    if (!confirm(`Are you sure you want to delete "${item.productName}"? This action cannot be undone.`)) {
      return;
    }

    setIsLoading(String(item.productId || item.productName));
    try {
      const response = await fetchWithAuth(`${API_URL}/products/${item.productId}/`, {
        method: 'DELETE'
      });

      if (response.ok) {
        if (onUpdate) onUpdate();
      } else {
        throw new Error('Failed to delete product');
      }
    } catch (error) {
      console.error('Error deleting product:', error);
      alert('Failed to delete product. Please try again.');
    } finally {
      setIsLoading(null);
    }
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditValues({});
  };

  return (
    <div className="overflow-x-auto">
      <h2 className="text-lg font-semibold mb-4 text-blue-400">Stock Information</h2>

      {stockData.length > 0 ? (
        <div className="w-full overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-blue-400 bg-blue-900/20">
                <th className="text-left py-3 px-4 text-blue-400">Product Name</th>
                <th className="text-left py-3 px-4 text-blue-400">Category</th>
                <th className="text-left py-3 px-4 text-blue-400">Available</th>
                <th className="text-left py-3 px-4 text-blue-400">Price</th>
                <th className="text-left py-3 px-4 text-blue-400">Required</th>
                <th className="text-left py-3 px-4 text-blue-400">Demanded</th>
                <th className="text-left py-3 px-4 text-blue-400">Status</th>
                <th className="text-left py-3 px-4 text-blue-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {stockData.map((item, index) => {
                const itemId = String(item.productId || item.productName);
                const isEditing = editingId === itemId;
                const loading = isLoading === itemId;
                
                return (
                  <tr key={itemId || index} className="border-b border-blue-400/30 hover:bg-blue-900/20">
                    <td className="py-3 px-4 font-medium text-blue-200">{item.productName}</td>
                    <td className="py-3 px-4 text-blue-200">{item.category}</td>
                    
                    {/* Available Quantity - Editable */}
                    <td className="py-3 px-4 text-blue-200">
                      {isEditing ? (
                        <input
                          type="number"
                          value={editValues.available || 0}
                          onChange={(e) => setEditValues({...editValues, available: safeToNumber(e.target.value)})}
                          className="w-20 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                          min="0"
                        />
                      ) : (
                        item.available
                      )}
                    </td>
                    
                    {/* Price - Editable */}
                    <td className="py-3 px-4 text-blue-200">
                      {isEditing ? (
                        <input
                          type="number"
                          value={editValues.price || 0}
                          onChange={(e) => setEditValues({...editValues, price: safeToNumber(e.target.value)})}
                          className="w-24 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                          min="0"
                          step="0.01"
                        />
                      ) : (
                        formatCurrency(item.price)
                      )}
                    </td>
                    
                    {/* Required Quantity - Editable */}
                    <td className="py-3 px-4 text-blue-200">
                      {isEditing ? (
                        <input
                          type="number"
                          value={editValues.total_required_quantity || 0}
                          onChange={(e) => setEditValues({...editValues, total_required_quantity: safeToNumber(e.target.value)})}
                          className="w-20 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
                          min="0"
                        />
                      ) : (
                        item.total_required_quantity || 0
                      )}
                    </td>
                    
                    <td className="py-3 px-4 flex items-center gap-2 text-blue-200">
                      {item.demanded}
                      {item.demanded > item.available && (
                        <ArrowUpRight className="text-red-400 h-4 w-4" />
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded text-sm ${
                          item.available > item.demanded 
                            ? "bg-blue-900 text-blue-300" 
                            : "bg-red-900 text-red-300"
                        }`}
                      >
                        {item.available > item.demanded ? "Sufficient" : "High Demand"}
                      </span>
                    </td>
                    
                    {/* Actions Column */}
                    <td className="py-3 px-4">
                      {isEditing ? (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleSave(item)}
                            disabled={loading}
                            className="p-1 text-green-400 hover:text-green-300 disabled:opacity-50"
                            title="Save changes"
                          >
                            {loading ? (
                              <div className="animate-spin h-4 w-4 border-2 border-green-400 border-t-transparent rounded-full"></div>
                            ) : (
                              <Save className="h-4 w-4" />
                            )}
                          </button>
                          <button
                            onClick={handleCancel}
                            disabled={loading}
                            className="p-1 text-gray-400 hover:text-gray-300 disabled:opacity-50"
                            title="Cancel editing"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleEdit(item)}
                            disabled={loading}
                            className="p-1 text-blue-400 hover:text-blue-300 disabled:opacity-50"
                            title="Edit product"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(item)}
                            disabled={loading}
                            className="p-1 text-red-400 hover:text-red-300 disabled:opacity-50"
                            title="Delete product"
                          >
                            {loading ? (
                              <div className="animate-spin h-4 w-4 border-2 border-red-400 border-t-transparent rounded-full"></div>
                            ) : (
                              <Trash2 className="h-4 w-4" />
                            )}
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-gray-400">No stock data available</p>
      )}
    </div>
  );
};

export default StockTable;