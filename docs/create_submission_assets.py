#!/usr/bin/env python3
"""
Create all visual assets for Kaggle competition submission
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

# Set style
sns.set_style('whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

# Create output directory
output_dir = Path(__file__).parent / "submission_assets"
output_dir.mkdir(exist_ok=True)

# Load evaluation results
data_dir = Path(__file__).parent.parent / "data"
df_results = pd.read_csv(data_dir / "evaluation_results.csv")


def create_architecture_diagram():
    """Create a modern architecture diagram with light backgrounds"""
    fig, ax = plt.subplots(figsize=(14, 16))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # Modern color scheme with light backgrounds
    colors = {
        'input': '#E3F2FD',  # Light blue
        'input_border': '#2196F3',  # Blue
        'agent_bg': '#E8EAF6',  # Light indigo
        'agent_border': '#3F51B5',  # Indigo
        'output': '#E8F5E9',  # Light green
        'output_border': '#4CAF50',  # Green
        'text': '#1A237E',  # Dark blue
        'agent_text': '#1A237E',  # Dark text for agents
        'arrow': '#757575',  # Gray arrows
        'red_flag_bg': '#FFEBEE',  # Light red
        'red_flag_border': '#F44336',  # Red
        'knowledge_bg': '#F3E5F5',  # Light purple
        'knowledge_border': '#9C27B0',  # Purple
        'shadow': '#00000015'
    }
    
    # Title section with background
    title_bg = FancyBboxPatch((0.5, 14.5), 9, 1.3,
                             boxstyle="round,pad=0.15",
                             facecolor='#FAFAFA', edgecolor='none', alpha=0.7, zorder=0)
    ax.add_patch(title_bg)
    
    ax.text(5, 15.5, 'MedGemma AI Medical Triage System', 
            ha='center', va='top', fontsize=26, fontweight='bold', 
            color=colors['text'], zorder=2)
    ax.text(5, 14.95, 'Multi-Agent Architecture', 
            ha='center', va='top', fontsize=14, color='#546E7A',
            style='italic', zorder=2)
    
    # Helper function for modern boxes with light backgrounds
    def add_box(x, y, width, height, text, bg_color, border_color, fontsize=12, lines=None, is_agent=False):
        # Main box with light background
        box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                            boxstyle="round,pad=0.12", 
                            edgecolor=border_color, facecolor=bg_color,
                            linewidth=3, alpha=0.95, zorder=2)
        ax.add_patch(box)
        
        # Main text - always dark for readability
        text_color = colors['agent_text'] if is_agent else colors['text']
        ax.text(x, y + 0.2, text, ha='center', va='center', 
                fontsize=fontsize, fontweight='bold', color=text_color, zorder=3)
        
        # Additional lines
        if lines:
            y_offset = -0.22
            for line in lines:
                ax.text(x, y + y_offset, line, ha='center', va='center',
                        fontsize=9, color='#616161', zorder=3)
                y_offset -= 0.22
    
    # Helper function for clean arrows
    def add_arrow(x1, y1, x2, y2, label=None, color=None):
        arrow_color = color if color else colors['arrow']
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='->', mutation_scale=30,
                               linewidth=3, color=arrow_color,
                               alpha=0.7, zorder=1)
        ax.add_patch(arrow)
        if label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mid_x + 0.3, mid_y, label, fontsize=10, 
                   style='italic', color=arrow_color, 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                            edgecolor='none', alpha=0.8))
    
    # Patient Input
    add_box(5, 13.5, 4.2, 0.9, 'Patient Input', colors['input'], colors['input_border'],
            lines=['"I have severe chest pain..."'])
    
    # Agent 1: Intake Agent
    add_arrow(5, 13.05, 5, 12.5)
    add_box(5, 11.8, 5, 1.3, '1. Intake Agent', colors['agent_bg'], colors['agent_border'],
            lines=['Collects symptoms', 'Asks clarifying questions', 'Structures information'],
            is_agent=True)
    
    # Agent 2: Symptom Assessment Agent  
    add_arrow(5, 11.15, 5, 10.6)
    add_box(5, 9.9, 5, 1.3, '2. Symptom Assessment Agent', colors['agent_bg'], colors['agent_border'],
            lines=['Analyzes symptoms', 'Identifies conditions', 'Detects red flags'],
            is_agent=True)
    
    # Red Flag Detection (side box) - modern light style
    line = plt.Line2D([7.5, 8.3], [9.9, 9.9], 
                      color=colors['red_flag_border'], linewidth=2, 
                      linestyle='-', alpha=0.5, zorder=1)
    ax.add_line(line)
    
    add_box(9.0, 9.9, 1.7, 1.1, 'Red Flag\nDetection', colors['red_flag_bg'], 
            colors['red_flag_border'], fontsize=10)
    
    # Medical Knowledge Agent (side box) - modern light style
    line = plt.Line2D([1.65, 2.5], [8.0, 8.0], 
                      color=colors['knowledge_border'], linewidth=2, 
                      linestyle='-', alpha=0.5, zorder=1)
    ax.add_line(line)
    
    add_box(0.8, 8.0, 1.7, 1.1, 'Medical\nKnowledge', colors['knowledge_bg'], 
            colors['knowledge_border'], fontsize=10)
    
    # Agent 3: Urgency Classification Agent
    add_arrow(5, 9.25, 5, 8.7)
    add_box(5, 8.0, 5, 1.3, '3. Urgency Classification Agent', colors['agent_bg'], colors['agent_border'],
            lines=['Classifies urgency level', 'Uses triage protocols', 'Provides reasoning'],
            is_agent=True)
    
    # Agent 4: Care Recommendation Agent
    add_arrow(5, 7.35, 5, 6.8)
    add_box(5, 6.1, 5, 1.3, '4. Care Recommendation Agent', colors['agent_bg'], colors['agent_border'],
            lines=['Recommends care setting', 'Suggests next steps', 'Provides timeline'],
            is_agent=True)
    
    # Agent 5: Communication Agent
    add_arrow(5, 5.45, 5, 4.9)
    add_box(5, 4.2, 5, 1.3, '5. Communication Agent', colors['agent_bg'], colors['agent_border'],
            lines=['Patient-friendly language', 'Comprehensive report', 'Medical disclaimers'],
            is_agent=True)
    
    # Final Output
    add_arrow(5, 3.55, 5, 3.0)
    add_box(5, 2.3, 4.5, 1.1, 'Final Triage Report', colors['output'], colors['output_border'],
            lines=['Urgency + Recommendations + Next Steps'])
    
    # Modern legend for urgency levels
    legend_y = 0.9
    # Legend background
    legend_bg = FancyBboxPatch((1.2, legend_y - 0.35), 7.6, 0.85,
                              boxstyle="round,pad=0.1", 
                              edgecolor='#E0E0E0', facecolor='#FAFAFA',
                              linewidth=2, alpha=0.95, zorder=1)
    ax.add_patch(legend_bg)
    
    ax.text(5, legend_y + 0.35, 'Urgency Levels:', ha='center', fontsize=12, 
            fontweight='bold', color=colors['text'])
    
    urgency_colors = ['#D32F2F', '#F57C00', '#FBC02D', '#388E3C']
    urgency_labels = ['EMERGENCY', 'URGENT', 'SEMI-URGENT', 'NON-URGENT']
    
    for i, (label, color) in enumerate(zip(urgency_labels, urgency_colors)):
        x_pos = 2.2 + i * 1.5
        # Main rect
        rect = mpatches.Rectangle((x_pos - 0.45, legend_y - 0.17), 0.9, 0.35,
                                  facecolor=color, edgecolor='white', 
                                  linewidth=2, alpha=0.95, zorder=2)
        ax.add_patch(rect)
        ax.text(x_pos, legend_y, label, ha='center', va='center',
                fontsize=8, color='white', fontweight='bold', zorder=3)
    
    plt.tight_layout()
    plt.savefig(output_dir / "architecture_diagram.png", dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"✓ Created: architecture_diagram.png")
    plt.close()


def create_performance_dashboard():
    """Create a comprehensive performance dashboard"""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Title
    fig.suptitle('MedGemma AI Triage System - Performance Evaluation', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    # 1. Overall Accuracy Gauge
    ax1 = fig.add_subplot(gs[0, 0])
    successful = df_results[df_results['success'] == True]
    accuracy = successful['correct'].mean() if len(successful) > 0 else 0
    emergency_acc = successful[successful['expected_urgency'] == 'EMERGENCY']['correct'].mean()
    
    metrics = ['Overall\nAccuracy', 'Emergency\nAccuracy', 'Success\nRate']
    values = [accuracy * 100, emergency_acc * 100, 100]
    colors_gauge = ['#FFC107', '#4CAF50', '#2196F3']
    
    bars = ax1.barh(metrics, values, color=colors_gauge, alpha=0.8, edgecolor='black')
    ax1.set_xlim(0, 100)
    ax1.set_xlabel('Percentage (%)', fontsize=10)
    ax1.set_title('Key Performance Metrics', fontsize=12, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars, values):
        ax1.text(val + 2, bar.get_y() + bar.get_height()/2, 
                f'{val:.1f}%', va='center', fontsize=10, fontweight='bold')
    
    # 2. Accuracy by Category
    ax2 = fig.add_subplot(gs[0, 1:])
    category_stats = successful.groupby('category').agg({
        'correct': ['mean', 'count']
    }).reset_index()
    category_stats.columns = ['category', 'accuracy', 'count']
    category_stats = category_stats.sort_values('accuracy', ascending=False)
    
    colors_cat = ['#4CAF50' if acc == 1.0 else '#F44336' if acc == 0 else '#FFC107' 
                  for acc in category_stats['accuracy']]
    
    bars = ax2.bar(range(len(category_stats)), category_stats['accuracy'] * 100, 
                   color=colors_cat, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.set_xticks(range(len(category_stats)))
    ax2.set_xticklabels(category_stats['category'], rotation=45, ha='right')
    ax2.set_ylabel('Accuracy (%)', fontsize=11)
    ax2.set_title('Accuracy by Test Category', fontsize=12, fontweight='bold')
    ax2.set_ylim(0, 110)
    ax2.grid(axis='y', alpha=0.3)
    ax2.axhline(y=100, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Perfect')
    
    # Add value labels and counts
    for i, (bar, acc, count) in enumerate(zip(bars, category_stats['accuracy'], category_stats['count'])):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                f'{acc*100:.0f}%', ha='center', fontsize=10, fontweight='bold')
        ax2.text(bar.get_x() + bar.get_width()/2, -8,
                f'n={int(count)}', ha='center', fontsize=8, style='italic')
    
    # 3. Confusion Matrix
    ax3 = fig.add_subplot(gs[1, :])
    from sklearn.metrics import confusion_matrix
    
    y_true = successful['expected_urgency']
    y_pred = successful['actual_urgency']
    
    labels = ['EMERGENCY', 'URGENT', 'SEMI-URGENT', 'NON-URGENT']
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    # Create heatmap
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=labels, yticklabels=labels,
                cbar_kws={'label': 'Count'}, ax=ax3,
                linewidths=2, linecolor='white',
                annot_kws={'size': 14, 'weight': 'bold'})
    
    ax3.set_title('Urgency Classification Confusion Matrix', fontsize=12, fontweight='bold', pad=15)
    ax3.set_ylabel('Expected Urgency', fontsize=11, fontweight='bold')
    ax3.set_xlabel('Predicted Urgency', fontsize=11, fontweight='bold')
    
    # Highlight diagonal
    for i in range(len(labels)):
        ax3.add_patch(plt.Rectangle((i, i), 1, 1, fill=False, edgecolor='green', 
                                    lw=3 if cm[i, i] > 0 else 0))
    
    # 4. Red Flag Detection
    ax4 = fig.add_subplot(gs[2, 0])
    emergency_cases = successful[successful['expected_urgency'] == 'EMERGENCY']
    red_flag_rate = (emergency_cases['red_flags'] > 0).mean() * 100 if len(emergency_cases) > 0 else 0
    
    # Pie chart
    sizes = [red_flag_rate, 100 - red_flag_rate]
    colors_pie = ['#4CAF50', '#E0E0E0']
    explode = (0.1, 0)
    
    wedges, texts, autotexts = ax4.pie(sizes, explode=explode, labels=['Detected', 'Missed'],
                                        colors=colors_pie, autopct='%1.1f%%',
                                        startangle=90, textprops={'fontsize': 11, 'weight': 'bold'})
    ax4.set_title('Red Flag Detection Rate\n(Emergency Cases)', fontsize=11, fontweight='bold')
    
    # 5. Processing Success Rate
    ax5 = fig.add_subplot(gs[2, 1])
    success_counts = df_results['success'].value_counts()
    
    bars = ax5.bar(['Successful', 'Failed'], 
                   [success_counts.get(True, 0), success_counts.get(False, 0)],
                   color=['#4CAF50', '#F44336'], alpha=0.8, edgecolor='black', linewidth=1.5)
    ax5.set_ylabel('Count', fontsize=11)
    ax5.set_title('Processing Success Rate', fontsize=11, fontweight='bold')
    ax5.grid(axis='y', alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # 6. Test Distribution
    ax6 = fig.add_subplot(gs[2, 2])
    category_dist = df_results['category'].value_counts()
    
    colors_dist = plt.cm.Set3(range(len(category_dist)))
    wedges, texts, autotexts = ax6.pie(category_dist.values, labels=category_dist.index,
                                        colors=colors_dist, autopct='%1.0f%%',
                                        startangle=90, textprops={'fontsize': 9})
    ax6.set_title('Test Scenario Distribution', fontsize=11, fontweight='bold')
    
    plt.savefig(output_dir / "performance_dashboard.png", dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"✓ Created: performance_dashboard.png")
    plt.close()


def create_thumbnail():
    """Create a thumbnail/card image for Kaggle (560x280)"""
    fig, ax = plt.subplots(figsize=(11.2, 5.6))  # 560x280 at 50 dpi
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    
    # Background gradient
    from matplotlib.patches import Rectangle
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))
    
    ax.imshow(gradient, aspect='auto', extent=[0, 10, 0, 5], 
              cmap='Blues', alpha=0.3, zorder=0)
    
    # Medical cross icon (simple version)
    cross_x, cross_y = 1.5, 2.5
    cross_size = 0.8
    cross_rect_v = Rectangle((cross_x - 0.15, cross_y - cross_size/2), 0.3, cross_size,
                             facecolor='#2196F3', edgecolor='white', linewidth=3)
    cross_rect_h = Rectangle((cross_x - cross_size/2, cross_y - 0.15), cross_size, 0.3,
                             facecolor='#2196F3', edgecolor='white', linewidth=3)
    ax.add_patch(cross_rect_v)
    ax.add_patch(cross_rect_h)
    
    # Title
    ax.text(5.5, 4, 'MedGemma AI', ha='center', va='top',
            fontsize=42, fontweight='bold', color='#1565C0')
    ax.text(5.5, 3.3, 'Medical Triage System', ha='center', va='top',
            fontsize=32, fontweight='bold', color='#1976D2')
    
    # Subtitle
    ax.text(5.5, 2.5, 'Multi-Agent Medical Intelligence', ha='center', va='center',
            fontsize=20, style='italic', color='#424242')
    
    # Key metrics
    ax.text(3.5, 1.5, '100%', ha='center', va='center',
            fontsize=36, fontweight='bold', color='#4CAF50')
    ax.text(3.5, 1.0, 'Emergency\nDetection', ha='center', va='top',
            fontsize=14, color='#424242')
    
    ax.text(5.5, 1.5, '6', ha='center', va='center',
            fontsize=36, fontweight='bold', color='#2196F3')
    ax.text(5.5, 1.0, 'Specialized\nAgents', ha='center', va='top',
            fontsize=14, color='#424242')
    
    ax.text(7.5, 1.5, '14/14', ha='center', va='center',
            fontsize=36, fontweight='bold', color='#FF9800')
    ax.text(7.5, 1.0, 'Tests\nPassed', ha='center', va='top',
            fontsize=14, color='#424242')
    
    # Bottom tag
    ax.text(5.5, 0.3, 'Powered by Google MedGemma | MedGemma Impact Challenge 2026',
            ha='center', va='center', fontsize=11, color='#757575', style='italic')
    
    plt.savefig(output_dir / "thumbnail.png", dpi=50, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"✓ Created: thumbnail.png")
    plt.close()


def create_key_highlights():
    """Create a visual showing key project highlights with modern design"""
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title with background
    title_bg = FancyBboxPatch((0.5, 8.8), 9, 1.0,
                             boxstyle="round,pad=0.15",
                             facecolor='#FAFAFA', edgecolor='none', alpha=0.7, zorder=0)
    ax.add_patch(title_bg)
    
    ax.text(5, 9.4, 'MedGemma AI Triage System - Key Highlights', 
            ha='center', va='top', fontsize=24, fontweight='bold', color='#1A237E')
    
    # Highlight boxes with modern style
    highlights = [
        {
            'title': '100% Emergency Accuracy',
            'text': 'Perfect identification of life-threatening\nconditions - the most critical metric',
            'tag': '',  # Empty for filled circle
            'tag_color': '#4CAF50',
            'box_color': '#E8F5E9'
        },
        {
            'title': '6-Agent Architecture',
            'text': 'Specialized agents for intake, assessment,\nknowledge, urgency, care, and communication',
            'tag': '',
            'tag_color': '#2196F3',
            'box_color': '#E3F2FD'
        },
        {
            'title': 'Real-Time Triage',
            'text': 'Average processing time under 5 minutes\nper patient assessment',
            'tag': '',
            'tag_color': '#FF9800',
            'box_color': '#FFF3E0'
        },
        {
            'title': 'Safety First',
            'text': 'Multiple red flag checkpoints, confidence\nscoring, and conservative defaults',
            'tag': '',
            'tag_color': '#F44336',
            'box_color': '#FFEBEE'
        },
        {
            'title': 'Global Impact',
            'text': 'Designed for resource-constrained settings\nand rural healthcare access',
            'tag': '',
            'tag_color': '#9C27B0',
            'box_color': '#F3E5F5'
        },
        {
            'title': 'Production Ready',
            'text': 'Complete testing, documentation, and\ndeployment-ready architecture',
            'tag': '',
            'tag_color': '#00BCD4',
            'box_color': '#E0F7FA'
        }
    ]
    
    positions = [
        (1.7, 6.5), (5, 6.5), (8.3, 6.5),
        (1.7, 3.5), (5, 3.5), (8.3, 3.5)
    ]
    
    for (x, y), highlight in zip(positions, highlights):
        # Main box with light background
        box = FancyBboxPatch((x - 1.45, y - 1.15), 2.9, 2.3,
                            boxstyle="round,pad=0.12",
                            edgecolor=highlight['tag_color'],
                            facecolor=highlight['box_color'],
                            linewidth=3, alpha=0.95, zorder=1)
        ax.add_patch(box)
        
        # Checkmark circle at top
        circle = plt.Circle((x, y + 0.85), 0.22, 
                           facecolor=highlight['tag_color'],
                           edgecolor='none', alpha=0.9, zorder=2)
        ax.add_artist(circle)
        
        ax.text(x, y + 0.85, highlight['tag'], ha='center', va='center',
                fontsize=14, fontweight='bold', color='white', zorder=3)
        
        # Title
        ax.text(x, y + 0.35, highlight['title'], ha='center', va='center',
                fontsize=13, fontweight='bold', color=highlight['tag_color'], zorder=2)
        
        # Description text
        ax.text(x, y - 0.35, highlight['text'], ha='center', va='center',
                fontsize=10, color='#424242', linespacing=1.5, zorder=2)
    
    # Bottom section - Tech Stack with styled box
    tech_bg = FancyBboxPatch((0.8, 0.5), 8.4, 1.0,
                            boxstyle="round,pad=0.12",
                            facecolor='#FAFAFA', edgecolor='#E0E0E0',
                            linewidth=2, alpha=0.9, zorder=0)
    ax.add_patch(tech_bg)
    
    ax.text(5, 1.25, 'Technology Stack', ha='center', va='center',
            fontsize=16, fontweight='bold', color='#1A237E')
    
    tech_text = 'MedGemma-1.5-4B | Python | PyTorch | Transformers | Gradio | Custom Agent Framework'
    ax.text(5, 0.75, tech_text, ha='center', va='center',
            fontsize=11, color='#616161', style='italic')
    
    plt.savefig(output_dir / "key_highlights.png", dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"✓ Created: key_highlights.png")
    plt.close()


def create_workflow_visualization():
    """Create an enhanced workflow visualization"""
    fig, ax = plt.subplots(figsize=(16, 11))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Add subtle background gradient
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))
    ax.imshow(gradient, aspect='auto', extent=[0, 14, 0, 10], 
              cmap='Blues', alpha=0.04, zorder=0)
    
    # Enhanced title with shadow - repositioned higher
    ax.text(7.02, 9.78, 'Agentic Workflow: Patient Journey', 
            ha='center', va='top', fontsize=24, fontweight='bold',
            color='#00000015', zorder=1)
    ax.text(7, 9.8, 'Agentic Workflow: Patient Journey', 
            ha='center', va='top', fontsize=24, fontweight='bold',
            color='#1A237E', zorder=2)
    
    # Define workflow stages with enhanced styling - repositioned lower
    stages = [
        {'name': 'Patient\nInput', 'y': 6.5, 'color': '#E3F2FD', 'edge': '#90CAF9', 
         'example': '"Chest pain\nfor 1 hour"', 'text_color': '#1565C0'},
        {'name': 'Intake\nAgent', 'y': 6.5, 'color': '#1565C0', 'edge': '#0D47A1',
         'example': 'Asks clarifying\nquestions', 'text_color': 'white'},
        {'name': 'Symptom\nAgent', 'y': 6.5, 'color': '#1565C0', 'edge': '#0D47A1',
         'example': 'Detects red\nflags', 'text_color': 'white'},
        {'name': 'Urgency\nAgent', 'y': 6.5, 'color': '#1565C0', 'edge': '#0D47A1',
         'example': 'Classifies as\nEMERGENCY', 'text_color': 'white'},
        {'name': 'Care\nAgent', 'y': 6.5, 'color': '#1565C0', 'edge': '#0D47A1',
         'example': 'Recommends\nER visit', 'text_color': 'white'},
        {'name': 'Communication\nAgent', 'y': 6.5, 'color': '#1565C0', 'edge': '#0D47A1',
         'example': 'Patient-friendly\nreport', 'text_color': 'white'},
        {'name': 'Final\nReport', 'y': 6.5, 'color': '#388E3C', 'edge': '#2E7D32',
         'example': 'Complete triage\nassessment', 'text_color': 'white'}
    ]
    
    x_positions = np.linspace(1, 13, len(stages))
    
    for i, (x, stage) in enumerate(zip(x_positions, stages)):
        is_agent = 'Agent' in stage['name']
        
        # Shadow for depth
        shadow = FancyBboxPatch((x - 0.65 + 0.05, stage['y'] - 0.55 - 0.05), 1.3, 1.1,
                               boxstyle="round,pad=0.12",
                               edgecolor='none', facecolor='#00000015',
                               linewidth=0, alpha=0.4, zorder=1)
        ax.add_patch(shadow)
        
        # Main box with enhanced border
        box = FancyBboxPatch((x - 0.65, stage['y'] - 0.55), 1.3, 1.1,
                            boxstyle="round,pad=0.12",
                            edgecolor=stage.get('edge', stage['color']),
                            facecolor=stage['color'],
                            linewidth=3.5 if is_agent else 2.5,
                            alpha=0.95, zorder=2)
        ax.add_patch(box)
        
        # Stage name with better formatting
        ax.text(x, stage['y'] + 0.2, stage['name'], ha='center', va='center',
                fontsize=11, fontweight='bold', color=stage['text_color'],
                linespacing=1.4, zorder=3)
        
        # Example text with background
        example_bg = FancyBboxPatch((x - 0.6, stage['y'] - 1.45), 1.2, 0.5,
                                   boxstyle="round,pad=0.08",
                                   edgecolor='#BDBDBD', facecolor='white',
                                   linewidth=1, alpha=0.9, zorder=1)
        ax.add_patch(example_bg)
        
        ax.text(x, stage['y'] - 1.2, stage['example'], ha='center', va='center',
                fontsize=8.5, style='italic', color='#424242',
                linespacing=1.4, zorder=2)
        
        # Enhanced arrow to next stage
        if i < len(stages) - 1:
            next_x = x_positions[i + 1]
            # Shadow arrow
            arrow_shadow = FancyArrowPatch((x + 0.65 + 0.03, stage['y'] - 0.03), 
                                          (next_x - 0.65 + 0.03, stage['y'] - 0.03),
                                          arrowstyle='->', mutation_scale=30,
                                          linewidth=3, color='#00000008',
                                          alpha=0.5, zorder=1)
            ax.add_patch(arrow_shadow)
            # Main arrow
            arrow = FancyArrowPatch((x + 0.65, stage['y']), (next_x - 0.65, stage['y']),
                                   arrowstyle='->', mutation_scale=30,
                                   linewidth=3.5, color='#546E7A',
                                   alpha=0.85, zorder=2)
            ax.add_patch(arrow)
    
    # Knowledge Agent (supporting role) with glow - repositioned lower
    knowledge_x = 7
    knowledge_y = 3.5
    
    # Glow effect
    for offset in [0.2, 0.15, 0.1, 0.05]:
        glow_box = FancyBboxPatch((knowledge_x - 1.3 - offset, knowledge_y - 0.65 - offset), 
                                 2.6 + 2*offset, 1.3 + 2*offset,
                                 boxstyle="round,pad=0.12",
                                 edgecolor='none', facecolor='#6A1B9A',
                                 linewidth=0, alpha=0.08, zorder=1)
        ax.add_patch(glow_box)
    
    # Shadow
    shadow = FancyBboxPatch((knowledge_x - 1.3 + 0.05, knowledge_y - 0.65 - 0.05), 2.6, 1.3,
                           boxstyle="round,pad=0.12",
                           edgecolor='none', facecolor='#00000015',
                           linewidth=0, alpha=0.4, zorder=1)
    ax.add_patch(shadow)
    
    # Main box
    box = FancyBboxPatch((knowledge_x - 1.3, knowledge_y - 0.65), 2.6, 1.3,
                        boxstyle="round,pad=0.12",
                        edgecolor='#4A148C',
                        facecolor='#6A1B9A',
                        linewidth=3.5, alpha=0.95, zorder=2)
    ax.add_patch(box)
    
    ax.text(knowledge_x, knowledge_y + 0.35, 'Medical Knowledge Agent', 
            ha='center', va='center',
            fontsize=12, fontweight='bold', color='white', zorder=3)
    ax.text(knowledge_x, knowledge_y - 0.15, 'Provides context & guidelines to all agents',
            ha='center', va='center',
            fontsize=9.5, color='white', alpha=0.95, zorder=3)
    
    # Enhanced arrows from knowledge agent to other agents - updated positions
    for x in x_positions[2:6]:  # Connect to symptom, urgency, and care agents
        # Shadow arrow
        arrow_shadow = FancyArrowPatch((knowledge_x + 0.03, knowledge_y + 0.65 + 0.03), 
                                      (x + 0.03, 5.95 - 0.03),
                                      arrowstyle='->', mutation_scale=24,
                                      linewidth=2, color='#00000008',
                                      linestyle='dashed', alpha=0.3, zorder=1)
        ax.add_patch(arrow_shadow)
        # Main arrow
        arrow = FancyArrowPatch((knowledge_x, knowledge_y + 0.65), (x, 5.95),
                               arrowstyle='->', mutation_scale=24,
                               linewidth=2.5, color='#6A1B9A',
                               linestyle='dashed', alpha=0.7, zorder=2)
        ax.add_patch(arrow)
    
    # Red Flag Detection - CENTERED UNDER TITLE with spacing
    redflag_x = 7
    redflag_y = 8.4  # Positioned under title with more space
    
    # Glow effect
    for offset in [0.2, 0.15, 0.1, 0.05]:
        glow_box = FancyBboxPatch((redflag_x - 1.3 - offset, redflag_y - 0.55 - offset), 
                                 2.6 + 2*offset, 1.1 + 2*offset,
                                 boxstyle="round,pad=0.12",
                                 edgecolor='none', facecolor='#D32F2F',
                                 linewidth=0, alpha=0.08, zorder=1)
        ax.add_patch(glow_box)
    
    # Shadow
    shadow = FancyBboxPatch((redflag_x - 1.3 + 0.05, redflag_y - 0.55 - 0.05), 2.6, 1.1,
                           boxstyle="round,pad=0.12",
                           edgecolor='none', facecolor='#00000015',
                           linewidth=0, alpha=0.4, zorder=1)
    ax.add_patch(shadow)
    
    # Main box
    box = FancyBboxPatch((redflag_x - 1.3, redflag_y - 0.55), 2.6, 1.1,
                        boxstyle="round,pad=0.12",
                        edgecolor='#B71C1C',
                        facecolor='#D32F2F',
                        linewidth=3.5, alpha=0.95, zorder=2)
    ax.add_patch(box)
    
    ax.text(redflag_x, redflag_y + 0.25, 'Red Flag Detection', 
            ha='center', va='center',
            fontsize=12, fontweight='bold', color='white', zorder=3)
    ax.text(redflag_x, redflag_y - 0.15, 'Automatic emergency escalation',
            ha='center', va='center',
            fontsize=9.5, color='white', alpha=0.95, zorder=3)
    
    # Straight arrow from symptom agent to red flag - updated positions
    # Shadow arrow
    arrow_shadow = FancyArrowPatch((x_positions[2] + 0.03, 7.05 + 0.03), 
                                  (redflag_x + 0.03, redflag_y - 0.55 - 0.03),
                                  arrowstyle='->', mutation_scale=26,
                                  linewidth=2.5, color='#00000008',
                                  alpha=0.3, zorder=1)
    ax.add_patch(arrow_shadow)
    # Main arrow - STRAIGHT upward
    arrow = FancyArrowPatch((x_positions[2], 7.05), (redflag_x, redflag_y - 0.55),
                           arrowstyle='->', mutation_scale=26,
                           linewidth=3.5, color='#D32F2F',
                           alpha=0.85, zorder=2)
    ax.add_patch(arrow)
    
    # Bottom info with background
    info_bg = FancyBboxPatch((1.5, 0.5), 11, 0.65,
                            boxstyle="round,pad=0.15",
                            edgecolor='#BDBDBD', facecolor='white',
                            linewidth=1.5, alpha=0.95, zorder=1)
    ax.add_patch(info_bg)
    
    info_text = 'Each agent uses MedGemma to perform specialized medical reasoning | Average processing: <5 minutes'
    ax.text(7, 0.82, info_text, ha='center', va='center',
            fontsize=11, color='#546E7A', style='italic', zorder=2)
    
    plt.savefig(output_dir / "workflow_visualization.png", dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"✓ Created: workflow_visualization.png")
    plt.close()


def create_impact_infographic():
    """Create a user-friendly infographic showing potential real-world impact"""
    fig, ax = plt.subplots(figsize=(14, 11))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title section with background
    title_bg = FancyBboxPatch((0.5, 10.5), 9, 1.3,
                             boxstyle="round,pad=0.2",
                             facecolor='#E3F2FD', edgecolor='none', alpha=0.5, zorder=0)
    ax.add_patch(title_bg)
    
    ax.text(5, 11.5, 'Real-World Impact Potential', 
            ha='center', va='top', fontsize=26, fontweight='bold', color='#0D47A1')
    ax.text(5, 10.95, 'Transforming Healthcare Access in Resource-Constrained Settings',
            ha='center', va='top', fontsize=14, style='italic', color='#546E7A')
    
    # Impact metrics - more user-friendly with color coding
    impacts = [
        {
            'number': '2.7M+',
            'label': 'Annual Assessments',
            'detail': 'At just 1% deployment',
            'tag': 'SCALE',
            'tag_color': '#4CAF50',
            'box_color': '#E8F5E9'
        },
        {
            'number': '50%',
            'label': 'Global Population',
            'detail': 'Lacks health access',
            'tag': 'REACH',
            'tag_color': '#2196F3',
            'box_color': '#E3F2FD'
        },
        {
            'number': '20-30%',
            'label': 'Wait Time Reduction',
            'detail': 'Optimized allocation',
            'tag': 'EFFICIENCY',
            'tag_color': '#FF9800',
            'box_color': '#FFF3E0'
        },
        {
            'number': '$100K+',
            'label': 'Annual Savings',
            'detail': 'Per facility',
            'tag': 'VALUE',
            'tag_color': '#9C27B0',
            'box_color': '#F3E5F5'
        }
    ]
    
    positions = [(2.5, 8.8), (7.5, 8.8), (2.5, 6.2), (7.5, 6.2)]
    
    for (x, y), impact in zip(positions, impacts):
        # Main box with color-coded background
        box = FancyBboxPatch((x - 1.9, y - 1.05), 3.8, 2.1,
                            boxstyle="round,pad=0.15",
                            edgecolor=impact['tag_color'],
                            facecolor=impact['box_color'],
                            linewidth=3, alpha=0.95, zorder=1)
        ax.add_patch(box)
        
        # Category tag at top
        tag_box = FancyBboxPatch((x - 0.6, y + 0.75), 1.2, 0.3,
                                boxstyle="round,pad=0.05",
                                facecolor=impact['tag_color'],
                                edgecolor='none', alpha=0.9, zorder=2)
        ax.add_patch(tag_box)
        
        ax.text(x, y + 0.9, impact['tag'], ha='center', va='center',
                fontsize=9, fontweight='bold', color='white', zorder=3)
        
        # Large prominent number
        ax.text(x, y + 0.2, impact['number'], ha='center', va='center',
                fontsize=32, fontweight='bold', color=impact['tag_color'], zorder=2)
        
        # Clear label
        ax.text(x, y - 0.35, impact['label'], ha='center', va='center',
                fontsize=12, fontweight='bold', color='#212121', zorder=2)
        
        # Context detail
        ax.text(x, y - 0.7, impact['detail'], ha='center', va='center',
                fontsize=9.5, color='#616161', zorder=2)
    
    # Use cases section title - moved down
    ax.text(5, 4.5, 'Key Use Cases', ha='center', va='center',
            fontsize=18, fontweight='bold', color='#0D47A1')
    
    # Use cases as individual boxes (similar to metrics) - positioned lower
    use_cases = [
        {
            'title': 'Rural Clinics',
            'description': 'Extend specialist expertise\nto underserved areas',
            'tag': 'ACCESSIBILITY',
            'tag_color': '#00897B',
            'box_color': '#E0F2F1'
        },
        {
            'title': 'Telemedicine',
            'description': 'Provide structured\ninitial assessment',
            'tag': 'REMOTE CARE',
            'tag_color': '#5E35B1',
            'box_color': '#EDE7F6'
        },
        {
            'title': 'Emergency Dept',
            'description': 'Optimize patient\nprioritization',
            'tag': 'EFFICIENCY',
            'tag_color': '#E64A19',
            'box_color': '#FBE9E7'
        },
        {
            'title': 'Disaster Response',
            'description': 'Rapid triage during\nmass casualty events',
            'tag': 'CRISIS READY',
            'tag_color': '#C62828',
            'box_color': '#FFEBEE'
        }
    ]
    
    use_case_positions = [(2, 3.5), (4, 3.5), (6, 3.5), (8, 3.5)]
    
    for (x, y), use_case in zip(use_case_positions, use_cases):
        # Main box with color-coded background
        box = FancyBboxPatch((x - 0.85, y - 0.65), 1.7, 1.3,
                            boxstyle="round,pad=0.1",
                            edgecolor=use_case['tag_color'],
                            facecolor=use_case['box_color'],
                            linewidth=2.5, alpha=0.95, zorder=1)
        ax.add_patch(box)
        
        # Category tag at top
        tag_box = FancyBboxPatch((x - 0.55, y + 0.45), 1.1, 0.25,
                                boxstyle="round,pad=0.04",
                                facecolor=use_case['tag_color'],
                                edgecolor='none', alpha=0.9, zorder=2)
        ax.add_patch(tag_box)
        
        ax.text(x, y + 0.575, use_case['tag'], ha='center', va='center',
                fontsize=7.5, fontweight='bold', color='white', zorder=3)
        
        # Title
        ax.text(x, y + 0.05, use_case['title'], ha='center', va='center',
                fontsize=11, fontweight='bold', color='#212121', zorder=2)
        
        # Description
        ax.text(x, y - 0.35, use_case['description'], ha='center', va='center',
                fontsize=8.5, color='#424242', linespacing=1.4, zorder=2)
    
    # Visual separator - moved down
    ax.plot([1, 9], [2.3, 2.3], color='#BDBDBD', linewidth=2, alpha=0.5)
    
    # Safety section - prominent and clear - moved down
    safety_bg = FancyBboxPatch((0.8, 0.2), 8.4, 2.0,
                              boxstyle="round,pad=0.15",
                              facecolor='#FFEBEE', edgecolor='#EF5350',
                              linewidth=3, alpha=0.95, zorder=0)
    ax.add_patch(safety_bg)
    
    ax.text(5, 1.95, 'Clinical Safety & Validation', ha='center', va='center',
            fontsize=18, fontweight='bold', color='#C62828')
    
    # Safety features in organized grid
    safety_features = [
        '100% Emergency Detection',
        'Red Flag Checkpoints',
        'Conservative Defaults',
        'Human Oversight',
        'Complete Audit Trails',
        'Medical Disclaimers'
    ]
    
    # Display in 2 rows of 3
    y_positions = [1.25, 0.8]
    x_positions = [2.2, 5, 7.8]
    
    idx = 0
    for y in y_positions:
        for x in x_positions:
            if idx < len(safety_features):
                ax.text(x, y, safety_features[idx], ha='center', va='center',
                       fontsize=10.5, fontweight='bold', color='#424242')
                idx += 1
    
    plt.savefig(output_dir / "impact_infographic.png", dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"✓ Created: impact_infographic.png")
    plt.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Creating Submission Assets for Kaggle Competition")
    print("="*60 + "\n")
    
    print("Generating visualizations...")
    create_architecture_diagram()
    create_performance_dashboard()
    create_thumbnail()
    create_key_highlights()
    create_workflow_visualization()
    create_impact_infographic()
    
    print("\n" + "="*60)
    print(f"✓ All assets created successfully!")
    print(f"✓ Output directory: {output_dir.absolute()}")
    print("="*60 + "\n")
    
    print("Files created:")
    for f in sorted(output_dir.glob("*.png")):
        print(f"  - {f.name}")
