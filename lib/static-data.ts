import fs from 'fs';
import path from 'path';
import type { Arena } from '@/lib/types';

// In Next.js, files in lib/ are bundled, so __dirname is not reliable.
// We use process.cwd() which is the project root in both dev and build.
const PROJECT_ROOT = process.cwd();
const ARENAS_ROOT_DIR = path.join(PROJECT_ROOT, 'Content', 'Arena', 'All Arenas');

// Use a function so paths are evaluated at runtime.
function getArenaJsonPaths() {
  return {
    zh: path.join(PROJECT_ROOT, 'Content', 'Arena', 'page.zh.json'),
    en: path.join(PROJECT_ROOT, 'Content', 'Arena', 'page.en.json'),
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

function cleanText(value: unknown): string {
  return String(value ?? '').trim();
}

function readJsonRows<T extends Record<string, unknown>>(filePath: string): T[] {
  if (!fs.existsSync(filePath)) return [];
  try {
    const parsed = JSON.parse(fs.readFileSync(filePath, 'utf-8')) as unknown;
    return Array.isArray(parsed) ? (parsed as T[]) : [];
  } catch {
    return [];
  }
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

function buildArenasFromJson(): Arena[] {
  const jsonPaths = getArenaJsonPaths();
  const zhRows = readJsonRows<ArenaRow>(jsonPaths.zh);
  const enRows = readJsonRows<ArenaRow>(jsonPaths.en);

  const folderMap = buildFolderMapByArenaNo();
  const enMap = new Map<string, ArenaRow>();
  for (const row of enRows) {
    const arenaNo = cleanText(row.arena_no);
    if (arenaNo) {
      enMap.set(arenaNo, row);
    }
  }

  const arenas: Arena[] = [];
  for (const row of zhRows) {
    const arenaNo = cleanText(row.arena_no);
    if (!arenaNo) continue;

    const enRow = enMap.get(arenaNo);
    const titleZh = cleanText(row.title);
    if (!titleZh || titleZh.includes('敬请期待')) continue;

    const folderId = folderMap.get(arenaNo) || '';
    arenas.push({
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
    });
  }

  return arenas.sort((a, b) => Number(a.id) - Number(b.id));
}

function getArenasMtimeKey(): string {
  const jsonPaths = getArenaJsonPaths();
  const zhMtime = fs.existsSync(jsonPaths.zh) ? fs.statSync(jsonPaths.zh).mtimeMs : 0;
  const enMtime = fs.existsSync(jsonPaths.en) ? fs.statSync(jsonPaths.en).mtimeMs : 0;
  return `${zhMtime}|${enMtime}`;
}

export async function getAllArenasFromStaticData(): Promise<Arena[]> {
  const mtimeKey = getArenasMtimeKey();
  if (cachedArenas && cachedArenasMtimeKey === mtimeKey) {
    return cachedArenas;
  }

  cachedArenas = buildArenasFromJson();
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
