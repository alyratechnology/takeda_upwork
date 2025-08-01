import streamlit as st
import pandas as pd
from typing import Dict, List, Any
import json
from datetime import datetime
import time

# Import our custom modules
from agents.orchestrator_agent import OrchestratorAgent
from agents.smart_orchestrator_agent import SmartOrchestratorAgent
from database.vector_db import VectorDatabaseManager
from database.graph_db import GraphDatabaseManager
from utils.data_processor import DataProcessor
from utils.audit_logger import AuditLogger, RiskLevel, ObservationType
from utils.checklist_generator import AuditChecklistGenerator
from config import OUTPUT_TYPES

class AuditIntelligenceApp:
    def __init__(self):
        # Initialize components only when needed for better performance
        self._orchestrator = None
        self._smart_orchestrator = None
        self._vector_db = None
        self._graph_db = None
        self._data_processor = None
        self._audit_logger = None
        self._checklist_generator = None
        
    @property
    def orchestrator(self):
        if self._orchestrator is None:
            self._orchestrator = OrchestratorAgent()
        return self._orchestrator
    
    @property
    def smart_orchestrator(self):
        if self._smart_orchestrator is None:
            self._smart_orchestrator = SmartOrchestratorAgent()
        return self._smart_orchestrator
    
    @property
    def vector_db(self):
        if self._vector_db is None:
            self._vector_db = VectorDatabaseManager()
        return self._vector_db
    
    @property
    def graph_db(self):
        if self._graph_db is None:
            self._graph_db = GraphDatabaseManager()
        return self._graph_db
    
    @property
    def data_processor(self):
        if self._data_processor is None:
            self._data_processor = DataProcessor()
        return self._data_processor
    
    @property
    def audit_logger(self):
        if self._audit_logger is None:
            self._audit_logger = AuditLogger()
        return self._audit_logger
    
    @property
    def checklist_generator(self):
        if self._checklist_generator is None:
            self._checklist_generator = AuditChecklistGenerator()
        return self._checklist_generator
        
    def run(self):
        st.set_page_config(
            page_title="Takeda AI Audit Intelligence",
            page_icon="📋",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for better performance and styling
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
        }
        .agent-status {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px;
            border-radius: 5px;
            margin: 5px 0;
            background-color: #f8f9fa;
        }
        .agent-loading {
            color: #007bff;
        }
        .agent-success {
            color: #28a745;
        }
        .agent-error {
            color: #dc3545;
        }
        .source-item {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
            border-left: 4px solid #007bff;
        }
        .response-container {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .file-upload-area {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background-color: #fafafa;
            margin: 20px 0;
        }
        .stButton > button {
            width: 100%;
            background-color: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #0056b3;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown('<h1 class="main-header">Takeda AI Audit Intelligence</h1>', unsafe_allow_html=True)
        
        # Sidebar
        self._create_sidebar()
        
        # Main content
        self._create_main_content()
        
    def _create_sidebar(self):
        """Create the simplified sidebar"""
        st.sidebar.title("AI Agents")
        
        # Agent status display
        st.sidebar.markdown("### Agent Status")
        
        # Initialize agent status in session state
        if 'agent_status' not in st.session_state:
            st.session_state.agent_status = {
                'web_scraper': 'idle',
                'internal_audit': 'idle', 
                'external_conference': 'idle',
                'quality_systems': 'idle',
                'sop': 'idle'
            }
        
        # Display agent status with icons
        for agent_name, status in st.session_state.agent_status.items():
            display_name = agent_name.replace('_', ' ').title()
            
            if status == 'idle':
                st.sidebar.markdown(f"⭕ {display_name} Agent")
            elif status == 'running':
                st.sidebar.markdown(f"🔄 {display_name} Agent")
            elif status == 'completed':
                st.sidebar.markdown(f"✅ {display_name} Agent")
            elif status == 'error':
                st.sidebar.markdown(f"❌ {display_name} Agent")
        
        st.sidebar.markdown("---")
        
        # Document upload section (frontend only)
        st.sidebar.markdown("### 📁 Document Upload")
        st.sidebar.markdown("*(Coming Soon)*")
        
        uploaded_files = st.sidebar.file_uploader(
            "Upload documents for analysis",
            type=['pdf', 'csv', 'docx', 'txt'],
            accept_multiple_files=True,
            disabled=True
        )
        
        if uploaded_files:
            st.sidebar.info("Document processing will be available in a future update.")
                    
    def _create_main_content(self):
        """Create the main content area"""
        
        # Create tabs for different functionalities
        tab1, tab2, tab3, tab4 = st.tabs(["🤖 Smart Audit AI", "📋 Checklist Generator", "📝 Observation Logger", "📊 Audit Reports"])
        
        with tab1:
            self._create_smart_audit_tab()
        
        with tab2:
            self._create_checklist_tab()
        
        with tab3:
            self._create_observation_logger_tab()
        
        with tab4:
            self._create_audit_reports_tab()
    
    def _create_smart_audit_tab(self):
        """Create the Smart Audit AI tab"""
        st.markdown("### 🤖 Smart Audit Orchestrator")
        st.markdown("Ask complex audit questions and get intelligent, risk-based responses.")
        
        # Query input
        query = st.text_area(
            "Enter your audit-related question:",
            placeholder="e.g., Generate a checklist for Hovione sterile manufacturing audit, or Provide 360° health status for Boehringer Ingelheim, or What changed since our last audit?",
            height=100
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.button("Submit to Smart AI", type="primary")
        
        # Process query
        if submit_button and query.strip():
            self._process_smart_query(query.strip())
    
    def _create_checklist_tab(self):
        """Create the Checklist Generator tab"""
        st.markdown("### 📋 Intelligent Checklist Generator")
        st.markdown("Generate comprehensive, risk-based audit checklists.")
        
        # Checklist parameters
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name", placeholder="e.g., Hovione, Boehringer Ingelheim")
            audit_type = st.selectbox(
                "Audit Type",
                ["comprehensive", "supplier", "internal", "regulatory", "cdmo"]
            )
        
        with col2:
            product_modality = st.selectbox(
                "Product Modality",
                ["", "sterile_manufacturing", "oral_solid", "biotech", "laboratory", "warehouse", "quality_systems"]
            )
            
            risk_factors = st.text_area(
                "Risk Factors (one per line)",
                placeholder="e.g., sterility concerns\ndata integrity issues\nvalidation gaps",
                height=100
            )
        
        # Generate checklist button
        if st.button("Generate Checklist", type="primary"):
            if company_name:
                self._generate_checklist(company_name, audit_type, product_modality, risk_factors)
    
    def _create_observation_logger_tab(self):
        """Create the Observation Logger tab"""
        st.markdown("### 📝 Audit Observation Logger")
        st.markdown("Log and manage audit observations with structured data.")
        
        # Observation input form
        with st.form("observation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                area = st.text_input("Area", placeholder="e.g., Warehouse, QC Laboratory")
                finding = st.text_area("Finding", placeholder="Describe the observation")
                risk_level = st.selectbox("Risk Level", ["Critical", "Major", "Minor"])
                evidence = st.text_area("Evidence", placeholder="Supporting evidence")
            
            with col2:
                reference = st.text_input("Reference", placeholder="e.g., 21 CFR 211.22, SOP-123")
                observation_type = st.selectbox(
                    "Observation Type",
                    ["Document Review", "Interview", "On-site Observation", "System Review", "Facility Tour"]
                )
                auditor = st.text_input("Auditor", placeholder="Auditor name")
                company = st.text_input("Company", placeholder="Company being audited")
                audit_type = st.text_input("Audit Type", placeholder="e.g., supplier, internal")
            
            corrective_action = st.text_area("Corrective Action (Optional)", placeholder="Proposed corrective action")
            
            submitted = st.form_submit_button("Log Observation", type="primary")
            
            if submitted and area and finding and evidence:
                self._log_observation(area, finding, risk_level, evidence, reference, 
                                   observation_type, auditor, company, audit_type, corrective_action)
        
        # Display existing observations
        st.markdown("### Recent Observations")
        self._display_observations()
    
    def _create_audit_reports_tab(self):
        """Create the Audit Reports tab"""
        st.markdown("### 📊 Audit Reports & Analytics")
        st.markdown("Generate comprehensive audit reports and analytics.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                "Report Type",
                ["Observation Summary", "Structured Report", "Detailed Report", "Delta Analysis"]
            )
            
            company_filter = st.text_input("Company Filter (Optional)", placeholder="Filter by company")
        
        with col2:
            format_type = st.selectbox("Format", ["structured", "summary", "detailed"])
            
            if st.button("Generate Report", type="primary"):
                self._generate_report(report_type, company_filter, format_type)
    
    def _process_query(self, query: str):
        """Process the user query with intelligent routing"""
        
        # Reset agent status
        for agent_name in st.session_state.agent_status:
            st.session_state.agent_status[agent_name] = 'idle'
        
        # Determine intent and route
        intent = self._determine_intent(query)
        
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🤖 AI Analysis in Progress")
            
            # Show which agents will be used
            agents_to_use = self._get_relevant_agents(query, intent)
            
            # Create columns for agent status
            cols = st.columns(len(agents_to_use))
            
            # Initialize agent status
            for i, agent_name in enumerate(agents_to_use):
                with cols[i]:
                    st.markdown(f"**{agent_name.replace('_', ' ').title()}**")
                    status_placeholder = st.empty()
                    st.session_state.agent_status[agent_name] = 'running'
                    status_placeholder.markdown("🔄 Running...")
        
        # Process with orchestrator
        try:
            # Get response from orchestrator
            response = self.orchestrator.process_query(query, intent=intent)
            
            # Update agent status to completed
            for agent_name in agents_to_use:
                st.session_state.agent_status[agent_name] = 'completed'
            
            # Display response
            self._display_response(response, query)
            
        except Exception as e:
            # Update agent status to error
            for agent_name in agents_to_use:
                st.session_state.agent_status[agent_name] = 'error'
            
            st.error(f"An error occurred while processing your query: {str(e)}")
    
    def _process_smart_query(self, query: str):
        """Process query using the Smart Orchestrator Agent"""
        
        # Reset agent status
        for agent_name in st.session_state.agent_status:
            st.session_state.agent_status[agent_name] = 'idle'
        
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🧠 Smart Audit AI Analysis")
            
            # Show processing status
            status_placeholder = st.empty()
            status_placeholder.markdown("🔄 Smart AI is analyzing your query...")
        
        # Process with smart orchestrator
        try:
            # Get response from smart orchestrator
            response = self.smart_orchestrator.process_query(query)
            
            # Update agent status
            for agent_name in response.get('involved_agents', []):
                if agent_name in st.session_state.agent_status:
                    st.session_state.agent_status[agent_name] = 'completed'
            
            # Display smart response
            self._display_smart_response(response, query)
            
        except Exception as e:
            st.error(f"An error occurred while processing your query: {str(e)}")
    
    def _generate_checklist(self, company_name: str, audit_type: str, product_modality: str, risk_factors: str):
        """Generate audit checklist"""
        
        # Parse risk factors
        risk_list = [factor.strip() for factor in risk_factors.split('\n') if factor.strip()] if risk_factors else None
        
        # Generate checklist
        checklist_data = self.checklist_generator.generate_checklist(
            audit_type=audit_type,
            company_name=company_name,
            product_modality=product_modality if product_modality else None,
            risk_factors=risk_list
        )
        
        # Display checklist
        st.markdown("### 📋 Generated Audit Checklist")
        
        # Show summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Items", checklist_data['total_items'])
        with col2:
            st.metric("Critical", checklist_data['priority_breakdown']['Critical'])
        with col3:
            st.metric("Standard", checklist_data['priority_breakdown']['Standard'])
        with col4:
            st.metric("Watchlist", checklist_data['priority_breakdown']['Watchlist'])
        
        # Display checklist
        st.markdown(checklist_data['checklist'])
        
        # Download option
        checklist_json = json.dumps(checklist_data, indent=2)
        st.download_button(
            label="Download Checklist (JSON)",
            data=checklist_json,
            file_name=f"audit_checklist_{company_name}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
    
    def _log_observation(self, area: str, finding: str, risk_level: str, evidence: str, 
                        reference: str, observation_type: str, auditor: str, company: str, 
                        audit_type: str, corrective_action: str):
        """Log a new audit observation"""
        
        # Convert risk level to enum
        risk_level_enum = RiskLevel(risk_level)
        
        # Convert observation type to enum
        observation_type_enum = ObservationType(observation_type)
        
        # Create observation
        observation = self.audit_logger.create_observation(
            area=area,
            finding=finding,
            risk_level=risk_level_enum,
            evidence=evidence,
            reference=reference,
            observation_type=observation_type_enum,
            auditor=auditor,
            company=company,
            audit_type=audit_type,
            corrective_action=corrective_action if corrective_action else None
        )
        
        st.success(f"✅ Observation logged successfully! ID: {observation.id}")
    
    def _display_observations(self):
        """Display recent observations"""
        
        # Get observations summary
        summary = self.audit_logger.generate_observation_summary()
        
        # Show summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", summary['total_observations'])
        with col2:
            st.metric("Critical", summary['by_risk_level']['Critical'])
        with col3:
            st.metric("Major", summary['by_risk_level']['Major'])
        with col4:
            st.metric("Minor", summary['by_risk_level']['Minor'])
        
        # Show recent observations
        recent_observations = self.audit_logger.observations[-10:]  # Last 10 observations
        
        if recent_observations:
            for obs in reversed(recent_observations):
                with st.expander(f"{obs.area} - {obs.finding[:50]}..."):
                    st.markdown(f"**Risk Level:** {obs.risk_level.value} {obs.priority_label}")
                    st.markdown(f"**Evidence:** {obs.evidence}")
                    st.markdown(f"**Reference:** {obs.reference}")
                    st.markdown(f"**Status:** {obs.status}")
                    st.markdown(f"**Date:** {obs.timestamp.strftime('%Y-%m-%d %H:%M')}")
                    
                    if obs.corrective_action:
                        st.markdown(f"**Corrective Action:** {obs.corrective_action}")
        else:
            st.info("No observations logged yet.")
    
    def _generate_report(self, report_type: str, company_filter: str, format_type: str):
        """Generate audit report"""
        
        if report_type == "Observation Summary":
            report = self.audit_logger.generate_observation_summary(company_filter if company_filter else None)
            st.markdown("### 📊 Observation Summary")
            st.json(report)
        
        elif report_type == "Structured Report":
            report = self.audit_logger.generate_observation_report(
                company_filter if company_filter else None, 
                "structured"
            )
            st.markdown("### 📋 Structured Observation Report")
            st.markdown(report)
        
        elif report_type == "Detailed Report":
            report = self.audit_logger.generate_observation_report(
                company_filter if company_filter else None, 
                "detailed"
            )
            st.markdown("### 📄 Detailed Observation Report")
            st.markdown(report)
        
        elif report_type == "Delta Analysis":
            # This would integrate with the smart orchestrator for delta analysis
            st.info("Delta analysis requires integration with Smart Orchestrator Agent.")
    
    def _display_smart_response(self, response: Dict[str, Any], query: str):
        """Display response from Smart Orchestrator Agent with enhanced document citations"""
        
        st.markdown("---")
        st.markdown("### Smart Audit AI Response")
        
        # Display intent and agent communications
        intent = response.get('intent', 'unknown')
        st.info(f"**Detected Intent:** {intent.replace('_', ' ').title()}")
        
        # Display agent communications
        agent_communications = response.get('agent_communications', [])
        if agent_communications:
            st.markdown("### Agent Communications")
            comm_col1, comm_col2, comm_col3 = st.columns(3)
            
            with comm_col1:
                st.metric("Total Agents", len(agent_communications))
            
            with comm_col2:
                successful_agents = len([comm for comm in agent_communications if comm.get('status') == 'completed'])
                st.metric("Successful", successful_agents)
            
            with comm_col3:
                total_docs = sum(comm.get('documents_found', 0) for comm in agent_communications if comm.get('status') == 'completed')
                st.metric("Documents Found", total_docs)
            
            # Show agent details
            for comm in agent_communications:
                if comm.get('status') == 'completed':
                    st.success(f"✅ {comm['agent'].replace('_', ' ').title()}: {comm.get('documents_found', 0)} documents (Score: {comm.get('relevance_score', 0):.2f})")
                else:
                    st.error(f"❌ {comm['agent'].replace('_', ' ').title()}: {comm.get('error', 'Unknown error')}")
        
        # Display main response
        if 'response' in response:
            st.markdown("### Analysis Results")
            st.markdown(response['response'])
        
        # Display cross-agent insights
        cross_agent_insights = response.get('cross_agent_insights', {})
        if cross_agent_insights and any(cross_agent_insights.values()):
            st.markdown("### Cross-Agent Insights")
            for insight_type, insight_content in cross_agent_insights.items():
                if insight_content:
                    with st.expander(f"{insight_type.replace('_', ' ').title()}"):
                        st.markdown(insight_content)
        
        # Display document citations
        document_citations = response.get('document_citations', [])
        if document_citations:
            st.markdown("### Document Citations")
            
            # Show document summary
            document_summary = response.get('document_summary', {})
            if document_summary:
                doc_col1, doc_col2, doc_col3, doc_col4 = st.columns(4)
                
                with doc_col1:
                    st.metric("Total Documents", document_summary.get('total_documents', 0))
                
                with doc_col2:
                    st.metric("Document Types", len(document_summary.get('document_types', {})))
                
                with doc_col3:
                    st.metric("Agents Used", len(document_summary.get('agents_used', [])))
                
                with doc_col4:
                    high_relevance = len(document_summary.get('high_relevance_documents', []))
                    st.metric("High Relevance", high_relevance)
            
            # Show document breakdown by agent
            document_breakdown = document_summary.get('document_breakdown', {})
            if document_breakdown:
                st.markdown("#### Documents by Agent")
                for agent, docs in document_breakdown.items():
                    with st.expander(f"{agent.replace('_', ' ').title()} ({len(docs)} documents)"):
                        for doc in docs:
                            st.markdown(f"**{doc.get('document_id', 'Unknown')}**: {doc.get('title', 'Unknown')}")
                            st.markdown(f"*File: {doc.get('file_name', 'Unknown')} | Score: {doc.get('relevance_score', 0):.3f}*")
            
            # Show high relevance documents
            high_relevance_docs = document_summary.get('high_relevance_documents', [])
            if high_relevance_docs:
                st.markdown("#### High Relevance Documents")
                for doc in high_relevance_docs:
                    st.markdown(f"**{doc.get('document_id', 'Unknown')}**: {doc.get('title', 'Unknown')}")
                    st.markdown(f"*Agent: {doc.get('agent', 'Unknown')} | File: {doc.get('file_name', 'Unknown')} | Score: {doc.get('relevance_score', 0):.3f}*")
        
        # Display detailed sources
        sources = response.get('sources', [])
        if sources:
            st.markdown("### Detailed Sources")
            for i, source in enumerate(sources[:10], 1):  # Show top 10 sources
                with st.expander(f"Source {i}: {source.get('title', 'Unknown')} ({source.get('document_id', 'Unknown')})"):
                    st.markdown(f"**Agent:** {source.get('agent', 'Unknown')}")
                    st.markdown(f"**File:** {source.get('metadata', {}).get('file_name', 'Unknown')}")
                    st.markdown(f"**Type:** {source.get('metadata', {}).get('file_extension', 'Unknown')}")
                    st.markdown(f"**Relevance Score:** {source.get('score', 0):.3f}")
                    st.markdown(f"**Company:** {source.get('metadata', {}).get('company', 'N/A')}")
                    st.markdown(f"**Date:** {source.get('metadata', {}).get('date', 'N/A')}")
                    
                    if source.get('content'):
                        st.markdown("**Content Preview:**")
                        st.markdown(f"*{source['content'][:300]}...*")
    
    def _determine_intent(self, query: str) -> str:
        """Determine the user's intent from the query"""
        query_lower = query.lower()
        
        # Check for checklist intent
        if any(word in query_lower for word in ['checklist', 'list', 'steps', 'procedures']):
            return 'checklist'
        
        # Check for report intent
        if any(word in query_lower for word in ['report', 'analysis', 'summary', 'overview']):
            return 'report'
        
        # Check for insights intent
        if any(word in query_lower for word in ['insights', 'trends', 'patterns', 'analysis']):
            return 'insights'
        
        # Default to general
        return 'general'
    
    def _get_relevant_agents(self, query: str, intent: str) -> List[str]:
        """Determine which agents are relevant for the query"""
        query_lower = query.lower()
        relevant_agents = []
        
        # Always include orchestrator
        relevant_agents.append('orchestrator')
        
        # Check for company-specific queries
        if any(word in query_lower for word in ['hovione', 'boehringer', 'thermo fisher', 'company']):
            relevant_agents.extend(['quality_systems', 'external_conference'])
        
        # Check for audit-related queries
        if any(word in query_lower for word in ['audit', 'compliance', 'checklist']):
            relevant_agents.extend(['internal_audit', 'sop'])
        
        # Check for quality-related queries
        if any(word in query_lower for word in ['quality', 'snc', 'deviation']):
            relevant_agents.append('quality_systems')
        
        # Check for conference-related queries
        if any(word in query_lower for word in ['conference', 'event', 'meeting']):
            relevant_agents.append('external_conference')
        
        # Check for web scraping related queries
        if any(word in query_lower for word in ['fda', 'warning', 'due diligence']):
            relevant_agents.append('web_scraper')
        
        # If no specific agents identified, use all
        if len(relevant_agents) <= 1:
            relevant_agents = ['web_scraper', 'internal_audit', 'external_conference', 'quality_systems', 'sop']
        
        return relevant_agents
    
    def _display_response(self, response: Dict, query: str):
        """Display the response with proper formatting and source attribution"""
        
        st.markdown("---")
        st.markdown("### 📋 Response")
        
        # Create response container
        with st.container():
            st.markdown('<div class="response-container">', unsafe_allow_html=True)
            
            # Display main response
            if 'response' in response:
                st.markdown(response['response'])
            
            # Display sources with better formatting
            if 'sources' in response and response['sources']:
                st.markdown("---")
                st.markdown("### 📚 Sources")
                
                for i, source in enumerate(response['sources'], 1):
                    with st.expander(f"Source {i}: {source.get('title', 'Unknown Document')}"):
                        st.markdown(f"**Document:** {source.get('title', 'Unknown')}")
                        st.markdown(f"**Agent:** {source.get('agent', 'Unknown')}")
                        st.markdown(f"**Relevance:** {source.get('score', 0):.3f}")
                        
                        if 'content' in source:
                            st.markdown("**Content:**")
                            st.markdown(f"*{source['content'][:300]}...*")
                        
                        if 'metadata' in source:
                            st.markdown("**Metadata:**")
                            for key, value in source['metadata'].items():
                                st.markdown(f"- **{key}:** {value}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display processing summary
        st.markdown("---")
        st.markdown("### ⚡ Processing Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Query Type", self._determine_intent(query).title())
        
        with col2:
            st.metric("Agents Used", len([s for s in st.session_state.agent_status.values() if s == 'completed']))
        
        with col3:
            st.metric("Sources Found", len(response.get('sources', [])))

def main():
    app = AuditIntelligenceApp()
    app.run()

if __name__ == "__main__":
    main() 