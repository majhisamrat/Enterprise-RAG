import { motion } from 'framer-motion';

export function VennDiagram() {
  const circleVariants = {
    hidden: { scale: 0, opacity: 0 },
    visible: { scale: 1, opacity: 1 },
  };

  const centerVariants = {
    hidden: { scale: 0, rotate: -180 },
    visible: { scale: 1, rotate: 0 },
  };

  return (
    <div className="relative w-full max-w-sm mx-auto aspect-square">
      <svg
        viewBox="0 0 400 400"
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Left Circle - Text Content */}
        <motion.circle
          cx="140"
          cy="200"
          r="120"
          fill="rgba(203, 243, 255, 0.6)"
          stroke="rgba(203, 243, 255, 0.8)"
          strokeWidth="2"
          style={{ mixBlendMode: 'multiply' }}
          variants={circleVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.1 }}
        />

        {/* Right Circle - Visual Content */}
        <motion.circle
          cx="260"
          cy="200"
          r="120"
          fill="rgba(254, 240, 190, 0.6)"
          stroke="rgba(254, 240, 190, 0.8)"
          strokeWidth="2"
          style={{ mixBlendMode: 'multiply' }}
          variants={circleVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.2 }}
        />

        {/* Bottom Circle - AI */}
        <motion.circle
          cx="200"
          cy="280"
          r="120"
          fill="rgba(255, 227, 241, 0.6)"
          stroke="rgba(255, 227, 241, 0.8)"
          strokeWidth="2"
          style={{ mixBlendMode: 'multiply' }}
          variants={circleVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.3 }}
        />
      </svg>

      {/* Labels */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.div
          className="absolute"
          style={{ top: '20%', left: '15%' }}
          variants={circleVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.4 }}
        >
          <div className="text-center">
            <div className="text-3xl mb-1">📄</div>
            <div className="text-sm font-semibold text-blue-700">Text</div>
            <div className="text-xs text-blue-600">Content</div>
          </div>
        </motion.div>

        <motion.div
          className="absolute"
          style={{ top: '20%', right: '15%' }}
          variants={circleVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.5 }}
        >
          <div className="text-center">
            <div className="text-3xl mb-1">📊</div>
            <div className="text-sm font-semibold text-amber-700">Visual</div>
            <div className="text-xs text-amber-600">Content</div>
          </div>
        </motion.div>

        <motion.div
          className="absolute"
          style={{ bottom: '15%' }}
          variants={circleVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.6 }}
        >
          <div className="text-center">
            <div className="text-3xl mb-1">✨</div>
            <div className="text-sm font-semibold text-pink-700">Artificial</div>
            <div className="text-xs text-pink-600">Intelligence</div>
          </div>
        </motion.div>

        {/* Center Icon */}
        <motion.div
          className="w-12 h-12 bg-brand-ink text-white rounded-full flex items-center justify-center font-bold text-xl shadow-lg"
          variants={centerVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.7, type: 'spring', stiffness: 100 }}
        >
          ◇
        </motion.div>
      </div>
    </div>
  );
}
