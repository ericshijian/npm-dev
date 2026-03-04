import { Building2, ShoppingCart, GraduationCap, HeartPulse, Zap, Factory } from 'lucide-react';

export const categories = {
  service: { en: 'Service', zh: '服务' },
  management: { en: 'Management', zh: '管理' },
  marketing: { en: 'Marketing', zh: '营销' },
  'risk-control': { en: 'Risk Control', zh: '风控' },
  operations: { en: 'Operations', zh: '运营' },
  general: { en: 'General', zh: '通用' },
};

export const industries = {
  finance: { en: 'Finance', zh: '金融', icon: Building2 },
  retail: { en: 'Retail', zh: '零售', icon: ShoppingCart },
  education: { en: 'Education', zh: '教育', icon: GraduationCap },
  healthcare: { en: 'Healthcare', zh: '医疗', icon: HeartPulse },
  energy: { en: 'Energy', zh: '能源', icon: Zap },
  manufacturing: { en: 'Manufacturing', zh: '制造', icon: Factory },
  general: { en: 'General', zh: '通用', icon: Building2 },
};
