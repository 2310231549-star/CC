# CLAUDE.md — CC 项目记忆库

原则：不让用户把时间花在重复的调试上。

## 用户

- 学号 231612147，姓名 张睿 (Zhang Rui)，广东金融学院 金融数学与统计学院 信计1班
- 桌面 `C:\Users\23102\Desktop\`

## 核心规则

**语言**: 对话用中文，代码/命令用英文

**OCR 图片作业**: 非多模态模型无法读图时，cp 到纯英文路径 → easyocr(ch_sim+en, gpu=False) → 保存 homework_text.txt。
关键教训：Git Bash 下中文文件名会被编码损坏，必须先 cp 到英文名。

**作业输出**: 文件命名 `231612147张睿.txt/docx/py`，放桌面。

**路径**: Git Bash 用 `/c/...` Unix 风格；Python 内用 `r'C:\Users\23102\Desktop\'`；中文路径 cp/mv 加引号。

## Skill 管理

好用的 skill → 存 `CC/` → 确认 → 移到 `.claude/skills/<name>/SKILL.md` → 重启生效。

## 工具

easyocr(CPU~3-5min/图), numpy, pandas, matplotlib, scikit-learn, scipy, tensorflow, Pillow

## 作业模板

- **信息加解密**: 凯撒/替换密码 → Ok.txt(密文) + 学号文件(答案)
- **Python/Jupyter**: 参考 `课程/python/` 历史作业，用 NotebookEdit 或 .py
- **文档 .docx**: 命名含 `231612147张睿`

## 清理规则

删临时文件(hw_temp.jpg, homework_text.txt)；保留答案文件和有用脚本。

> 更新: 2026-05-25 — 配置审计优化
