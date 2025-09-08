import matplotlib.pyplot as plt
import matplotlib.patches as patches

def main():
    # --- Style ---
    BLUE = "#007bff"
    TEXT_BLACK = "#343a40"
    WHITE = "#ffffff"
    FONT = "Helvetica"

    # --- Canvas ---
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # --- Helpers ---
    def draw_box(xy, w, h, title, subtitle="", title_fs=12, sub_fs=9):
        box = patches.FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.2,rounding_size=0.05",
                                     linewidth=1.5, edgecolor=BLUE, facecolor=WHITE, zorder=5)
        ax.add_patch(box)
        title_y = xy[1] + h * (0.7 if subtitle else 0.5)
        ax.text(xy[0] + w/2, title_y, title, ha="center", va="center", fontsize=title_fs, fontfamily=FONT, color=TEXT_BLACK, weight='bold', zorder=10)
        if subtitle:
            ax.text(xy[0] + w/2, xy[1] + h * 0.3, subtitle, ha="center", va="center", fontsize=sub_fs, fontfamily=FONT, color=TEXT_BLACK, zorder=10, linespacing=1.3)

    def draw_arrow(start, end, label, va='bottom', ha='center'):
        ax.annotate(label, xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="->", color=TEXT_BLACK, lw=1.5, shrinkA=10, shrinkB=10),
                    ha=ha, va=va, fontsize=9, fontfamily=FONT, zorder=3)

    def draw_bidir_arrow(p1, p2, label=""):
        ax.annotate("", xy=p1, xytext=p2, arrowprops=dict(arrowstyle="<->", color=TEXT_BLACK, lw=1.5, shrinkA=8, shrinkB=8), zorder=3)
        if label:
            mid_point = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2 + 0.2)
            ax.text(mid_point[0], mid_point[1], label, ha='center', va='bottom', fontsize=9, fontfamily=FONT,
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1), zorder=10)

    # --- Layer Containers (using text labels) ---
    ax.text(0.5, 9.5, "DSL Layer", fontsize=14, fontfamily=FONT, color="#555", weight='bold')
    ax.plot([0.5, 15.5], [9.2, 9.2], color='#ddd', lw=1.5)

    ax.text(0.5, 6.5, "Backend Layer", fontsize=14, fontfamily=FONT, color="#555", weight='bold')
    ax.plot([0.5, 15.5], [6.2, 6.2], color='#ddd', lw=1.5)

    ax.text(0.5, 3.5, "Execution Layer", fontsize=14, fontfamily=FONT, color="#555", weight='bold')
    ax.plot([0.5, 15.5], [3.2, 3.2], color='#ddd', lw=1.5)


    # --- Component Boxes ---
    # DSL Layer
    draw_box((1, 7.5), 14, 1.5, "Declarative Logic / Workflows", 
             "- Declarative Logic Authoring   - Workflow Template Management   - Rule Validation & Optimization", sub_fs=8.5)

    # Backend Layer
    draw_box((1, 4.2), 10.5, 1.8, "Core Services")
    draw_box((1.5, 4.5), 2.2, 1, "API Gateway", "接口适配", sub_fs=8)
    draw_box((4.2, 4.5), 2.2, 1, "Orchestration", "任务编排", sub_fs=8)
    draw_box((6.9, 4.5), 2.2, 1, "Scheduling", "调度策略", sub_fs=8)
    draw_box((9.6, 4.5), 1.5, 1, "State Mgt.", "状态存储", sub_fs=8)

    # Execution Layer
    draw_box((1, 1), 3.5, 2, "Event Bus", "事件中枢 (Pub/Sub)", sub_fs=8)
    draw_box((5, 1.5), 3, 1.5, "Agent Manager", "智能体注册/调度", sub_fs=8)
    draw_box((8.5, 1), 4, 2, "Agent Pool", "- Traffic Agent, Safety Agent\n- Perception Agent, Dispatch Agent...", sub_fs=8)

    # Frontend Layer (Spans across layers conceptually)
    draw_box((12, 4.2), 3.5, 1.8, "Frontend Layer", "User Interface\n- React UI & Visualization\n- WebSocket for Real-time State", sub_fs=8)

    # --- Connections ---
    draw_arrow((8, 7.5), (8, 6.8), "解析指令 (Parse Instructions)")
    draw_arrow((6.5, 4.2), (3, 3.0), "事件分发 (Event Dispatch)")
    draw_bidir_arrow((4.5, 2.25), (5, 2.25))
    draw_arrow((8, 2.25), (8.5, 2.25), "")
    draw_arrow((10.5, 1), (10.5, 0.5), "实时反馈 (Real-time Feedback)")
    ax.plot([10.5, 13.75, 13.75], [0.5, 0.5, 4.2], color=TEXT_BLACK, lw=1.5) # Manual arrow routing

    draw_bidir_arrow((11.5, 5.1), (12, 5.1), "API")
    
    # --- Titles ---
    fig.suptitle("System Architecture Overview", fontsize=16, fontfamily=FONT, weight='bold', y=0.99)
    fig.text(0.5, 0.01, "Fig. 1: A Layered, Decoupled Architecture for the DSL-based Multi-Agent System", ha='center', va='bottom', fontsize=10, fontfamily=FONT)

    # --- Save ---
    output_path = "/Users/Apple/Desktop/multi-agent-dsl-final/presentation-site/results/system_architecture_final.svg"
    plt.savefig(output_path, format="svg", bbox_inches="tight", pad_inches=0.4)

if __name__ == "__main__":
    main()