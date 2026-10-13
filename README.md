# Overlock Seams That Stop Fraying — 交付包

## 文件

| 文件 | 是什么 |
| --- | --- |
| overlock-seams-that-stop-fraying.md | 最终文章，Markdown 原稿（约 4,150 词正文，英式拼写） |
| overlock-seams-that-stop-fraying.docx | 同一篇文章的 Word 版 |
| overlock-seams-that-stop-fraying.html | 套进站点版型的成品页，含 10 张配图，可整个贴进 Elementor 的 HTML 小组件 |
| template-what-is-private-label-apparel.html | 你提供的版型原件（未改动） |
| images-to-upload.md | 需要下载到媒体库的 5 张图：下载地址、上传文件名、alt、要替换的 src |
| wp_media_upload.py | 自动完成上一条：下载 5 张图、上传媒体库、写 alt、生成 src 已换成本地地址的 HTML |
| build_html.py | 由 Markdown 生成套版 HTML 的脚本（改了 Markdown 再跑一次即可重新生成） |
| stats.py | 写作时用的检查脚本：字数、引号、短横线、数字范围写法、句长分布 |
| 调研笔记.md | 写作前的调研：竞品对比、文献用在哪、写作约定、信息增益清单 |

## 改了 Markdown 之后怎么重新生成

Markdown 是唯一的源文件，HTML 和 Word 都由它生成；改完原稿后在本目录运行：

```
python3 build_html.py                      # Markdown + 版型 → overlock-seams-that-stop-fraying.html
pandoc overlock-seams-that-stop-fraying.md -o overlock-seams-that-stop-fraying.docx   # Markdown → Word
python3 stats.py                           # 字数、引号、短横线等检查
```

`build_html.py` 默认读写脚本旁边的文件，也可以用 `--src`、`--template`、`--out` 指定路径。
包里的 HTML 和 docx 就是这两条命令生成的（已核对：重新生成的结果与包里的文件逐字节一致）。

## 发布步骤

1. 在能访问 fashionme.com 的电脑上运行：
   ```
   pip install requests
   python3 wp_media_upload.py --site https://www.fashionme.com --user 登录名 \
     --password "应用密码" \
     --html overlock-seams-that-stop-fraying.html \
     --out overlock-seams-that-stop-fraying.local.html
   ```
   不想跑脚本就按 images-to-upload.md 手动下载、上传、替换 5 个 src。
2. 后台新建文章，标题 Overlock Seams That Stop Fraying，slug `overlock-seams-that-stop-fraying`。
3. 像 What Is Private Label Apparel? 那篇一样，在 Elementor 里放一个 HTML 小组件，把 `.local.html` 整个文件内容贴进去。
4. 发布前把 5 张 Pexels 图过一眼（选图时按图片描述选的，没有亲眼看过像素）。
5. 用过的应用密码在 用户 > 个人资料 > 应用密码 里撤销。

## 套版时对版型做的三处适配

- 容器 id 由 `fm-private-label` 改为 `fm-overlock-seams`（CSS 与 HTML 同步）。
- 版型没有 h3，加了一条 `#fm-overlock-seams h3` 规则（21px，其余同 h2）。
- 文章里的列表改成段落：方法类用加粗首句，步骤类用短段。

## 配图

已在站点媒体库里的 5 张（直接引用原 URL）：
- fm-frayed-raw-edge-on-satin-fabric-b6a473141e.jpg（散边一节）
- fm-fine-silk-fabric-under-a-sewing-machine-presser-foot-53d0f6451c.webp（三线四线）
- fm-seam-being-pulled-to-show-slippage-beside-the-stitch-line-41ca44b6cc.jpg（滑移）
- Garment-Wash-Test-Reference.jpg（洗样）
- Sewing-Seam-Close-Up.jpg（没有包缝机一节）

来自 Pexels 的 5 张（免费商用，无需署名）：
- 首图 Cristian Rojas / Los Muertos Crew，pexels.com/photo/7998331
- 原理一节 Whittington，pexels.com/photo/38561617
- 设置一节 Ron Lach，pexels.com/photo/9850425
- 线一节 Anete Lusina（竖图），pexels.com/photo/7256903
- 修补一节 Rodolfo Gaion，pexels.com/photo/32641558

## 文章里引用的来源

- AMANN Knowledge Hub：overedging 参数页、seam slippage 页
- Juki MO-4S 说明书（manualslib，卷边张力在网站第 49 页，宽度在第 43 页）
- Just Style, Seams in Good Condition (1999)，SGS 柔顺剂研究
- Katrina Walker, Tips for troubleshooting serger issues, C&T Publishing (2024)
- YLI Threads, Cathy's woolly nylon serging tips
- Threads 论坛 Seams coming apart (2005)
