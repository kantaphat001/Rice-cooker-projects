/**
 * Smart Rice Cooker - Theme & Medication Color System (2026 Edition)
 * Centralized design tokens and color mappings for elder accessibility.
 * Completely eliminates hardcoded color strings across the application.
 */

export const MED_COLOR_OPTIONS = [
  {
    key: 'pink',
    label: 'ซองสีชมพู',
    icon: '🌸',
    keywords: ['ชมพู', 'pink'],
    bgTint: 'bg-rose-50/60',
    hoverBg: 'hover:bg-rose-50',
    badgeBg: 'bg-rose-100/80',
    badgeText: 'text-rose-800',
    accentDot: 'bg-rose-500',
    previewBorder: 'ring-rose-400',
  },
  {
    key: 'green',
    label: 'ซองสีเขียว',
    icon: '🟢',
    keywords: ['เขียว', 'green'],
    bgTint: 'bg-emerald-50/60',
    hoverBg: 'hover:bg-emerald-50',
    badgeBg: 'bg-emerald-100/80',
    badgeText: 'text-emerald-800',
    accentDot: 'bg-emerald-500',
    previewBorder: 'ring-emerald-400',
  },
  {
    key: 'blue',
    label: 'ซองสีฟ้า',
    icon: '🔵',
    keywords: ['ฟ้า', 'น้ำเงิน', 'blue'],
    bgTint: 'bg-sky-50/60',
    hoverBg: 'hover:bg-sky-50',
    badgeBg: 'bg-sky-100/80',
    badgeText: 'text-sky-800',
    accentDot: 'bg-sky-500',
    previewBorder: 'ring-sky-400',
  },
  {
    key: 'yellow',
    label: 'ซองสีเหลือง',
    icon: '🟡',
    keywords: ['เหลือง', 'yellow'],
    bgTint: 'bg-amber-50/60',
    hoverBg: 'hover:bg-amber-50',
    badgeBg: 'bg-amber-100/80',
    badgeText: 'text-amber-900',
    accentDot: 'bg-amber-500',
    previewBorder: 'ring-amber-400',
  },
  {
    key: 'orange',
    label: 'ซองสีส้ม',
    icon: '🟠',
    keywords: ['ส้ม', 'orange'],
    bgTint: 'bg-orange-50/60',
    hoverBg: 'hover:bg-orange-50',
    badgeBg: 'bg-orange-100/80',
    badgeText: 'text-orange-900',
    accentDot: 'bg-orange-500',
    previewBorder: 'ring-orange-400',
  },
  {
    key: 'red',
    label: 'ซองสีแดง',
    icon: '🔴',
    keywords: ['แดง', 'red'],
    bgTint: 'bg-red-50/60',
    hoverBg: 'hover:bg-red-50',
    badgeBg: 'bg-red-100/80',
    badgeText: 'text-red-900',
    accentDot: 'bg-red-500',
    previewBorder: 'ring-red-400',
  },
  {
    key: 'purple',
    label: 'ซองสีม่วง',
    icon: '🟣',
    keywords: ['ม่วง', 'purple'],
    bgTint: 'bg-purple-50/60',
    hoverBg: 'hover:bg-purple-50',
    badgeBg: 'bg-purple-100/80',
    badgeText: 'text-purple-900',
    accentDot: 'bg-purple-500',
    previewBorder: 'ring-purple-400',
  },
  {
    key: 'white',
    label: 'ซองสีขาว',
    icon: '⚪',
    keywords: ['ขาว', 'white'],
    bgTint: 'bg-slate-50',
    hoverBg: 'hover:bg-slate-100/70',
    badgeBg: 'bg-slate-200/80',
    badgeText: 'text-slate-800',
    accentDot: 'bg-slate-400',
    previewBorder: 'ring-slate-300',
  },
  {
    key: 'box',
    label: 'ช่องเก็บยา',
    icon: '📦',
    keywords: ['ช่อง', 'ตลับ', 'กล่อง', 'box'],
    bgTint: 'bg-indigo-50/60',
    hoverBg: 'hover:bg-indigo-50',
    badgeBg: 'bg-indigo-100/80',
    badgeText: 'text-indigo-900',
    accentDot: 'bg-indigo-500',
    previewBorder: 'ring-indigo-400',
  }
];

export const DEFAULT_THEME = {
  key: 'default',
  label: '',
  icon: '💊',
  bgTint: 'bg-white',
  hoverBg: 'hover:bg-slate-50',
  badgeBg: 'bg-slate-100',
  badgeText: 'text-slate-700',
  accentDot: 'bg-emerald-500',
  previewBorder: 'ring-slate-200',
};

/**
 * Normalizes user input typos (e.g. "ของสี..." -> "ซองสี...")
 */
export function normalizeTag(tag) {
  if (!tag) return '';
  let clean = tag.trim();
  if (clean.startsWith('ของสี')) {
    clean = 'ซองสี' + clean.substring(5);
  }
  return clean;
}

/**
 * Retrieves color design token matching medication color_tag or name
 */
export function getMedTheme(colorTag = '', medName = '') {
  const cleanTag = normalizeTag(colorTag);
  const searchStr = `${cleanTag} ${medName || ''}`.toLowerCase();

  for (const option of MED_COLOR_OPTIONS) {
    if (option.keywords.some((kw) => searchStr.includes(kw))) {
      return {
        ...option,
        label: cleanTag || option.label
      };
    }
  }

  if (cleanTag) {
    return {
      key: 'custom',
      label: cleanTag,
      icon: '🏷️',
      bgTint: 'bg-emerald-50/40',
      hoverBg: 'hover:bg-emerald-50',
      badgeBg: 'bg-emerald-100/80',
      badgeText: 'text-emerald-800',
      accentDot: 'bg-emerald-500',
      previewBorder: 'ring-emerald-400',
    };
  }

  return DEFAULT_THEME;
}
