"""
 Product Discovery AI - Gradio Interface
Beautiful UI with real-time agent monitoring
"""
import sys
from pathlib import Path

# ✅ Fix Python path to find 'product' module
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Now your regular imports
import gradio as gr
from product.crew import ProductDiscoveryCrew
import time
from datetime import datetime
from io import StringIO
import re
import queue
import threading
import sys

# Custom CSS for beautiful styling
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

.gradio-container {
    font-family: 'Inter', sans-serif !important;
}

.header-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40px;
    border-radius: 16px;
    color: white;
    margin-bottom: 30px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    margin-bottom: 20px;
    border: 1px solid #e5e7eb;
}

.metric-row {
    display: flex;
    gap: 20px;
    margin: 20px 0;
}

.metric-card {
    flex: 1;
    background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
    padding: 24px;
    border-radius: 12px;
    border: 2px solid #e5e7eb;
    text-align: center;
    transition: transform 0.2s;
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: #667eea;
}

.metric-value {
    font-size: 36px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.metric-label {
    font-size: 14px;
    color: #6b7280;
    font-weight: 500;
}

.agent-badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 14px;
    margin: 4px;
}

.agent-completed {
    background: #d1fae5;
    color: #065f46;
}

.agent-running {
    background: #fef3c7;
    color: #92400e;
    animation: pulse 2s infinite;
}

.agent-pending {
    background: #f3f4f6;
    color: #6b7280;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
"""

# Agent activity tracker
class AgentTracker:
    def __init__(self):
        self.activities = []
        self.agents = [
            {"name": "Market Landscape", "icon": "🔍", "status": "pending"},
            {"name": "Customer Pain Mining", "icon": "💬", "status": "pending"},
            {"name": "Opportunity Sizing", "icon": "📊", "status": "pending"},
            {"name": "Risk Assessment", "icon": "⚠️", "status": "pending"},
            {"name": "Strategy Synthesis", "icon": "🎯", "status": "pending"}
        ]
    
    def update_status(self, agent_index: int, status: str, message: str = ""):
        if 0 <= agent_index < len(self.agents):
            self.agents[agent_index]["status"] = status
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activities.append({
            "time": timestamp,
            "message": message
        })
    
    def get_progress_html(self):
        html = '<div style="margin: 20px 0;">'
        
        # Progress badges
        for agent in self.agents:
            status_class = f"agent-{agent['status']}"
            html += f'<span class="agent-badge {status_class}">{agent["icon"]} {agent["name"]}</span>'
        
        html += '</div>'
        
        # Activity log
        html += '<div class="card" style="margin-top: 20px; max-height: 300px; overflow-y: auto;">'
        html += '<h3 style="margin-top: 0;">📋 Activity Log</h3>'
        
        for activity in self.activities[-10:]:
            html += f'<div style="padding: 8px; border-left: 3px solid #667eea; margin: 8px 0; background: #f9fafb;">'
            html += f'<span style="font-weight: 600; color: #667eea;">{activity["time"]}</span> '
            html += f'<span>{activity["message"]}</span>'
            html += '</div>'
        
        html += '</div>'
        return html

# Stream handler to capture terminal output
class StreamToQueue:
    def __init__(self, q):
        self.q = q

    def write(self, data):
        if data:
            self.q.put(data)

    def flush(self):
        pass

# Parse results into structured sections
def parse_results(raw_output: str):
    """Extract key sections from the crew output"""
    sections = {
        "recommendation": "",
        "confidence": "",
        "market_size": "",
        "top_risk": "",
        "full_report": raw_output
    }
    
    # Improved parsing with regex for cleaner extraction
    rec_match = re.search(r"Product Recommendation:\s*(.*?)(?:\n\n|\n[A-Z]|$)", raw_output, re.DOTALL)
    if rec_match:
        sections["recommendation"] = rec_match.group(1).strip()
    
    conf_match = re.search(r"Confidence Level:\s*(.*?)(?:\n|$)", raw_output)
    if conf_match:
        sections["confidence"] = conf_match.group(1).strip()
    
    # Extract market sizing info (looking for SOM range)
    som_match = re.search(r"SOM.*?(\$[\d\.,MK\s]+-?\$?[\d\.,MK\s]+)", raw_output)
    if som_match:
        sections["market_size"] = som_match.group(1).strip()
    
    # Extract top risk
    risk_match = re.search(r"(?:CRITICAL RISK|KEY RISKS):\s*(.*?)(?:\n\n|\n[A-Z]|$)", raw_output, re.DOTALL)
    if risk_match:
        risk_text = risk_match.group(1).strip()
        sections["top_risk"] = risk_text[:300] + "..." if len(risk_text) > 300 else risk_text
    
    return sections

# Main analysis function with progress tracking and streaming
def analyze_product_idea(product_idea, target_customer, constraints, industry, vertical):
    """Run the product discovery analysis with real-time updates and streaming logs"""
    
    tracker = AgentTracker()
    log_queue = queue.Queue()
    stream_handler = StreamToQueue(log_queue)
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = stream_handler
    
    # Validate inputs
    if not product_idea or not target_customer:
        sys.stdout = old_stdout
        yield (
            "❌ Please provide both a product idea and target customer.",
            "", "", "", "", "", "Waiting for input..."
        )
        return

    # Prepare inputs
    inputs = {
        "product_idea": product_idea,
        "target_customer": target_customer,
        "constraints": constraints or "No specific constraints provided",
        "industry": industry or "Not specified",
        "vertical": vertical or "Not specified"
    }

    results = {"final": None, "error": None}
    
    def run_crew():
        try:
            crew_obj = ProductDiscoveryCrew().crew()
            results["final"] = crew_obj.kickoff(inputs=inputs)
        except Exception as e:
            results["error"] = str(e)

    # Start crew in a separate thread
    thread = threading.Thread(target=run_crew)
    thread.start()

    accumulated_logs = ""
    summary_html = '<div class="card"><p style="text-align: center; padding: 20px;">🤖 Agents are brainstorming... check the "Agent Thinking" tab for live logs!</p></div>'
    
    # Yield logs while the thread is running
    while thread.is_alive():
        while not log_queue.empty():
            accumulated_logs += log_queue.get()
        
        yield (
            summary_html,
            "_Analysis in progress..._",
            "_Analysis in progress..._",
            "_Analysis in progress..._",
            "_Analysis in progress..._",
            accumulated_logs,
            accumulated_logs
        )
        time.sleep(0.5)

    # Restore stdout
    sys.stdout = old_stdout

    if results["error"]:
        error_msg = f"❌ An error occurred: {results['error']}"
        yield (error_msg, "", "", "", "", "", accumulated_logs)
        return

    # Process final results
    result = results["final"]
    sections = parse_results(str(result))
    
    # Create beautiful summary HTML
    summary_html = f"""
    <div class="card">
        <h2 style="margin-top: 0; color: #764ba2;">📋 Executive Summary</h2>
        <div style="padding: 24px; background: linear-gradient(135deg, #f8faff 0%, #ffffff 100%); border-radius: 12px; border: 1px solid #e2e8f0; margin: 15px 0; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">
            <div style="margin-bottom: 16px;">
                <span style="font-weight: 700; color: #475569; text-transform: uppercase; font-size: 12px; letter-spacing: 0.05em;">Recommendation</span>
                <p style="font-size: 18px; color: #1e293b; margin: 4px 0; font-weight: 600;">{sections['recommendation'] or "See full report"}</p>
            </div>
            <div style="display: flex; gap: 24px;">
                <div style="flex: 1;">
                    <span style="font-weight: 700; color: #475569; text-transform: uppercase; font-size: 12px; letter-spacing: 0.05em;">Confidence</span>
                    <p style="font-size: 16px; color: #1e293b; margin: 4px 0; font-weight: 500;">{sections['confidence'] or "TBD"}</p>
                </div>
                <div style="flex: 1;">
                    <span style="font-weight: 700; color: #475569; text-transform: uppercase; font-size: 12px; letter-spacing: 0.05em;">Projected SOM</span>
                    <p style="font-size: 16px; color: #1e293b; margin: 4px 0; font-weight: 500;">{sections['market_size'] or "TBD"}</p>
                </div>
            </div>
        </div>
    </div>
    """
    
    # Extract specific task outputs
    # Order in crew.py: market_landscape (0), subreddit_discovery (1), customer_pain (2), opportunity_sizing (3), risk_assumptions (4), final_strategy (5)
    tasks = result.tasks_output
    competitive = tasks[0].raw if len(tasks) > 0 else "No data"
    pain = tasks[2].raw if len(tasks) > 2 else "No data"
    sizing = tasks[3].raw if len(tasks) > 3 else "No data"
    risks = tasks[4].raw if len(tasks) > 4 else "No data"
    full_text = str(result)

    yield (
        summary_html,
        competitive,
        pain,
        sizing,
        risks,
        full_text,
        accumulated_logs
    )

# Create Gradio interface
with gr.Blocks(title="Product Discovery AI") as demo:
    
    # Header
    gr.HTML("""
        <div class="header-section">
            <h1 style="font-size: 48px; margin: 0; font-weight: 700;">🚀 Product Discovery AI</h1>
            <p style="font-size: 20px; margin-top: 12px; opacity: 0.95; font-weight: 400;">
                Validate your product idea in minutes, not weeks
            </p>
            <p style="font-size: 14px; margin-top: 8px; opacity: 0.8;">
                Powered by multi-agent AI • Real customer signals • Data-driven decisions
            </p>
        </div>
    """)
    
    with gr.Row():
        # Left column: Inputs
        with gr.Column(scale=1):
            gr.Markdown("### 📝 Product Details")
            
            product_idea = gr.Textbox(
                label="💡 Product Idea",
                placeholder="Describe your product idea in detail...\nExample: AI-powered fitness coach for busy professionals",
                lines=4,
                info="Be specific about what problem you're solving"
            )
            
            target_customer = gr.Textbox(
                label="🎯 Target Customer",
                placeholder="Who is your ideal customer?\nExample: Working professionals aged 30-45 with limited time for gym",
                lines=3,
                info="Include demographics, behaviors, and pain points"
            )
            
            constraints = gr.Textbox(
                label="⚙️ Constraints (Optional)",
                placeholder="Budget, timeline, technical constraints...\nExample: Low budget, MVP in 3 months, B2C subscription",
                lines=2
            )
            industry = gr.Textbox(
                label="🏢 Industry",
                placeholder="e.g., dating tech, fintech, healthcare, edtech, fitness",
                lines=1,
                info="What industry or market category is this product in?"
            )
            vertical = gr.Textbox(
                label="📈 Business Model",
                placeholder="e.g., B2C SaaS, B2B Enterprise, Marketplace, Hardware",
                lines=1,
                info="What type of business model are you using?"
            )
            
            with gr.Row():
                submit_btn = gr.Button("🚀 Start Analysis", variant="primary", size="lg")
                clear_btn = gr.ClearButton([product_idea, target_customer, constraints, industry, vertical], value="Clear")

            
            # Examples
            gr.Examples(
                examples=[
    [
        "AI-powered meal planning app for people with Type 2 diabetes",
        "Adults aged 40-65 diagnosed with Type 2 diabetes, struggling with dietary management",
        "Need to ensure FDA compliance, 6-month development window",
        "healthcare tech",
        "B2C SaaS"
    ],
    [
        "Automated LinkedIn outreach tool for B2B sales teams",
        "Sales Development Reps at B2B SaaS companies with 10-100 employees",
        "Bootstrap budget, must integrate with existing CRMs",
        "sales tech",
        "B2B SaaS"
    ],
    [
        "Mental wellness app for remote workers with anxiety",
        "Remote workers aged 25-40 experiencing work-related stress and anxiety",
        "Low budget, mobile-first, subscription model under $15/month",
        "mental health tech",
        "B2C mobile app"
    ]
],
inputs=[product_idea, target_customer, constraints, industry, vertical],
                label="💡 Try These Examples",
            )
        
        # Right column: Results
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Analysis Results")
            
            with gr.Tabs():
                with gr.Tab("📋 Summary"):
                    summary_output = gr.HTML(value='<div class="card"><p style="color: #6b7280; text-align: center; padding: 40px;">Results will appear here after analysis...</p></div>')
                
                with gr.Tab("🏢 Competitive Analysis"):
                    competitive_output = gr.Markdown(value="_Competitive analysis will appear here..._")
                
                with gr.Tab("💬 Customer Pain"):
                    pain_output = gr.Markdown(value="_Customer pain analysis will appear here..._")
                
                with gr.Tab("📊 Market Sizing"):
                    sizing_output = gr.Markdown(value="_Market sizing will appear here..._")
                
                with gr.Tab("⚠️ Risks"):
                    risks_output = gr.Markdown(value="_Risk assessment will appear here..._")
                
                with gr.Tab("📄 Full Report"):
                    full_output = gr.Markdown(value="_The complete analysis report will appear here..._")

                with gr.Tab("🧠 Agent Thinking"):
                    thinking_output = gr.Code(
                        label="Live Agent Thoughts & Tool Usage",
                        language="markdown",
                        value="Agents are ready to start...",
                        lines=20
                    )
    

    
    # Wire up the submit button
    submit_btn.click(
        fn=analyze_product_idea,
        inputs=[product_idea, target_customer, constraints, industry, vertical],
        outputs=[summary_output, competitive_output, pain_output, sizing_output, risks_output, full_output, thinking_output],
        show_progress=True
    )

# Launch the app
if __name__ == "__main__":
    demo.queue()
    demo.launch(
    share=False,
    show_error=True,
    server_name="0.0.0.0", 
    css=custom_css
)
