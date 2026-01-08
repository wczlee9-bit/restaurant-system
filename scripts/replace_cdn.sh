#!/bin/bash

echo "======================================"
echo "🔄 批量替换 CDN 脚本"
echo "======================================"
echo ""

# 查找所有使用 jsdelivr 的 HTML 文件
echo "📋 查找需要替换的文件..."
echo ""

FILES=$(find assets -name "*.html" -type f -exec grep -l "cdn.jsdelivr.net" {} \;)

if [ -z "$FILES" ]; then
    echo "✅ 没有需要替换的文件"
    exit 0
fi

echo "找到以下文件："
echo "$FILES"
echo ""

read -p "是否继续替换？(y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "正在替换..."
echo ""

for file in $FILES; do
    echo "处理: $file"
    
    # 创建备份
    cp "$file" "$file.bak"
    
    # 替换 jsdelivr CDN 为 unpkg CDN
    sed -i 's|cdn\.jsdelivr\.net/npm/vue@3|unpkg.com/vue@3|g' "$file"
    sed -i 's|cdn\.jsdelivr\.net/npm/element-plus|unpkg.com/element-plus|g' "$file"
    sed -i 's|cdn\.jsdelivr\.net/npm/axios|unpkg.com/axios|g' "$file"
    
    echo "  ✅ 完成"
done

echo ""
echo "======================================"
echo "✅ 替换完成"
echo "======================================"
echo ""
echo "📊 统计信息："
echo "  处理文件数: $(echo "$FILES" | wc -l)"
echo ""
echo "📦 备份文件位置："
find assets -name "*.html.bak" -type f
echo ""
echo "如需恢复，请使用备份文件"
echo ""
