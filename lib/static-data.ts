import fs from 'fs';
import path from 'path';
import * as XLSX from 'xlsx';
import type { Arena } from '@/lib/types';

// In Next.js, files in lib/ are bundled, so __dirname is not reliable.
// We use process.cwd() which is the project root in both dev and build.
const PROJECT_ROOT = process.cwd();
const ARENAS_ROOT_DIR = path.join(PROJECT_ROOT, 'Content', 'Arena', 'All Arenas');

// Use a function to get CSV paths so they're evaluated at runtime
function getCsvPaths() {
  return {
    zh: path.join(PROJECT_ROOT, 'Content', 'Arena', 'List of Arenas ZH.csv'),
    en: path.join(PROJECT_ROOT, 'Content', 'Arena', 'List of Arenas EN.csv'),
  };
}

export type ArenaTechConfigStep = {
  number: number;
  title: string;
  subsections: Array<{ title: string; content: string[] }>;
};

export type ArenaTechConfigPayload = {
  markdown?: string;
  steps?: ArenaTechConfigStep[];
  [key: string]: unknown;
};

export type ArenaContentValue = string | ArenaTechConfigPayload;
type ArenaContentMap = Record<string, Record<string, Record<string, ArenaContentValue>>>;

let cachedArenas: Arena[] | null = null;
let cachedArenasMtimeKey = '';

type CsvZhRow = {
  擂台编号?: string | number;
  擂台名称?: string;
  本周擂主?: string;
  验证状态?: string;
  亮点?: string;
  行业类别?: string;
  应用类别?: string;
  速度?: string;
  质量?: string;
  安全?: string;
  成本?: string;
  攻擂中?: string;
};

type CsvEnRow = {
  arena_no?: string | number;
  title_zh?: string;
  title_en?: string;
  champion_zh?: string;
  champion_en?: string;
  verification_status_zh?: string;
  highlights_zh?: string;
  highlights_en?: string;
  industry_zh?: string;
  industry_en?: string;
  category_zh?: string;
  category_en?: string;
  speed_zh?: string;
  quality_zh?: string;
  security_zh?: string;
  cost_zh?: string;
  challenger_zh?: string;
  challenger_en?: string;
};

function cleanText(value: unknown): string {
  return String(value ?? '').trim();
}

function readCsvRows<T extends Record<string, unknown>>(filePath: string): T[] {
  if (!fs.existsSync(filePath)) return [];
  // Use readFileSync + XLSX.read for better compatibility with Next.js build
  const fileContent = fs.readFileSync(filePath);
  const workbook = XLSX.read(fileContent, { type: 'buffer', raw: false });
  const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
  return XLSX.utils.sheet_to_json<T>(firstSheet, { defval: '' });
}

function buildFolderMapByArenaNo(): Map<string, string> {
  const map = new Map<string, string>();
  if (!fs.existsSync(ARENAS_ROOT_DIR)) {
    return map;
  }

  const dirs = fs.readdirSync(ARENAS_ROOT_DIR, { withFileTypes: true }).filter((entry) => entry.isDirectory());
  for (const dir of dirs) {
    const match = dir.name.match(/^(\d+)-/);
    if (match) {
      map.set(match[1], dir.name);
    }
  }
  return map;
}

function hasArenaContent(folderId: string): boolean {
  if (!folderId) return false;
  const folderPath = path.join(ARENAS_ROOT_DIR, folderId);
  if (!fs.existsSync(folderPath)) return false;

  return fs.existsSync(path.join(folderPath, 'overview.zh.json'))
    || fs.existsSync(path.join(folderPath, 'overview.en.json'))
    || fs.existsSync(path.join(folderPath, 'implementation.zh.json'))
    || fs.existsSync(path.join(folderPath, 'implementation.en.json'))
    || fs.existsSync(path.join(folderPath, 'tech-configuration.zh.json'))
    || fs.existsSync(path.join(folderPath, 'tech-configuration.en.json'));
}

function buildArenasFromCsv(): Arena[] {
  const csvPaths = getCsvPaths();
  const zhRows = readCsvRows<CsvZhRow>(csvPaths.zh);
  const enRows = readCsvRows<CsvEnRow>(csvPaths.en);

  const folderMap = buildFolderMapByArenaNo();
  const enMap = new Map<string, CsvEnRow>();
  for (const row of enRows) {
    const arenaNo = cleanText(row.arena_no);
    if (arenaNo) {
      enMap.set(arenaNo, row);
    }
  }

  const arenas: Arena[] = [];
  for (const row of zhRows) {
    const arenaNo = cleanText(row.擂台编号);
    if (!arenaNo) continue;

    const enRow = enMap.get(arenaNo);
    const titleZh = cleanText(row.擂台名称 || enRow?.title_zh);
    if (!titleZh || titleZh.includes('敬请期待')) continue;

    const folderId = folderMap.get(arenaNo) || '';
    arenas.push({
      id: arenaNo,
      folderId,
      title: {
        zh: titleZh,
        en: cleanText(enRow?.title_en),
      },
      category: cleanText(row.应用类别 || enRow?.category_zh),
      categoryEn: cleanText(enRow?.category_en),
      industry: cleanText(row.行业类别 || enRow?.industry_zh),
      industryEn: cleanText(enRow?.industry_en),
      verificationStatus: cleanText(row.验证状态 || enRow?.verification_status_zh),
      champion: cleanText(row.本周擂主 || enRow?.champion_zh),
      championEn: cleanText(enRow?.champion_en),
      challenger: cleanText(row.攻擂中 || enRow?.challenger_zh),
      challengerEn: cleanText(enRow?.challenger_en),
      highlights: cleanText(row.亮点 || enRow?.highlights_zh),
      highlightsEn: cleanText(enRow?.highlights_en),
      metrics: {
        speed: cleanText(row.速度 || enRow?.speed_zh),
        quality: cleanText(row.质量 || enRow?.quality_zh),
        security: cleanText(row.安全 || enRow?.security_zh),
        cost: cleanText(row.成本 || enRow?.cost_zh),
      },
      hasContent: hasArenaContent(folderId),
    });
  }

  return arenas.sort((a, b) => Number(a.id) - Number(b.id));
}

function getArenasMtimeKey(): string {
  const csvPaths = getCsvPaths();
  const zhMtime = fs.existsSync(csvPaths.zh) ? fs.statSync(csvPaths.zh).mtimeMs : 0;
  const enMtime = fs.existsSync(csvPaths.en) ? fs.statSync(csvPaths.en).mtimeMs : 0;
  return `${zhMtime}|${enMtime}`;
}

export async function getAllArenasFromStaticData(): Promise<Arena[]> {
  const mtimeKey = getArenasMtimeKey();
  if (cachedArenas && cachedArenasMtimeKey === mtimeKey) {
    return cachedArenas;
  }

  cachedArenas = buildArenasFromCsv();
  cachedArenasMtimeKey = mtimeKey;
  return cachedArenas;
}

export async function getArenaContentFromStaticData(
  folderId: string,
  tabKey: string,
  locale: string
): Promise<ArenaContentValue | null> {
  const normalizedLocale = locale === 'zh' ? 'zh' : 'en';
  const tabJsonPath = path.join(
    ARENAS_ROOT_DIR,
    folderId,
    `${tabKey}.${normalizedLocale}.json`
  );
  if (!fs.existsSync(tabJsonPath)) {
    return null;
  }
  try {
    return JSON.parse(fs.readFileSync(tabJsonPath, 'utf-8')) as ArenaContentValue;
  } catch (error) {
    console.error(`[static-data] Failed to parse tab JSON: ${tabJsonPath}`, error);
    return null;
  }
}
