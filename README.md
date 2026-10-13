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
它只认文章用到的 Markdown 子集（## 和 ### 标题、段落、管道表格、单层列表、链接），遇到不认识的写法会报错退出，
而不是悄悄生成一个和 pandoc 不一样的页面；每张配图没放进页面也会报错。
包里的 HTML 和 docx 就是这两条命令生成的（HTML 重新生成后逐字节一致；docx 内容一致，只有 docProps/core.xml 里的生成时间不同）。

## 发布步骤

1. 在能访问 fashionme.com 的电脑上运行（应用密码放环境变量或等脚本提示输入，不要写在命令行里）：
   ```
   pip install requests
   export WP_APP_PASSWORD="应用密码"
   python3 wp_media_upload.py --site https://www.fashionme.com --user 登录名 \
     --html overlock-seams-that-stop-fraying.html \
     --out overlock-seams-that-stop-fraying.local.html
   ```
   脚本可以重复运行：媒体库里已有同名文件会直接复用，输出文件每传一张就写一次，中途失败不会丢进度。
   不想跑脚本就按 images-to-upload.md 手动下载、上传、替换 5 个 src。
2. 后台新建文章，标题 Overlock Seams That Stop Fraying，slug `overlock-seams-that-stop-fraying`。
3. 像 What Is Private Label Apparel? 那篇一样，在 Elementor 里放一个 HTML 小组件，把 `.local.html` 整个文件内容贴进去。
4. 把 HTML 里 `<meta name="description">` 那句话（156 字符）填进文章的 SEO 描述或摘要字段：贴在小组件里的 meta 标签会落在页面 body 里，WordPress 不会拿它当页面描述。
5. 10 张图都已逐张看过，内容与 alt 相符；发布前在页面上看一眼"配图"一节提到的两张非 3:2 的图裁切得是否满意。
6. 用过的应用密码在 用户 > 个人资料 > 应用密码 里撤销。

## 套版时对版型做的几处适配

- 容器 id 由 `fm-private-label` 改为 `fm-overlock-seams`（CSS 与 HTML 同步）。
- 版型没有 h3，加了一条 `#fm-overlock-seams h3` 规则（21px，字体和字重同 h1/h2，上下间距、行高和字距另设），打印样式里 h3 和 h2 一样不与后文分页。
- 文章里的列表改成段落：方法类用加粗首句，步骤类用短段。
- 正文的撇号和引号按版型正文的排法转成弯引号（’ “ ”）；Markdown 原稿保持直引号，pandoc 生成 docx 时自己会转。
- 每张图都带原图的 width/height（版型的做法）；meta description 控制在 160 字符以内。

## 配图

已在站点媒体库里的 5 张（直接引用原 URL）：
- fm-frayed-raw-edge-on-satin-fabric-b6a473141e.jpg（散边一节）
- fm-fine-silk-fabric-under-a-sewing-machine-presser-foot-53d0f6451c.webp（三线四线）
- fm-seam-being-pulled-to-show-slippage-beside-the-stitch-line-41ca44b6cc.jpg（滑移。注意：这张是 404×720 的竖版视频截图，顶部有 "Seam Slippage" 字样；页面按 3:2 居中裁切后字会被裁掉，但图要放大约 2 倍，会偏糊，有更清晰的滑移照片就换掉）
- Garment-Wash-Test-Reference.jpg（洗样）
- Sewing-Seam-Close-Up.jpg（没有包缝机一节）

来自 Pexels 的 5 张（免费商用，无需署名）：
- 首图 Cristian Rojas / Los Muertos Crew，pexels.com/photo/7998331
- 原理一节 Whittington，pexels.com/photo/38561617
- 设置一节 Ron Lach，pexels.com/photo/9850425（原图是竖图 4052×6078，页面按 3:2 居中裁切后只露出旋钮，alt 相应写成 Tension dials on an overlocker seen from above）
- 线一节 Anete Lusina（竖图），pexels.com/photo/7256903
- 修补一节 Rodolfo Gaion，pexels.com/photo/32641558

## 文章里引用的来源

- AMANN Knowledge Hub：overedging 参数页、seam slippage 页
- Juki MO-4S 说明书（manualslib，卷边张力和左右针的咬边宽度都在网站第 49 页，即印刷页码 48；第 43 页只有刀宽的调节方法和 1 到 4 mm 的针距范围）
- Just Style, Seams in Good Condition (1999)，SGS 柔顺剂研究（全文在付费墙后，文中只保留能核实的平纹、缎纹和斜纹数字）
- Katrina Walker, Tips for troubleshooting serger issues, C&T Publishing (2024)
- YLI Threads, Cathy's woolly nylon serging tips
- Threads 论坛 Seams coming apart (2005)
- ISO 4915（线迹分类）、ISO 13936-1（缝口滑移试验，张开 6 mm）、ASTM D1683（缝口失效分类）：正文里 "the catalogues"、"labs"、"seam testing in the trade" 指的就是这三个标准

## 2026-10-13 校对后的改动

对照来源逐条核对过文章（AMANN 两页、Juki 说明书、C&T、YLI、Threads 论坛的每个细节都对得上），改了下面这些：

- 文字错误：Away from the needle 一节的 "cut the pieces 3 mm wide" 改为 "3 mm wider"；"let the right thread catch" 改为 "the wrong thread"；"both loopers is the better trade" 补了 "using"；去掉一句里重复的 "in several places"。
- 内部矛盾：rayon challis 的针距在表格里原为 2.0–2.5 mm，正文说降到 2.0 mm，表格改为 2.0 mm；卷边针距原为 1.0–1.5 mm，与文中引用的 MO-4S 数字 1.5–2 不接，改为 1.0–2.0 mm；MO-4S 卷边张力那句的连字符改为 en dash 并补上 mm。
- 用词：表格里的 "fabric softener" 改为英式的 "fabric conditioner"；按写作约定在开头把 serger 作为同义词提一次，"serger seam hook" 改为 "overlocker seam hook"。
- 来源：SGS 研究那句去掉未能核实的 jacquard 数字和 "once"；来源列表加上三个标准，并注明 Just Style 需订阅。
- 表格下面补了一句说明数值是来源给的起始值、不是实测。
- Seam slippage 一节 "What helps" 的五条每条都给了短首句，页面上五条都能加粗首句（原来只有两条）。
- stats.py 原来按不存在的标题 "Sources and further reading" 截取正文，导致来源列表也计入字数；已改。
- 调研笔记里与文章不符的几处（字数、节名、"第 1 节的表"、"表下已注明"、serger 约定、YLI 的表述）已改成与文章一致，并修好了第 20 行一处损坏的字节（"缝口失效"）。
