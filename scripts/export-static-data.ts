import fs from 'fs';
import path from 'path';
import type { Arena } from '@/lib/types';

const ALL_ARENAS_DIR = path.join(process.cwd(), 'Content', 'Arena', 'All Arenas');
const JSON_ZH_PATH = path.join(process.cwd(), 'Content', 'Arena', 'page.zh.json');
const JSON_EN_PATH = path.join(process.cwd(), 'Content', 'Arena', 'page.en.json');
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

// Unified row type for both ZH and EN JSON files
type ArenaRow = {
  arena_no?: string | number;
  title?: string;
  champion?: string;
  verification_status?: string;
  highlights?: string;
  industry?: string;
  category?: string;
  speed?: string;
  quality?: string;
  security?: string;
  cost?: string;
  challenger?: string;
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

function readRowsFromJson<T extends Record<string, unknown>>(filePath: string): T[] {
  if (!fs.existsSync(filePath)) {
    throw new Error(`JSON file not found: ${filePath}`);
  }
  const parsed = parseJsonSafe(fs.readFileSync(filePath, 'utf-8'));
  if (!Array.isArray(parsed)) {
    throw new Error(`JSON data is not an array: ${filePath}`);
  }
  return parsed as T[];
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

function buildArenasFromJson(): Arena[] {
  const zhRows = readRowsFromJson<ArenaRow>(JSON_ZH_PATH);
  const enRows = readRowsFromJson<ArenaRow>(JSON_EN_PATH);

  const enMap = new Map<string, ArenaRow>();
  for (const row of enRows) {
    const arenaNo = cleanText(row.arena_no);
    if (arenaNo) {
      enMap.set(arenaNo, row);
    }
  }

  const folderMap = buildFolderMapByArenaNo();
  const arenas: Arena[] = [];

  for (const row of zhRows) {
    const arenaNo = cleanText(row.arena_no);
    if (!arenaNo) continue;

    const enRow = enMap.get(arenaNo);
    const folderId = folderMap.get(arenaNo) || '';

    const titleZh = cleanText(row.title);
    if (!titleZh || titleZh.includes('敬请期待')) {
      continue;
    }

    const arena: Arena = {
      id: arenaNo,
      folderId,
      title: {
        zh: titleZh,
        en: cleanText(enRow?.title),
      },
      category: cleanText(row.category),
      categoryEn: cleanText(enRow?.category),
      industry: cleanText(row.industry),
      industryEn: cleanText(enRow?.industry),
      verificationStatus: cleanText(row.verification_status),
      champion: cleanText(row.champion),
      championEn: cleanText(enRow?.champion),
      challenger: cleanText(row.challenger),
      challengerEn: cleanText(enRow?.challenger),
      highlights: cleanText(row.highlights),
      highlightsEn: cleanText(enRow?.highlights),
      metrics: {
        speed: cleanText(row.speed),
        quality: cleanText(row.quality),
        security: cleanText(row.security),
        cost: cleanText(row.cost),
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

  const arenas = buildArenasFromJson();
  const contentMap = buildContentMapFromJsonFiles();

  writeJson(ARENAS_JSON_PATH, arenas);
  writeJson(ARENA_CONTENT_JSON_PATH, contentMap);

  console.log(`[export-static-data] source=json+tabs-json`);
  console.log(`[export-static-data] arenas=${arenas.length}`);
  console.log(`[export-static-data] wrote ${ARENAS_JSON_PATH}`);
  console.log(`[export-static-data] wrote ${ARENA_CONTENT_JSON_PATH}`);
}

main();
