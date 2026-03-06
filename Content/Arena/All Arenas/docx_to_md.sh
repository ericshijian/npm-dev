#!/usr/bin/env bash
set -euo pipefail

# 用法: ./batch_docx_to_md.sh [--force]
#   --force  强制重新生成所有 md 文件，忽略修改时间检查

FORCE_MODE=false
for arg in "$@"; do
  case "$arg" in
    --force|-f)
      FORCE_MODE=true
      shift
      ;;
  esac
done

BASE_DIR="${BASE_DIR:-.}"
LOG_DIR="${LOG_DIR:-logs/pandoc}"
MAPPING_FILE="${MAPPING_FILE:-logs/filename_mapping.tsv}"

# 文档类型后缀列表（可根据需要扩展）
DOC_TYPE_SUFFIXES=(
  "实践详情"
  # "xxx"
)

PANDOC="${PANDOC:-pandoc}"

if ! command -v "$PANDOC" >/dev/null 2>&1; then
  echo "Error: pandoc 未安装，请先安装 pandoc。" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"

# 初始化映射文件
printf "docx_file\tcn_name\tmd_file\n" > "$MAPPING_FILE"

# 中英文文件名映射函数
cn_to_en() {
  local cn_name="$1"
  case "$cn_name" in
    "首页") echo "main" ;;
    "实践详情") echo "implementation-details" ;;
    *) echo "$cn_name" ;;
  esac
}

# 你可以按需增减这些扩展
TO_FMT="gfm+pipe_tables+task_lists+tex_math_dollars"

# 通用参数：尽量让输出"可维护"
COMMON_ARGS=(
  "--from=docx"
  "--to=$TO_FMT"
  "--wrap=none"
  "--markdown-headings=atx"
  "--reference-links"
  "--strip-comments"
)

count=0
failed=0
skipped=0

# 查找所有 */Original Documents/*.docx 文件
while IFS= read -r -d '' docx_file; do
  filename="$(basename "$docx_file")"
  name_without_ext="${filename%.docx}"

  # 获取 Original Documents 的父目录（即 1-xxx, 2-xxx 等）
  # 例如: ./1-intelligent-research-system/Original Documents/xxx.docx -> 1-intelligent-research-system
  parent_dir="$(dirname "$(dirname "$docx_file")")"
  output_subdir="$parent_dir/Original Documents"
  media_out="$output_subdir/media"

  # 根据文件名确定输出文件名
  # 如果匹配 DOC_TYPE_SUFFIXES，保留原文件名（如 "实践详情.docx" -> "实践详情.md"）
  # 否则输出为 "首页.md"
  is_matched=false
  cn_name=""
  for suffix in "${DOC_TYPE_SUFFIXES[@]}"; do
    if [[ "$name_without_ext" == "$suffix" ]]; then
      is_matched=true
      cn_name="$name_without_ext"
      break
    fi
  done

  if [[ "$is_matched" == false ]]; then
    cn_name="首页"
  fi

  # 转换为英文文件名
  output_name="$(cn_to_en "$cn_name")"
  md_file="$output_subdir/${output_name}.md"
  log_file="$LOG_DIR/${parent_dir##*/}-${output_name}.log"

  # 保存映射关系
  printf "%s\t%s\t%s\n" "$docx_file" "$cn_name" "$md_file" >> "$MAPPING_FILE"

  # 检查是否需要更新
  need_convert=true
  if [[ "$FORCE_MODE" == false ]] && [[ -f "$md_file" ]]; then
    # 获取文件的修改时间（Unix 时间戳）
    docx_mtime=$(stat -f %m "$docx_file" 2>/dev/null || stat -c %Y "$docx_file" 2>/dev/null)
    md_mtime=$(stat -f %m "$md_file" 2>/dev/null || stat -c %Y "$md_file" 2>/dev/null)

    if [[ -n "$docx_mtime" ]] && [[ -n "$md_mtime" ]] && [[ "$docx_mtime" -le "$md_mtime" ]]; then
      need_convert=false
      echo "Skipping (up-to-date): $docx_file"
    fi
  fi

  if [[ "$need_convert" == false ]]; then
    skipped=$((skipped + 1))
    continue
  fi

  echo "Converting: $docx_file -> $md_file"
  echo "  media: $media_out"
  echo "  log:   $log_file"

  mkdir -p "$media_out"

  # 注意：--extract-media 需要是每个文件独立目录，否则多个 docx 图片会互相覆盖
  if "$PANDOC" "$docx_file" \
      "${COMMON_ARGS[@]}" \
      --extract-media="$media_out" \
      -o "$md_file" \
      >"$log_file" 2>&1; then
    # 修正图片路径：
    # 1. pandoc 会生成 media/media/ 目录结构，需要移动到 media/
    if [[ -d "$media_out/media" ]]; then
      mv "$media_out/media/"* "$media_out/" 2>/dev/null || true
      rmdir "$media_out/media" 2>/dev/null || true
    fi
    # 2. 修正 md 文件中的图片路径引用
    # pandoc 生成的路径类似 "./xxx/media/media/image1.png"
    # 需要改为 "media/image1.png"（相对于 md 文件）
    sed -i.bak "s|\"[^\"]*/media/media/|\"media/|g" "$md_file" && rm -f "${md_file}.bak"
    # 3. 如果 media 目录为空则删除
    if [[ -d "$media_out" ]]; then
      rmdir "$media_out" 2>/dev/null || true
    fi
    count=$((count + 1))
  else
    failed=$((failed + 1))
    echo "Failed: $docx_file (see $log_file)" >&2
  fi
done < <(find "$BASE_DIR" -path "*/Original Documents/*.docx" -type f -print0)

echo "Done. success=$count, skipped=$skipped, failed=$failed"
