import { motion } from 'framer-motion';
import { Card } from '../components/ui/Card';
import { useDocuments } from '../hooks/useDocuments';
import { useSettingsStore } from '../store/settingsStore';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, FileText, Zap, Settings2 } from 'lucide-react';

// Sample data for charts
const retrievalData = [
  { name: 'Mon', queries: 420 },
  { name: 'Tue', queries: 640 },
  { name: 'Wed', queries: 580 },
  { name: 'Thu', queries: 790 },
  { name: 'Fri', queries: 890 },
  { name: 'Sat', queries: 720 },
  { name: 'Sun', queries: 650 },
];

const documentTypeData = [
  { name: 'PDFs', value: 45 },
  { name: 'Documents', value: 30 },
  { name: 'Spreadsheets', value: 15 },
  { name: 'Images', value: 10 },
];

const COLORS = ['#19b5df', '#1293b6', '#22c5ee', '#90d5e8'];

function StatCard({
  icon: Icon,
  label,
  value,
  detail,
  trend,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  detail: string;
  trend?: number;
}) {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Card className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="p-3 bg-brand-cyan-light rounded-lg">
            <Icon className="text-brand-cyan" size={24} />
          </div>
          {trend !== undefined && (
            <span className={`text-sm font-semibold ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
            </span>
          )}
        </div>
        <p className="text-sm text-brand-muted font-semibold mb-2">{label}</p>
        <p className="text-3xl font-bold text-brand-ink mb-2">{value}</p>
        <p className="text-xs text-brand-muted">{detail}</p>
      </Card>
    </motion.div>
  );
}

export function Dashboard() {
  const { documents, loading } = useDocuments();
  const { settings } = useSettingsStore();

  const totalChunks = documents.reduce((acc, doc) => acc + (doc.chunkCount || 0), 0);

  return (
    <div className="space-y-8 pb-8">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <p className="text-xs font-bold text-brand-muted tracking-widest mb-2">OVERVIEW</p>
          <h1 className="text-4xl font-bold text-brand-ink">Knowledge at a Glance</h1>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg font-semibold text-sm">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          System Online
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={FileText}
          label="Total Documents"
          value={loading ? '—' : documents.length}
          detail="Across this workspace"
          trend={12}
        />
        <StatCard
          icon={Zap}
          label="Total Chunks"
          value={loading ? '—' : totalChunks}
          detail="Available for retrieval"
          trend={8}
        />
        <StatCard
          icon={Activity}
          label="Retrieval Latency"
          value="142 ms"
          detail="Avg. over last 100 queries"
          trend={-5}
        />
        <StatCard
          icon={Settings2}
          label="Active Provider"
          value={settings.llmProvider.toUpperCase()}
          detail={settings.embeddingModel}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Retrieval Trends */}
        <motion.div
          className="lg:col-span-2"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="p-6">
            <div className="mb-6">
              <h3 className="text-xl font-bold text-brand-ink mb-2">Query Performance</h3>
              <p className="text-sm text-brand-muted">Queries executed this week</p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={retrievalData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#dce6e1" />
                <XAxis dataKey="name" stroke="#687772" />
                <YAxis stroke="#687772" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #dce6e1',
                    borderRadius: '8px',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="queries"
                  stroke="#19b5df"
                  strokeWidth={2}
                  dot={{ fill: '#19b5df', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </motion.div>

        {/* Document Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="p-6">
            <div className="mb-6">
              <h3 className="text-xl font-bold text-brand-ink mb-2">Document Types</h3>
              <p className="text-sm text-brand-muted">Distribution</p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={documentTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {documentTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </motion.div>
      </div>

      {/* Recent Documents */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="p-6">
          <div className="mb-6">
            <h3 className="text-xl font-bold text-brand-ink">Recent Documents</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-brand-line">
                  <th className="text-left py-3 px-4 font-semibold text-brand-muted">Name</th>
                  <th className="text-left py-3 px-4 font-semibold text-brand-muted">Size</th>
                  <th className="text-left py-3 px-4 font-semibold text-brand-muted">Chunks</th>
                  <th className="text-left py-3 px-4 font-semibold text-brand-muted">Status</th>
                  <th className="text-left py-3 px-4 font-semibold text-brand-muted">Date</th>
                </tr>
              </thead>
              <tbody>
                {documents.slice(0, 5).map((doc) => (
                  <tr key={doc.id} className="border-b border-brand-line hover:bg-brand-soft transition-colors">
                    <td className="py-3 px-4 font-medium text-brand-ink">{doc.name}</td>
                    <td className="py-3 px-4 text-brand-muted">{typeof doc.size === 'number' ? (doc.size / 1024).toFixed(1) : '0'} MB</td>
                    <td className="py-3 px-4 text-brand-muted">{doc.chunkCount || 0}</td>
                    <td className="py-3 px-4">
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
                        Indexed
                      </span>
                    </td>
                    <td className="py-3 px-4 text-brand-muted">
                      {new Date(doc.uploadedAt).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
