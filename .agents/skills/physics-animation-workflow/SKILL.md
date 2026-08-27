---
name: physics-animation-workflow
description: Convert physics problems into interactive HTML Canvas animations that show motion processes, trajectories, fields, and mechanics or electromagnetism scenarios through coordinated vector diagrams and physical calculations.
metadata:
  source_dir: physics-animation-workflow-1.0.0
  version: "1.0.0"
  author: 云爪 (wxdwqy)
  contact: wxdwqy@163.com
---

# 物理动画制作工作流（Physics Animation Workflow）

## 概述

将物理问题的运动过程制作成交互式动画，全程分 10 步完成（5步矢量化 + 5步动画化）。本技能强调矢量图与物理计算的**相互依赖关系**：
- **矢量图**确定整体框架：坐标系、场域划分、轨迹形状特征
- **物理计算**确定细节：速度、位移、时间、精确轨迹

两者缺一不可，顺序视题目情况而定。

## 何时使用

✅ **适用场景**：
- 物理题目需要展示运动过程动画
- 需要精确还原轨迹的电磁学问题
- 需要分阶段展示的复杂运动

❌ **不适用场景**：
- 只需静态示意图 → 用 bitmap-vectorize
- 纯文字推导，无需图形 → 直接文字回答

## 流程概览

```
物理示意图 → 矢量化 → 动画化 → 发布
     ↓           ↓         ↓        ↓
   (步骤1-5)  (步骤6-10)
```

---

## 第一阶段：矢量化

### Step 1: 识别元素组件

**输入**：物理示意图（截屏/扫描/手绘）

**任务**：
- 识别物品名称（小球、物块、弹簧、斜面、带电粒子等）
- 识别场域（电场、磁场、重力场等）
- 分析位置布局
- 理解相互关系

**输出**：元素清单 + 位置关系描述

---

### Step 2: 客户交互校对

**任务**：
- 展示识别结果
- 与客户交互完成物理问题文字部分校对
- ⚠️ 注意：只校对识图结果，不解题

**输出**：确认的元素清单

---

### Step 3: 建立坐标系和比例尺

**任务**：
- 确定画布尺寸
- 设置原点位置
- 定义比例：1单位 = ? 像素
- 确定场域边界（电场/磁场分界线等）

**输出**：坐标系参数

---

### Step 4: 生成矢量图形

**任务**：
- 用 HTML Canvas 绘制矢量图
- 检查物品、位置、关系三者与原图一致
- 绘制场域标注（E 场向下箭头、B 场 ⊙ 符号等）

**输出**：HTML Canvas 矢量图代码

---

### Step 5: 校对矢量图

**任务**：
- 检查背景
- 检查物体形状大小
- 检查颜色
- 检查中英文标注
- 与客户交互完成最终确认

**输出**：确认的矢量图文件

---

## 第二阶段：动画化

### Step 6: 描述运动过程 / 物理建模

**任务**：
- 根据物理条件和规律描述物体可能如何运动
- 复杂运动按时间顺序分为几个阶段描述
- 客户分阶段校对运动过程

**输出**：运动过程文字描述

---

### Step 7: 生成初级动画

**任务**：
- 生成反映物体运动的初级动画
- 复杂运动按时间顺序分为几个阶段生成
- 物体速率可基本不变
- 基本实现运动过程
- 客户确认后进行下一步

**输出**：初级动画文件

---

### Step 8: 加入真实物理计算（可选）

**任务**：
- 根据物理条件、物理规律在初级动画基础上加入运动速度和轨迹的计算结果
- 生成反映物体真实运动的动画
- 复杂运动分阶段逐步生成

**⚠️ 注意**：对于只需定性描述运动过程的问题，此步可跳过。是否需要精确计算取决于题目要求。

**输出**：物理精确动画文件

---

### Step 9: 最终校对

**任务**：客户确认最终动画效果

**输出**：确认的最终动画

---

### Step 10: 发布输出

**任务**：
- 按客户要求发布成所需的格式
- 默认输出 HTML Canvas（单文件，可直接浏览器打开）

**输出**：最终交付文件

---

## ⚠️ 重要注意事项

### 坐标系差异

| 项目 | Canvas默认 | 数学物理 |
|------|-----------|----------|
| Y轴方向 | 向下（y增大=向下）| 向上（y增大=向上）|
| 角度0°方向 | 右侧（3点钟）| 右侧（3点钟）|
| 角度正方向 | **顺时针** | **逆时针** |

### 转换公式

```javascript
// 数学物理坐标 → Canvas坐标
canvas_y = height - physics_y;

// 数学物理角度 → Canvas角度
canvas_angle = -physics_angle;  // 或 2π - physics_angle
```

### 矢量图与计算的关系

| 题目类型 | 推荐顺序 |
|---------|---------|
| 有标准答案的定量计算题 | 先画矢量图确定框架，再靠计算确定轨迹细节 |
| 无标准答案的定性分析题 | 先通过物理计算推导，再画矢量图 |
| 只需描述运动过程的简单问题 | 跳过物理计算步骤 |

---

## 核心原则

1. **交互式流程**：每个步骤完成后与客户确认再进行下一步
2. **分阶段复杂运动**：复杂动画按时间顺序分阶段逐步生成
3. **默认输出**：HTML Canvas 格式（单文件，易于分享）
4. **矢量图与计算互补**：两者相互依赖，顺序视题目而定

## 作者与联系

- **作者**：云爪
- **联系邮箱**：wxdwqy@163.com
- 如有问题或建议，欢迎反馈！

---

# Physics Animation Workflow (English)

## Overview

Create interactive HTML Canvas animations for physics problems through a 10-step workflow (5 vectorization + 5 animation steps).

## When to Use

✅ **Appropriate**:
- Physics problems requiring motion animation
- Electromagnetic problems needing precise trajectory
- Complex motion with multiple stages

❌ **Not appropriate**:
- Static diagrams only → use bitmap-vectorize
- Text-only problems → answer directly

## Core Principle

Vector graphics and physics calculations are **mutually dependent**:
- Vector diagram establishes the framework
- Physics calculations determine the details

## 10-Step Workflow

### Phase 1: Vectorization (Steps 1-5)
1. Identify elements
2. Client verification
3. Establish coordinate system
4. Generate vector graphics
5. Verify vector diagram

### Phase 2: Animation (Steps 6-10)
6. Describe motion / Physics modeling
7. Generate primary animation
8. Add physics calculations (optional)
9. Final verification
10. Publish output

## Key Differences

| Item | Canvas Default | Math/Physics |
|------|----------------|--------------|
| Y-axis direction | Downward | Upward |
| Angle positive | **Clockwise** | Counter-clockwise |
