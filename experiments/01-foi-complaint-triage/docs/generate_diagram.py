#!/usr/bin/env python3
"""
Generate architecture diagram for FOI Triage Agent.

Creates a PNG diagram suitable for documentation and LinkedIn posts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as path_effects
from pathlib import Path


def create_architecture_diagram():
    """Create the architecture diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    colors = {
        'user': '#E3F2FD',
        'agent': '#E8F5E9',
        'azure': '#FFF3E0',
        'output': '#F3E5F5',
        'arrow': '#455A64',
        'text': '#212121',
        'accent': '#1976D2',
        'warning': '#FF5722'
    }
    
    title = ax.text(7, 9.5, 'FOI Complaint Triage Agent', 
                    fontsize=20, fontweight='bold', ha='center', va='center',
                    color=colors['text'])
    title.set_path_effects([path_effects.withStroke(linewidth=2, foreground='white')])
    
    subtitle = ax.text(7, 9.0, 'Architecture Overview', 
                       fontsize=14, ha='center', va='center',
                       color='#666666', style='italic')
    
    user_box = FancyBboxPatch((0.5, 5.5), 2.5, 2.5,
                               boxstyle="round,pad=0.1,rounding_size=0.3",
                               facecolor=colors['user'],
                               edgecolor=colors['accent'],
                               linewidth=2)
    ax.add_patch(user_box)
    ax.text(1.75, 7.5, 'USER', fontsize=14, fontweight='bold', ha='center', va='center', color=colors['accent'])
    ax.text(1.75, 6.7, 'Public Sector', fontsize=11, fontweight='bold', ha='center', va='center')
    ax.text(1.75, 6.3, 'Staff', fontsize=11, fontweight='bold', ha='center', va='center')
    ax.text(1.75, 5.8, '(Human in the loop)', fontsize=8, ha='center', va='center', color='#666')
    
    input_box = FancyBboxPatch((0.5, 2.5), 2.5, 2.2,
                                boxstyle="round,pad=0.1,rounding_size=0.3",
                                facecolor='#FFFDE7',
                                edgecolor='#FBC02D',
                                linewidth=2)
    ax.add_patch(input_box)
    ax.text(1.75, 4.3, 'INPUT', fontsize=12, fontweight='bold', ha='center', va='center', color='#F57C00')
    ax.text(1.75, 3.7, 'FOI Request/', fontsize=10, fontweight='bold', ha='center', va='center')
    ax.text(1.75, 3.3, 'Complaint', fontsize=10, fontweight='bold', ha='center', va='center')
    ax.text(1.75, 2.9, '(Free text input)', fontsize=8, ha='center', va='center', color='#666')
    
    agent_box = FancyBboxPatch((4.5, 4), 3, 3.5,
                                boxstyle="round,pad=0.1,rounding_size=0.3",
                                facecolor=colors['agent'],
                                edgecolor='#388E3C',
                                linewidth=2)
    ax.add_patch(agent_box)
    ax.text(6, 7.1, 'AI', fontsize=14, fontweight='bold', ha='center', va='center', color='#388E3C')
    ax.text(6, 6.5, 'Triage Agent', fontsize=12, fontweight='bold', ha='center', va='center')
    ax.text(6, 6.0, '-------------', fontsize=10, ha='center', va='center', color='#888')
    ax.text(6, 5.5, '* Extract asks', fontsize=9, ha='center', va='center')
    ax.text(6, 5.1, '* Classify type', fontsize=9, ha='center', va='center')
    ax.text(6, 4.7, '* Flag urgency', fontsize=9, ha='center', va='center')
    ax.text(6, 4.3, '* Suggest routing', fontsize=9, ha='center', va='center')
    
    azure_box = FancyBboxPatch((9, 4.5), 4, 3,
                                boxstyle="round,pad=0.1,rounding_size=0.3",
                                facecolor=colors['azure'],
                                edgecolor='#F57C00',
                                linewidth=2)
    ax.add_patch(azure_box)
    ax.text(11, 7.1, 'AZURE', fontsize=12, fontweight='bold', ha='center', va='center', color='#F57C00')
    ax.text(11, 6.5, 'AI Foundry', fontsize=12, fontweight='bold', ha='center', va='center')
    ax.text(11, 5.9, 'GPT-4o with', fontsize=10, ha='center', va='center')
    ax.text(11, 5.5, 'Structured Outputs', fontsize=10, ha='center', va='center')
    ax.text(11, 5.0, '(or Mock Mode)', fontsize=9, ha='center', va='center', color='#666', style='italic')
    
    output_box = FancyBboxPatch((4.5, 0.5), 5, 2.8,
                                 boxstyle="round,pad=0.1,rounding_size=0.3",
                                 facecolor=colors['output'],
                                 edgecolor='#7B1FA2',
                                 linewidth=2)
    ax.add_patch(output_box)
    ax.text(7, 3.0, 'OUTPUT', fontsize=11, fontweight='bold', ha='center', va='center', color='#7B1FA2')
    ax.text(7, 2.5, 'Structured Triage', fontsize=10, fontweight='bold', ha='center', va='center')
    output_items = ['Classification & routing', 'Extracted asks with quotes', 
                    'Urgency/safeguarding flags', 'Draft clarification letter']
    for i, item in enumerate(output_items):
        ax.text(7, 2.0 - i*0.35, f'* {item}', fontsize=8, ha='center', va='center')
    
    copilot_box = FancyBboxPatch((10.5, 0.5), 3, 2.8,
                                  boxstyle="round,pad=0.1,rounding_size=0.3",
                                  facecolor='#E0E0E0',
                                  edgecolor='#616161',
                                  linewidth=2, linestyle='--')
    ax.add_patch(copilot_box)
    ax.text(12, 3.0, 'ALT', fontsize=10, fontweight='bold', ha='center', va='center', color='#616161')
    ax.text(12, 2.5, 'Copilot Studio', fontsize=10, fontweight='bold', ha='center', va='center')
    ax.text(12, 2.0, '(Alternative UI)', fontsize=8, ha='center', va='center', color='#666')
    ax.text(12, 1.6, 'Power Automate', fontsize=8, ha='center', va='center')
    ax.text(12, 1.3, 'Integration', fontsize=8, ha='center', va='center')
    
    arrow_style = "Simple, tail_width=0.5, head_width=4, head_length=6"
    
    ax.annotate('', xy=(4.4, 6.5), xytext=(3.1, 6.5),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))
    ax.text(3.75, 6.9, 'Submit', fontsize=8, ha='center', color='#666')
    
    ax.annotate('', xy=(3.1, 3.5), xytext=(4.4, 4.5),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))
    
    ax.annotate('', xy=(8.9, 5.8), xytext=(7.6, 5.8),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))
    ax.text(8.25, 6.2, 'Prompt +', fontsize=8, ha='center', color='#666')
    ax.text(8.25, 5.9, 'Schema', fontsize=8, ha='center', color='#666')
    
    ax.annotate('', xy=(7.6, 5.2), xytext=(8.9, 5.2),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))
    ax.text(8.25, 4.9, 'JSON', fontsize=8, ha='center', color='#666')
    
    ax.annotate('', xy=(6, 3.9), xytext=(6, 3.4),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))
    
    ax.annotate('', xy=(3.1, 5.5), xytext=(4.4, 3.2),
                arrowprops=dict(arrowstyle='->', color='#7B1FA2', lw=2))
    ax.text(3.2, 4.6, 'Review &', fontsize=8, ha='center', color='#666')
    ax.text(3.2, 4.3, 'Decide', fontsize=8, ha='center', color='#666')
    
    ax.annotate('', xy=(10.4, 2), xytext=(9.6, 2),
                arrowprops=dict(arrowstyle='->', color='#666', lw=1.5, linestyle='--'))
    
    warning_box = FancyBboxPatch((0.3, 0.3), 3.5, 1.5,
                                  boxstyle="round,pad=0.05,rounding_size=0.2",
                                  facecolor='#FFEBEE',
                                  edgecolor=colors['warning'],
                                  linewidth=1.5)
    ax.add_patch(warning_box)
    ax.text(2.05, 1.5, '! HUMAN IN THE LOOP', fontsize=9, fontweight='bold', 
            ha='center', va='center', color=colors['warning'])
    ax.text(2.05, 1.1, 'AI assists, never decides', fontsize=8, ha='center', va='center')
    ax.text(2.05, 0.75, 'No auto-rejection of requests', fontsize=8, ha='center', va='center')
    ax.text(2.05, 0.45, 'Staff make all final decisions', fontsize=8, ha='center', va='center')
    
    plt.tight_layout()
    return fig


def main():
    """Generate and save the diagram."""
    output_dir = Path(__file__).parent
    output_path = output_dir / "architecture_diagram.png"
    
    fig = create_architecture_diagram()
    fig.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close(fig)
    
    print(f"Diagram saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    main()
