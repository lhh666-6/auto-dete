# Related Work 文献综述

**论文主题**：半自动工业纸质表单数字化系统（生成带二维码/ArUco 标记的纸质模板 → 拍照导入 → 模板识别 + 透视校正 + 字段裁切 → 数字模板匹配与 OMR 勾选识别（带置信度与歧义带）→ 人工审核工作台 → 不可变版本与审计 → XLSX 导出；可选 LLM（DeepSeek）只读建议适配器、本地向量相似检索、PWA 离线移动提交）

> **检索与真实性说明**：以下全部条目来自 web_search 实际命中结果，所列 arXiv 号 / DOI 均为检索结果中出现的编号，未杜撰。凡作者全名、发表年份、DOI 等无法从命中结果确证的，均已标注「待核实」。文献条目保留英文原名，评述正文为中文。

---

## 1. 文档 / 表单 OCR 与版面分析

### 1.1 PP-OCRv3: More Attempts for the Improvement of Ultra Lightweight OCR System
- **作者**：Yuning Du 等（Du et al.）
- **年份**：2022
- **来源**：arXiv:2206.03001
- **与本系统差异**：PP-OCRv3 是面向中英文通用场景的端侧超轻量 OCR 流水线，目标是文本检出/识别的精度与推理速度；本系统的 OCR 只是"字段级候选"之一，且依赖二维码/ArUco 标记与数字模板先验保证几何对齐，而非纯图像端到端识别。

### 1.2 LayoutLMv3: Pre-training for Document AI with Unified Text and Image Masking
- **作者**：Yupan Huang, Tengchao Lv, Lei Cui, Yutong Lu, Furu Wei
- **年份**：2022
- **来源**：ACM MM 2022；arXiv:2204.08387
- **与本系统差异**：LayoutLMv3 通过文本+图像+布局的统一掩码做大规模多模态预训练，服务通用文档抽取/VQA；本系统无需预训练大模型，而是以标记几何锚点 + 数字模板匹配为主，机器输出为带置信度与歧义带的可审计候选，而非端到端直接抽取。

### 1.3 Donut: OCR-free Document Understanding Transformer
- **作者**：Geewook Kim 等（Kim et al.）
- **年份**：2022
- **来源**：ECCV 2022；arXiv:2111.15664
- **与本系统差异**：Donut 主张"去 OCR"的端到端文档理解，用统一 Transformer 直接生成结构化输出；本系统刻意保留显式 OCR + OMR + 几何校正的中间表示，以支撑人工审核与审计，避免黑盒生成难以追溯的问题。

> **本系统定位**：通用 OCR / 文档 AI 路线追求"更准的端到端抽取"，把机器输出当作最终结果；本系统则把 OCR 降格为受控候选源，通过"模板 + 标记 + 透视校正"的几何闭环约束识别空间，并把不确定性显式化（置信度 + 歧义带）交给后续人工裁决。

---

## 2. 光学标记识别（OMR）与表单处理系统

### 2.1 Optical Mark Recognition Techniques for Multiple-Choice Tests: A Comprehensive Review
- **作者**：Ali、Hammoud（作者待核实）
- **年份**：2024（待核实）
- **来源**：IEEE Access（DOI 待核实；IEEE Explore 文档号 11129039）
- **与本系统差异**：该综述聚焦选择题答题卡的 OMR 评估流水线（表格定位、灰度阈值、答案判定），以确定性判定为主；本系统面向工业表单的"勾选 + 手写/打印填写"混合字段，OMR 输出为带置信度的候选标记并进入歧义带，而非一次性硬判定。

### 2.2 SurveyNet: A Unified Deep Learning Framework for OCR and OMR-Based Survey Digitization
- **作者**：Quiñones、Gultepe 等（作者待核实）
- **年份**：2026
- **来源**：Journal of Imaging, 12(4):175；DOI 10.3390/jimaging12040175
- **与本系统差异**：SurveyNet 用统一深度模型同时做问卷的 OCR + OMR 数字化，目标为通用问卷；本系统强调"生成带标记模板 → 拍照 → 模板匹配"的闭环，以获得字段级对齐与全链路可追溯，并以人工审核工作台 + 不可变审计收口，而非纯模型自动化。

### 2.3 Various Techniques for Assessment of OMR Sheets through Ordinary 2D Scanner: A Survey
- **作者**：Patel、Prajapati（作者待核实）
- **年份**：待核实
- **来源**：待核实（Semantic Scholar 收录）
- **与本系统差异**：综述对象是基于普通平板扫描仪的传统 OMR 评估；本系统面向手机/现场拍照的非受控成像（倾斜、透视、光照），需先做透视校正再 OMR，且强调移动端离线提交。

> **本系统定位**：传统 OMR 是"确定性判读"的单点工具，近年工作走向"统一模型自动数字化"；本系统取其中间态——机器给出带置信度的候选与显式歧义带，把低置信/歧义项定向路由给人工审核，而非要么全自动、要么全人工。

---

## 3. 基于基准标记（fiducial marker：QR/ArUco）的定位与透视校正

### 3.1 Speeded Up Detection of Squared Fiducial Markers
- **作者**：Francisco J. Romero-Ramirez, Rafael Muñoz-Salinas, Rafael Medina-Carnicer
- **年份**：2018
- **来源**：Image and Vision Computing, 76:38–47；DOI 10.1016/j.imavis.2018.05.004
- **与本系统差异**：该文提出 ArUco 方形基准标记的快速检测（自适应阈值 + 轮廓 + 位姿估计），是通用定位组件；本系统把 ArUco 作为表单模板识别与透视校正的几何锚点，并与数字模板匹配、字段裁切链路耦合，服务于表单数字化而非通用 AR 位姿估计。

### 3.2 Generation of Fiducial Marker Dictionaries Using Mixed Integer Linear Programming
- **作者**：S. Garrido-Jurado, R. Muñoz-Salinas, F. J. Madrid-Cuevas, R. Medina-Carnicer
- **年份**：2016
- **来源**：Pattern Recognition, 51:481–491；DOI 10.1016/j.patcog.2015.09.023
- **与本系统差异**：该文解决标记字典的互最小距离与误检最小化问题；本系统利用其字典鲁棒性保证多模板并存时表单 ID 的可靠区分，但把"标记 → 模板 → 字段"映射作为系统级设计，而非孤立算法。

### 3.3 QR Code Detection with Perspective Correction and Decoding in Real-World Conditions Using Deep Learning and Enhanced Image Processing
- **作者**：Corpuz、Rosario 等（Corpuz et al.）
- **年份**：2025
- **来源**：VISIGRAPP 2025（dblp: conf/visigrapp/CorpuzRCLI25）
- **与本系统差异**：该文面向真实世界 QR 的检测 + 透视校正 + 解码的深度学习方案；本系统的二维码既承载表单/批次元数据、也作为定位标记，透视校正以四角标记单应性完成，并与 OMR/OCR 全链路绑定，而非孤立解码。

> **本系统定位**：基准标记研究多把"检测/字典/位姿"作为独立视觉任务；本系统将其纳入"表单数字化"的生产闭环——标记既是身份（表单 ID）又是几何（透视校正与字段对齐）锚点，从而把后续 OMR/OCR 的搜索空间从整图缩小到精确定位的字段区域。

---

## 4. 人机协同（human-in-the-loop）数字化与审核工作流

### 4.1 A Survey on Active Learning and Human-in-the-Loop Deep Learning for Medical Image Analysis
- **作者**：Samuel Budd, Emma C. Robinson, Bernhard Kainz
- **年份**：2021
- **来源**：Medical Image Analysis, 71:102062；DOI 10.1016/j.media.2021.102062（arXiv:1910.02923）
- **与本系统差异**：该综述系统梳理主动学习与 HITL 范式的标注/训练协同；本系统的人机协同发生在**推理后审核**阶段——机器候选 + 置信度/歧义带驱动人工聚焦，而非训练数据的主动标注循环。

### 4.2 AI-Assisted Digitization of Handwritten Drilling Reports with Human-in-the-Loop Validation
- **作者**：作者待核实
- **年份**：2025
- **来源**：Sixth EAGE Digitalization Conference & Exhibition；DOI 10.3997/2214-4609.202639070
- **与本系统差异**：该文面向油气钻井手写报告的 HITL 数字化，是与本系统工业场景最接近的工作；但本系统强调"生成带标记模板"的主动控制、勾选 OMR 的歧义带，以及不可变版本/审计导出，而非仅手写 OCR 的后校验。

### 4.3 Designing Reliable Enterprise Document AI Pipelines: A Production Framework for Scalable Document Extraction, Validation, and Human-in-the-Loop Governance
- **作者**：作者待核实
- **年份**：待核实
- **来源**：PeerJ（在审/预印本，待核实）
- **与本系统差异**：该文给出企业级文档 AI"抽取 + 校验 + HITL 治理"框架；本系统定位更轻量、聚焦纸质表单半自动数字化，且机器输出恒为候选、由显式歧义带与全链路可追溯支撑人工裁决。

> **本系统定位**：HITL 文献多把"人"当作模型训练纠偏的一环，或提供高层的治理原则；本系统把人工审核固化为**必经收口环节**——低置信与歧义项被定向路由给审核工作台，审核动作连同机器候选、版本号一起进入不可变审计链，形成可复核的证据闭环。

---

## 5. LLM 辅助文档处理 / 离线优先 Web 应用（PWA）

### 5.1 Large Language Models for Generative Information Extraction: A Survey
- **作者**：Derong Xu, Wei Chen, Wenjun Peng, Chao Zhang, Tong Xu, Xiangyu Zhao, Xian Wu, Yefeng Zheng, Enhong Chen
- **年份**：2024
- **来源**：arXiv:2312.17617
- **与本系统差异**：该综述梳理 LLM 生成式信息抽取（IE）范式，主张模型直接产出结构化结果；本系统的 DeepSeek 建议适配器是"**只读候选**"旁路——LLM 输出不直接落库，仅作为人工审核的辅助建议，避免生成式不可控内容进入审计链。

### 5.2 Retrieval Augmented Generation (RAG) and Beyond: A Comprehensive Survey on How to Make Your LLMs Use External Data More Wisely
- **作者**：Wenqi Fan、Yujuan Ding 等（Fan et al.）
- **年份**：2024
- **来源**：arXiv:2409.14924
- **与本系统差异**：该综述聚焦让 LLM 更聪明地使用外部数据的 RAG 范式；本系统用**本地向量相似检索**做历史模板/字段的最近邻匹配与候选推荐，强调离线本地化与数据不出域，而非云端大模型检索生成。

### 5.3 Local-First Software: You Own Your Data, in Spite of the Cloud
- **作者**：Martin Kleppmann, Adam Wiggins, Peter van Hardenberg, Mark McGranaghan
- **年份**：2019
- **来源**：Onward! (SPLASH) 2019；DOI 10.1145/3359591.3359737
- **与本系统差异**：该文提出 local-first 软件的七项理想（本地可用、离线、同步等）；本系统的 PWA 离线移动提交（IndexedDB 本地暂存 + 回传同步）与不可变版本正是 local-first 思想的工程落地，但面向工业表单采集的具体约束。

> **本系统定位**：LLM 文档处理路线倾向"模型生成即结果"，RAG 路线倾向"云端检索增强"；本系统把 LLM 与向量检索都限定在**只读辅助**角色，且核心数据采用 local-first / 离线优先策略，保证现场无网也能提交、数据所有权与可追溯性不依赖云端。

---

## 全局「本系统定位」总结

相较上述五类工作，本系统的核心差异可归纳为四点：

1. **机器输出只是候选，不是结论**：OCR / OMR / LLM 的产出统一视为候选，最终值由人工审核确认，避免"端到端黑盒"直接写入数据。
2. **显式歧义带（ambiguity band）**：对勾选状态、OCR 置信度落入歧义区的项做显式标记与定向路由，使"不确定"本身成为可管理、可审计的对象，而非被阈值硬性抹平。
3. **全链路可追溯与不可变审计**：从带标记模板生成、拍照、识别、审核到 XLSX 导出，每一步都携带版本与操作证据，形成复核闭环（区别于多数仅关注识别精度的系统）。
4. **离线提交与数据主权**：PWA + 本地暂存（IndexedDB）+ 回传同步，使现场在弱网/无网环境下仍可提交，兼顾工业现场约束与 local-first 的数据可控性。

---

*（注：本文件为 Related Work 章节的文献素材稿；正式引用前建议对标注「待核实」的条目补充核对作者全名、年份与 DOI。）*
