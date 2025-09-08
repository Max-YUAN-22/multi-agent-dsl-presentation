import matplotlib.pyplot as plt
import matplotlib.patches as patches

def main():
    # ---------------------- 全局样式（科研论文级） ----------------------
    BLUE = "#007bff"       # 主色调（科技蓝，顶刊审美）
    TEXT_BLACK = "#343a40" # 文字色（深灰，印刷清晰）
    WHITE = "#f8f9fa"      # 模块背景（浅灰，柔和不刺眼）
    FONT = "Arial"         # 无衬线字体（国际期刊通用）

    # ---------------------- 画布与调试辅助（可注释掉调试代码） ----------------------
    fig, ax = plt.subplots(figsize=(36, 22))  # 16:9 宽屏，留足排版空间
    ax.set_xlim(0, 36)
    ax.set_ylim(0, 22)
    ax.axis("off")  # 隐藏坐标轴

    # --- 【调试用】绘制网格（方便对齐，最终可注释） ---
    # for x in range(0, 37, 2):
    #     ax.axvline(x, color="#eee", linestyle="--", zorder=0)
    # for y in range(0, 23, 2):
    #     ax.axhline(y, color="#eee", linestyle="--", zorder=0)

    # ---------------------- 核心辅助函数：绘制带圆角模块 ----------------------
    def draw_box(xy, width, height, title, title_fontsize=22, box_class="backend"):
        edge_color = TEXT_BLACK
        face_color = WHITE
        linewidth = 4.0

        # 核心模块（DSL/Event Bus/Frontend）用蓝色强调
        if box_class in ["dsl", "eventbus", "frontend"]:
            edge_color = BLUE
            linewidth = 4.5

        # 绘制圆角矩形（rounding_size控制圆角弧度）
        box = patches.FancyBboxPatch(
            xy, width, height,
            boxstyle="round,pad=1.0,rounding_size=0.1",
            linewidth=linewidth,
            edgecolor=edge_color,
            facecolor=face_color,
            zorder=5  # 模块在箭头上方，避免被箭头遮挡
        )
        ax.add_patch(box)

        # 文字居中且自动换行（按\n分割）
        lines = title.split("\n")
        line_height = height / len(lines)
        for i, line in enumerate(lines):
            ax.text(
                xy[0] + width/2,
                xy[1] + height - (i + 0.5) * line_height,
                line,
                ha="center", va="center",
                fontsize=title_fontsize if i == 0 else title_fontsize-2,  # 标题稍大，内容稍小
                fontfamily=FONT,
                color=TEXT_BLACK,
                weight="bold" if i == 0 else "normal",
                zorder=10
            )

    # ---------------------- 辅助函数：绘制单向箭头 ----------------------
    def draw_arrow(start, end, label="", arrow_shrink=40):
        ax.annotate(
            label,
            xy=end,
            xytext=start,
            arrowprops=dict(
                arrowstyle="->",
                color=TEXT_BLACK,
                linewidth=4.0,
                shrinkA=arrow_shrink,
                shrinkB=arrow_shrink,
                zorder=3  # 箭头在模块下方，避免遮挡文字
            ),
            ha="center",
            va="center",
            fontsize=20,
            fontfamily=FONT,
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=1)
        )

    # ---------------------- 辅助函数：绘制双向箭头 ----------------------
    def draw_bidir_arrow(pt1, pt2, label=""):
        ax.annotate(
            "",
            xy=pt1,
            xytext=pt2,
            arrowprops=dict(
                arrowstyle="<->",
                color=TEXT_BLACK,
                linewidth=4.0,
                shrinkA=40,
                shrinkB=40,
                zorder=3
            )
        )
        if label:
            mid_x = (pt1[0] + pt2[0]) / 2
            mid_y = (pt1[1] + pt2[1]) / 2 + 0.7
            ax.text(
                mid_x, mid_y,
                label,
                ha="center",
                va="bottom",
                fontsize=20,
                fontfamily=FONT,
                bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=1),
                zorder=10
            )

    # ---------------------- 绘制“层标题”与“分隔线”（明确垂直分层） ----------------------
    # DSL Layer
    ax.text(
        1, 20.5, "DSL Layer",
        fontsize=26, fontfamily=FONT,
        color="#333", weight="bold",
        ha="left", va="center"
    )
    ax.plot([2, 34], [18.0, 18.0], color="#ccc", linewidth=4.5, zorder=1)

    # Backend Layer
    ax.text(
        1, 14.5, "Backend Layer",
        fontsize=26, fontfamily=FONT,
        color="#333", weight="bold",
        ha="left", va="center"
    )
    ax.plot([2, 34], [12.0, 12.0], color="#ccc", linewidth=4.5, zorder=1)

    # Execution Layer
    ax.text(
        1, 7.5, "Execution Layer",
        fontsize=26, fontfamily=FONT,
        color="#333", weight="bold",
        ha="left", va="center"
    )
    ax.plot([2, 34], [5.0, 5.0], color="#ccc", linewidth=4.5, zorder=1)

    # ---------------------- 绘制“DSL Layer”模块（最上层，无重叠） ----------------------
    draw_box(
        xy=(4, 19),
        width=25,
        height=3,
        title="Declarative Logic / Workflows\n"
              "- Declarative Rule Authoring\n"
              "- Workflow Template Management\n"
              "- Rule Validation & Optimization",
        title_fontsize=20,
        box_class="dsl"
    )

    # ---------------------- 绘制“Backend Layer”模块（中间层，三模块等距） ----------------------
    backend_w = 6.0   # 单个模块宽度
    backend_h = 3.5   # 单个模块高度
    backend_y = 13.0  # 垂直位置（与上层分隔线间距1.0）
    backend_gap = 5.0 # 模块间水平间隙（确保不重叠）

    # API Gateway
    draw_box(
        xy=(4, backend_y),
        width=backend_w,
        height=backend_h,
        title="API Gateway\n- Interface Adaptation",
        title_fontsize=18
    )

    # Orchestration
    draw_box(
        xy=(4 + backend_w + backend_gap, backend_y),
        width=backend_w,
        height=backend_h,
        title="Orchestration\n- Task Composition",
        title_fontsize=18
    )

    # State Management
    draw_box(
        xy=(4 + 2*backend_w + 2*backend_gap, backend_y),
        width=backend_w,
        height=backend_h,
        title="State Management\n- Execution State Storage",
        title_fontsize=18
    )

    # ---------------------- 绘制“Execution Layer”模块（最下层，三模块等距） ----------------------
    exec_w = 6.0   # 单个模块宽度
    exec_h = 3.5   # 单个模块高度
    exec_y = 6.0   # 垂直位置（与上层分隔线间距1.0）
    exec_gap = 5.0 # 模块间水平间隙

    # Event Bus（核心，蓝色边框）
    draw_box(
        xy=(4, exec_y),
        width=exec_w,
        height=exec_h,
        title="Event Bus\n- Event Publishing\n- Message Routing\n- Subscription Management",
        title_fontsize=18,
        box_class="eventbus"
    )

    # Agent Manager
    draw_box(
        xy=(4 + exec_w + exec_gap, exec_y),
        width=exec_w,
        height=exec_h,
        title="Agent Manager\n- Agent Registration\n- Dynamic Scheduling",
        title_fontsize=18
    )

    # Agent Pool
    draw_box(
        xy=(4 + 2*exec_w + 2*exec_gap, exec_y),
        width=exec_w,
        height=exec_h,
        title="Agent Pool\n- Traffic Agent\n- Safety Agent\n- Perception Agent\n- Dispatch Agent",
        title_fontsize=16
    )

    # ---------------------- 绘制“Frontend Layer”模块（右侧独立，无重叠） ----------------------
    draw_box(
        xy=(30.0, 7.0),
        width=5.5,
        height=11.0,
        title="Frontend\n- React UI (Visualization)\n- WebSocket (Real-time Feedback)\n- Log/Alert Dashboard",
        title_fontsize=20,
        box_class="frontend"
    )

    # ---------------------- 绘制“模块间箭头”（精准坐标，彻底避免交叉） ----------------------
    # 1. DSL → Orchestration（指令下传，垂直对齐）
    draw_arrow(
        start=(4 + 25/2, 19 + 3),      # DSL层下沿正中心
        end=(4 + backend_w + backend_gap + backend_w/2, backend_y + backend_h),  # Orchestration上沿正中心
        arrow_shrink=50
    )

    # 2. Orchestration → Agent Manager（任务分发，垂直对齐）
    draw_arrow(
        start=(4 + backend_w + backend_gap + backend_w/2, backend_y),  # Orchestration下沿正中心
        end=(4 + exec_w + exec_gap + exec_w/2, exec_y + exec_h),      # Agent Manager上沿正中心
        arrow_shrink=50
    )

    # 3. API Gateway → Event Bus（接口与事件层通信，垂直对齐）
    draw_arrow(
        start=(4 + backend_w/2, backend_y),  # API Gateway下沿正中心
        end=(4 + exec_w/2, exec_y + exec_h),  # Event Bus上沿正中心
        arrow_shrink=50
    )

    # 4. Event Bus ↔ Agent Manager（事件双向同步，水平对齐）
    draw_bidir_arrow(
        pt1=(4 + exec_w, exec_y + exec_h/2),        # Event Bus右侧正中心
        pt2=(4 + exec_w + exec_gap, exec_y + exec_h/2),  # Agent Manager左侧正中心
        label="Event Sync"
    )

    # 5. Agent Manager ↔ Agent Pool（智能体生命周期管理，水平对齐）
    draw_bidir_arrow(
        pt1=(4 + exec_w + exec_gap + exec_w, exec_y + exec_h/2),  # Agent Manager右侧正中心
        pt2=(4 + 2*exec_w + 2*exec_gap, exec_y + exec_h/2),        # Agent Pool左侧正中心
        label="Agent Lifecycle"
    )

    # 6. State Management ↔ Frontend（状态数据交互，斜线避让）
    draw_bidir_arrow(
        pt1=(4 + 2*backend_w + 2*backend_gap + backend_w, backend_y + backend_h/2),  # State Management右侧正中心
        pt2=(30.0, 7.0 + 11.0*0.7),  # Frontend左侧上1/3处（避开其他箭头）
        label="REST/GraphQL"
    )

    # 7. Agent Pool → State Management（执行状态上报，垂直对齐）
    draw_arrow(
        start=(4 + 2*exec_w + 2*exec_gap + exec_w/2, exec_y + exec_h),  # Agent Pool上沿正中心
        end=(4 + 2*backend_w + 2*backend_gap + backend_w/2, backend_y),  # State Management下沿正中心
        label="Status Reporting",
        arrow_shrink=50
    )

    # 8. Event Bus → Frontend（实时事件推送，斜线避让）
    draw_arrow(
        start=(4 + exec_w, exec_y + exec_h),  # Event Bus右上角
        end=(30.0, 7.0 + 11.0*0.3),  # Frontend左侧下1/3处（避开其他箭头）
        label="Real-time Events",
        arrow_shrink=50
    )

    # 9. Frontend → Orchestration（用户操作指令，垂直对齐）
    draw_arrow(
        start=(30.0 + 5.5/2, 7.0 + 11.0),  # Frontend上沿正中心
        end=(4 + backend_w + backend_gap + backend_w/2, backend_y + backend_h),  # Orchestration上沿正中心
        label="User Actions",
        arrow_shrink=50
    )

    # ---------------------- 总标题（顶刊级字号与位置） ----------------------
    fig.suptitle(
        "System Architecture Overview of DSL-based Multi-Agent System",
        fontsize=50,
        fontfamily=FONT,
        weight="bold",
        y=0.98  # 靠近顶部，不挤压内容
    )

    # ---------------------- 导出（论文交付双格式：SVG+PNG） ----------------------
    # SVG（矢量，期刊排版首选，无限缩放）
    svg_path = "system_architecture_final.svg"
    plt.savefig(
        svg_path,
        format="svg",
        bbox_inches="tight",  # 自动裁剪多余空白
        pad_inches=2.5,       # 四周留白（适配论文边距）
        dpi=300               # 隐式高清（SVG本身为矢量，此参数不影响矢量性，仅兼容PNG）
    )

    # PNG（300dpi，印刷级分辨率，兼容常规文档）
    png_path = "system_architecture_final.png"
    plt.savefig(
        png_path,
        format="png",
        bbox_inches="tight",
        pad_inches=2.5,
        dpi=300
    )

    print(f"✅ 论文级图示已导出：\n- SVG: {svg_path}\n- PNG: {png_path}")

if __name__ == "__main__":
    main()