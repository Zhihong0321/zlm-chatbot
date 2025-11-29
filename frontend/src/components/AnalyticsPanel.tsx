import { useState } from 'react';
import { useSessionAnalytics, useActivityTimeline } from '../hooks/useApi';

interface AnalyticsPanelProps {
  className?: string;
}

export default function AnalyticsPanel({ className = '' }: AnalyticsPanelProps) {
  const [timeframe, setTimeframe] = useState(7);
  const { data: analytics, isLoading: analyticsLoading } = useSessionAnalytics();
  const { data: timeline, isLoading: timelineLoading } = useActivityTimeline(timeframe);

  if (analyticsLoading || timelineLoading) {
    return (
      <div className={`p-6 bg-white rounded-lg shadow-sm ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!analytics || !timeline) {
    return (
      <div className={`p-6 bg-white rounded-lg shadow-sm ${className}`}>
        <p className="text-gray-500">Analytics data not available</p>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Sessions</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.total_sessions}</p>
            </div>
            <div className="text-3xl">💬</div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Messages</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.total_messages}</p>
            </div>
            <div className="text-3xl">📨</div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Messages/Session</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.avg_messages_per_session}</p>
            </div>
            <div className="text-3xl">📊</div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Recent (7 days)</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.recent_sessions_7_days}</p>
            </div>
            <div className="text-3xl">🔥</div>
          </div>
        </div>
      </div>

      {/* Activity Timeline */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Activity Timeline</h3>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(Number(e.target.value))}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
          </select>
        </div>
        
        <div className="space-y-2">
          {timeline.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No activity in the selected timeframe</p>
          ) : (
            timeline.slice(-7).reverse().map((item: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-gray-700">
                    {new Date(item.date).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric' 
                    })}
                  </span>
                </div>
                <div className="flex items-center space-x-4 text-sm">
                  <span className="text-gray-600">
                    {item.sessions_created} session{item.sessions_created !== 1 ? 's' : ''}
                  </span>
                  <span className="text-gray-600">
                    {item.messages_sent} message{item.messages_sent !== 1 ? 's' : ''}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Agent Usage Stats */}
      {analytics.sessions_by_agent && analytics.sessions_by_agent.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sessions by Agent</h3>
          <div className="space-y-2">
            {analytics.sessions_by_agent.map((agent: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <span className="text-sm text-gray-700">Agent {agent.agent_id}</span>
                <span className="text-sm font-medium text-gray-900">{agent.count} sessions</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}