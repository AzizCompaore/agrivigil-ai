import React from 'react';
import { ComposedChart, Area, Scatter, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import moment from 'moment';
import { severityColors } from '@/lib/theme';

const severityScore = { faible: 1, modérée: 2, élevée: 3, critique: 4 };
const severityLabel = { 1: 'Faible', 2: 'Modérée', 3: 'Élevée', 4: 'Critique' };
const severityColorsMap = {
  critique: '#D6473B',
  élevée: '#E8B84B',
  modérée: '#E8B84B',
  faible: '#1B7049',
};

// Tooltip personnalisé riche avec aperçu photo et détails
function CustomHealthTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;

  // On récupère le point complet depuis payload (Scatter ou Area)
  const item = payload[0];
  const dataPoint = item.payload;
  if (!dataPoint || dataPoint._virtual) return null;

  const score = dataPoint.score || (typeof item.value === 'number' ? item.value : 1);
  const severity = dataPoint.severity || (score === 4 ? 'critique' : score === 3 ? 'élevée' : score === 2 ? 'modérée' : 'faible');
  const badgeColor = severityColorsMap[severity] || '#12523A';

  return (
    <div className="bg-white/95 backdrop-blur-md p-3 rounded-2xl shadow-xl border border-[#DCE7E0] max-w-[220px] text-left animate-fadeIn">
      {dataPoint.image_url && (
        <div className="relative mb-2 overflow-hidden rounded-xl border border-[#E3EDE7]">
          <img
            src={dataPoint.image_url}
            alt="Scan"
            className="w-full h-24 object-cover"
          />
          <div className="absolute top-1.5 right-1.5">
            <span
              className="text-[9px] font-extrabold px-2 py-0.5 rounded-full text-white shadow-sm uppercase tracking-wide"
              style={{ backgroundColor: badgeColor }}
            >
              {severityLabel[score] || severity}
            </span>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between text-[11px] text-[#8A9A91] mb-1">
        <span>{moment(dataPoint.timestamp).format('DD/MM/YYYY')}</span>
        {!dataPoint.image_url && (
          <span
            className="text-[9px] font-bold px-2 py-0.5 rounded-full text-white capitalize"
            style={{ backgroundColor: badgeColor }}
          >
            {severityLabel[score] || severity}
          </span>
        )}
      </div>

      <p className="font-heading text-xs font-bold text-[#10221A] line-clamp-1">
        {dataPoint.crop || 'Plante'}
      </p>
      {dataPoint.disease && (
        <p className="text-[11px] text-[#5B6B62] line-clamp-2 mt-0.5">
          {dataPoint.disease}
        </p>
      )}
      {dataPoint.notes && (
        <p className="text-[10px] text-[#78887F] italic mt-1.5 border-t border-[#F0FAF4] pt-1 line-clamp-2">
          {dataPoint.notes}
        </p>
      )}
    </div>
  );
}

export default function HealthChart({ scans, days }) {
  const start = moment().subtract(days, 'days').valueOf();

  const seriesColors = ['#12523A', '#2F6FE4', '#E8B84B', '#5B6B62', '#D6473B', '#1B7049'];
  const seriesGroups = {};

  const validScans = scans
    .filter(s => moment(s.created_date).valueOf() >= start)
    .sort((a, b) => new Date(a.created_date) - new Date(b.created_date));

  validScans.forEach(s => {
    // Si scans du même carnet, on les groupe sur la même série principale
    const seriesId = s.tracking_id ? `tracking_${s.tracking_id}` : `${s.crop_name || 'Inconnu'}|${s.disease_name || 'Général'}`;
    const mainLabel = s.disease_name ? `${s.crop_name} – ${s.disease_name}` : s.crop_name || 'Suivi de santé';

    if (!seriesGroups[seriesId]) {
      seriesGroups[seriesId] = {
        id: seriesId,
        label: mainLabel,
        crop: s.crop_name,
        disease: s.disease_name,
        color: seriesColors[Object.keys(seriesGroups).length % seriesColors.length],
        points: [],
      };
    }

    const timestamp = moment(s.created_date).valueOf();
    seriesGroups[seriesId].points.push({
      timestamp,
      date: moment(s.created_date).format('DD/MM HH:mm'),
      score: severityScore[s.severity] || 1,
      image_url: s.image_url || null,
      scanId: s.id,
      disease: s.disease_name,
      crop: s.crop_name,
      severity: s.severity,
      notes: s.notes,
      is_healthy: s.is_healthy,
    });
  });

  const seriesList = Object.values(seriesGroups);
  seriesList.forEach(group => {
    group.points.sort((a, b) => a.timestamp - b.timestamp);
  });

  // Si un seul timestamp unique, padding virtuel pour axe X
  const allTimestamps = seriesList.flatMap(g => g.points.map(p => p.timestamp));
  const uniqueTimestamps = new Set(allTimestamps);
  if (uniqueTimestamps.size === 1) {
    const onlyTs = [...uniqueTimestamps][0];
    seriesList.forEach(group => {
      group.points.unshift({
        timestamp: onlyTs - 24 * 3600 * 1000,
        date: moment(onlyTs - 24 * 3600 * 1000).format('DD/MM'),
        score: null,
        image_url: null,
        scanId: null,
        disease: group.disease,
        crop: group.crop,
        severity: null,
        _virtual: true,
      });
    });
  }

  const dataMap = {};
  const seriesLabelMap = {};
  seriesList.forEach(group => {
    seriesLabelMap[group.id] = group.label;
    group.points.forEach(point => {
      const key = point.timestamp;
      if (!dataMap[key]) {
        dataMap[key] = {
          timestamp: point.timestamp,
          date: point.date,
          image_url: point.image_url,
          scanId: point.scanId,
          severity: point.severity,
          crop: point.crop,
          disease: point.disease,
          notes: point.notes,
          score: point.score,
        };
      }
      dataMap[key][group.id] = point.score;
    });
  });

  const data = Object.values(dataMap).sort((a, b) => a.timestamp - b.timestamp);

  // Pastille de scan avec miniature photo et anneau de couleur de sévérité
  const renderPhotoPoint = (color) => (props) => {
    const { cx, cy, payload } = props;
    if (!payload || payload._virtual || payload.score == null) return null;

    const ring = severityColorsMap[payload.severity] || severityColors[payload.severity] || color || '#12523A';
    const rOuter = 13;
    const rInner = 11;
    const size = rInner * 2;

    if (payload.image_url) {
      const clipId = `clip-photo-${payload.scanId || payload.timestamp}`;
      return (
        <g className="cursor-pointer transition-transform hover:scale-125">
          <defs>
            <clipPath id={clipId}>
              <circle cx={cx} cy={cy} r={rInner} />
            </clipPath>
          </defs>
          {/* Ombre portée subtile */}
          <circle cx={cx} cy={cy + 1} r={rOuter} fill="rgba(0,0,0,0.12)" />
          {/* Anneau extérieur coloré selon la sévérité */}
          <circle cx={cx} cy={cy} r={rOuter} fill="#FFFFFF" stroke={ring} strokeWidth={2.5} />
          {/* Photo de la feuille */}
          <image
            href={payload.image_url}
            xlinkHref={payload.image_url}
            x={cx - rInner}
            y={cy - rInner}
            width={size}
            height={size}
            clipPath={`url(#${clipId})`}
            preserveAspectRatio="xMidYMid slice"
          />
        </g>
      );
    }

    // Fallback sans photo : pastille pleine cerclée de blanc
    return (
      <g className="cursor-pointer">
        <circle cx={cx} cy={cy + 1} r={8} fill="rgba(0,0,0,0.1)" />
        <circle cx={cx} cy={cy} r={7.5} fill={ring} stroke="#FFFFFF" strokeWidth={2.5} />
      </g>
    );
  };

  if (seriesList.length === 0) {
    return (
      <p className="text-xs text-center text-[#8A9A91] font-body py-8">
        Aucune photo sur cette période. Scannez vos cultures pour suivre l'évolution.
      </p>
    );
  }

  // Ticks uniques par timestamp réel pour éviter les doublons de dates (ex: "21/10 21/10")
  const distinctTicks = Array.from(new Set(data.map(p => p.timestamp))).sort((a, b) => a - b);

  return (
    <div>
      <ResponsiveContainer width="100%" height={215}>
        <ComposedChart data={data} margin={{ top: 16, right: 15, left: -14, bottom: 6 }}>
          <defs>
            <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#12523A" stopOpacity={0.28} />
              <stop offset="60%" stopColor="#1B7049" stopOpacity={0.10} />
              <stop offset="100%" stopColor="#1B7049" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#DCE7E0" opacity={0.35} vertical={false} />
          <XAxis
            type="number"
            dataKey="timestamp"
            domain={['dataMin - 43200000', 'dataMax + 43200000']}
            ticks={distinctTicks}
            tickFormatter={(ts) => moment(ts).format('DD/MM')}
            tick={{ fontSize: 10, fill: '#5B6B62', fontWeight: 600 }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            domain={[0.6, 4.4]}
            ticks={[1, 2, 3, 4]}
            tickFormatter={(v) => severityLabel[v] || ''}
            tick={{ fontSize: 9.5, fill: '#8A9A91', fontWeight: 500 }}
            tickLine={false}
            axisLine={false}
            width={58}
          />
          <Tooltip content={<CustomHealthTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: 11, color: '#5B6B62', paddingTop: '4px' }}
            formatter={(value) => seriesLabelMap[value] || value}
          />
          {seriesList.map(group => (
            <React.Fragment key={group.id}>
              {/* Courbe avec zone dégradée sous la ligne */}
              <Area
                type="monotone"
                dataKey={group.id}
                name={group.label}
                stroke={group.color}
                fill="url(#trendGrad)"
                strokeWidth={2.5}
                dot={false}
                activeDot={false}
              />
              {/* Pastilles photos (sans doublon dans la légende grâce à legendType="none") */}
              <Scatter
                data={group.points}
                dataKey="score"
                shape={renderPhotoPoint(group.color)}
                legendType="none"
              />
            </React.Fragment>
          ))}
        </ComposedChart>
      </ResponsiveContainer>
      <div className="flex items-center justify-center gap-3 mt-1.5 text-[10px] text-[#5B6B62]">
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-[#D6473B]" /> Critique
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-[#E8B84B]" /> Élevée / Modérée
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-[#1B7049]" /> Faible (Guéri)
        </span>
      </div>
      <p className="text-[10px] text-center text-[#8A9A91] font-body mt-1">
        Chaque pastille = photo scannée au jour le jour • Touchez pour agrandir
      </p>
    </div>
  );
}