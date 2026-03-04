import fs from 'fs';
import path from 'path';
import * as XLSX from 'xlsx';
import type { Arena } from '@/lib/types';

const ALL_ARENAS_DIR = path.join(process.cwd(), 'Content', 'Arena', 'All Arenas');
const CSV_ZH_PATH = path.join(process.cwd(), 'Content', 'Arena', 'List of Arenas ZH.csv');
const CSV_EN_PATH = path.join(process.cwd(), 'Content', 'Arena', 'List of Arenas EN.csv');
const PUBLIC_DATA_DIR = path.join(process.cwd(), 'public', 'data');
const ARENAS_JSON_PATH = path.join(PUBLIC_DATA_DIR, 'arenas.json');
const ARENA_CONTENT_JSON_PATH = path.join(PUBLIC_DATA_DIR, 'arena-content.json');

type ArenaTechConfigStep = {
  number: number;
  title: string;
  subsections: Array<{ title: string; content: string[] }>;
};

type ArenaTechConfigPayload = {
  markdown?: string;
  steps?: ArenaTechConfigStep[];
  [key: string]: unknown;
};

type ArenaOverviewPayload = {
  highlight?: string;
  industry?: string;
  category?: string;
  cycle?: string;
  case_no?: string;
  sections?: Array<{ title: string; subsections: Array<{ title: string; content: string[] }> }>;
  markdown?: string;
  [key: string]: unknown;
};

type ArenaImplementationPayload = {
  markdown?: string;
  phases?: Array<{ title: string; subsections: Array<{ title: string; content: string[] }> }>;
  [key: string]: unknown;
};

type ArenaContentValue = string | ArenaTechConfigPayload | ArenaOverviewPayload | ArenaImplementationPayload;
type ArenaContentMap = Record<string, Record<string, Record<string, ArenaContentValue>>>;

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
  verification_status_en?: string;
  highlights_zh?: string;
  highlights_en?: string;
  industry_zh?: string;
  industry_en?: string;
  category_zh?: string;
  category_en?: string;
  speed_zh?: string;
  speed_en?: string;
  quality_zh?: string;
  quality_en?: string;
  security_zh?: string;
  security_en?: string;
  cost_zh?: string;
  cost_en?: string;
  challenger_zh?: string;
  challenger_en?: string;
};

function ensureOutputDir() {
  fs.mkdirSync(PUBLIC_DATA_DIR, { recursive: true });
}

function writeJson(filePath: string, data: unknown) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
}

function parseJsonSafe(value: string | null): unknown {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function readCsvRows<T extends Record<string, unknown>>(filePath: string): T[] {
  if (!fs.existsSync(filePath)) {
    throw new Error(`CSV file not found: ${filePath}`);
  }
  const workbook = XLSX.readFile(filePath, { raw: false });
  const sheetName = workbook.SheetNames[0];
  const worksheet = workbook.Sheets[sheetName];
  return XLSX.utils.sheet_to_json<T>(worksheet, { defval: '' });
}

function cleanText(value: unknown): string {
  return String(value ?? '').trim();
}

function buildFolderMapByArenaNo(): Map<string, string> {
  const map = new Map<string, string>();
  if (!fs.existsSync(ALL_ARENAS_DIR)) {
    return map;
  }

  const dirs = fs.readdirSync(ALL_ARENAS_DIR, { withFileTypes: true }).filter((entry) => entry.isDirectory());
  for (const entry of dirs) {
    const match = entry.name.match(/^(\d+)-/);
    if (match) {
      map.set(match[1], entry.name);
    }
  }

  return map;
}

function hasArenaContent(folderId: string): boolean {
  if (!folderId) return false;
  const baseDir = path.join(ALL_ARENAS_DIR, folderId);
  if (!fs.existsSync(baseDir)) return false;

  const required = [
    'overview.zh.json',
    'overview.en.json',
    'implementation.zh.json',
    'implementation.en.json',
    'tech-configuration.zh.json',
    'tech-configuration.en.json',
  ];

  return required.some((file) => fs.existsSync(path.join(baseDir, file)));
}

function buildArenasFromCsv(): Arena[] {
  const zhRows = readCsvRows<CsvZhRow>(CSV_ZH_PATH);
  const enRows = readCsvRows<CsvEnRow>(CSV_EN_PATH);

  const enMap = new Map<string, CsvEnRow>();
  for (const row of enRows) {
    const arenaNo = cleanText(row.arena_no);
    if (arenaNo) {
      enMap.set(arenaNo, row);
    }
  }

  const folderMap = buildFolderMapByArenaNo();
  const arenas: Arena[] = [];

  for (const row of zhRows) {
    const arenaNo = cleanText(row.擂台编号);
    if (!arenaNo) continue;

    const enRow = enMap.get(arenaNo);
    const folderId = folderMap.get(arenaNo) || '';

    const titleZh = cleanText(row.擂台名称 || enRow?.title_zh);
    if (!titleZh || titleZh.includes('敬请期待')) {
      continue;
    }

    const arena: Arena = {
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
    };

    arenas.push(arena);
  }

  arenas.sort((a, b) => Number(a.id) - Number(b.id));
  return arenas;
}

function buildContentMapFromJsonFiles(): ArenaContentMap {
  const contentMap: ArenaContentMap = {};

  function setContent(folderId: string, locale: string, tabKey: string, content: ArenaContentValue) {
    if (!folderId || !locale || !tabKey || !content) {
      return;
    }
    contentMap[folderId] = contentMap[folderId] || {};
    contentMap[folderId][locale] = contentMap[folderId][locale] || {};
    contentMap[folderId][locale][tabKey] = content;
  }

  const arenaFolders = fs.existsSync(ALL_ARENAS_DIR)
    ? fs.readdirSync(ALL_ARENAS_DIR, { withFileTypes: true }).filter((entry) => entry.isDirectory())
    : [];

  for (const entry of arenaFolders) {
    const folderId = entry.name;
    const baseDir = path.join(ALL_ARENAS_DIR, folderId);

    const tabFileSpecs: Array<{
      tabKey: 'overview' | 'implementation' | 'tech-configuration';
      fileName: string;
      zhType: 'overview' | 'implementation' | 'tech';
      enType: 'overview' | 'implementation' | 'tech';
    }> = [
      { tabKey: 'overview', fileName: 'overview', zhType: 'overview', enType: 'overview' },
      { tabKey: 'implementation', fileName: 'implementation', zhType: 'implementation', enType: 'implementation' },
      { tabKey: 'tech-configuration', fileName: 'tech-configuration', zhType: 'tech', enType: 'tech' },
    ];

    for (const spec of tabFileSpecs) {
      const zhPath = path.join(baseDir, `${spec.fileName}.zh.json`);
      const zhContent = parseJsonSafe(
        fs.existsSync(zhPath) ? fs.readFileSync(zhPath, 'utf-8') : null
      );
      if (zhContent && typeof zhContent === 'object') {
        const typedZh =
          spec.zhType === 'overview'
            ? (zhContent as ArenaOverviewPayload)
            : spec.zhType === 'implementation'
              ? (zhContent as ArenaImplementationPayload)
              : (zhContent as ArenaTechConfigPayload);
        setContent(folderId, 'zh', spec.tabKey, typedZh);
      }

      const enPath = path.join(baseDir, `${spec.fileName}.en.json`);
      const enContent = parseJsonSafe(
        fs.existsSync(enPath) ? fs.readFileSync(enPath, 'utf-8') : null
      );
      if (enContent && typeof enContent === 'object') {
        const typedEn =
          spec.enType === 'overview'
            ? (enContent as ArenaOverviewPayload)
            : spec.enType === 'implementation'
              ? (enContent as ArenaImplementationPayload)
              : (enContent as ArenaTechConfigPayload);
        setContent(folderId, 'en', spec.tabKey, typedEn);
      }
    }
  }

  return contentMap;
}

function main() {
  ensureOutputDir();

  const arenas = buildArenasFromCsv();
  const contentMap = buildContentMapFromJsonFiles();

  writeJson(ARENAS_JSON_PATH, arenas);
  writeJson(ARENA_CONTENT_JSON_PATH, contentMap);

  console.log(`[export-static-data] source=csv+tabs-json`);
  console.log(`[export-static-data] arenas=${arenas.length}`);
  console.log(`[export-static-data] wrote ${ARENAS_JSON_PATH}`);
  console.log(`[export-static-data] wrote ${ARENA_CONTENT_JSON_PATH}`);
}

main();
