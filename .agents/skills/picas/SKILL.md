# Skill: Project Intelligence & Capital Acquisition (PICAS)

## Description
Analyzes a project's local directory, codebase, and internal documentation to extract its core mission, architecture, and value proposition. Then performs external market intelligence gathering to generate an enterprise-grade fundraising and corporate strategy package.

## Trigger Keywords
- "project intelligence"
- "capital acquisition"
- "fundraising"
- "pitch deck"
- "business plan"
- "investment prospectus"
- "PICAS"
- "TAM analysis"
- "competitive landscape"
- "valuation"

## When to Use
Invoke this skill when:
- The user wants to raise capital or seek investment
- The user needs a business plan or pitch deck
- The user wants to understand their market position
- The user needs investor-ready documentation
- The user wants to analyze a project for acquisition or partnership

## Workflow

### Phase 1: Local Ingestion & System Extraction

#### Step 1.1: File & Directory Scanning
1. Scan project root for structural files:
   - package.json, Cargo.toml, requirements.txt, go.mod
   - Dockerfile, docker-compose.yml, Makefile
   - .env.example, config/*.yaml, config/*.json
   - README.md, docs/, CONTRIBUTING.md
   - ARCHITECTURE.md, SYSTEM_DESIGN.md

2. Scan for architecture documentation:
   - Database schemas (SQL files, ORM migrations)
   - API specifications (OpenAPI/Swagger, .proto files)
   - Infrastructure as code (Terraform, CloudFormation)
   - Deployment configurations (Kubernetes, Helm charts)

3. Scan for business logic:
   - Service definitions and route handlers
   - Data models and entities
   - Integration points (third-party APIs)
   - Security implementations (auth, encryption)

#### Step 1.2: Core Purpose Synthesis
Generate:
- **Mission Statement**: Primary objectives and problems solved
- **Technical IP**: Proprietary algorithms, unique workflows, moats
- **User Profile**: Target personas and use cases
- **Value Proposition**: What makes this unique

### Phase 2: Market Intelligence & External Research

#### Step 2.1: Market Sizing
Search for and compile:
- Total Addressable Market (TAM)
- Serviceable Addressable Market (SAM)
- Serviceable Obtainable Market (SOM)
- Market growth rates and trends

#### Step 2.2: Competitive Landscape
Identify and analyze:
- Direct competitors (same technology)
- Indirect competitors (alternative solutions)
- Pricing models and tiers
- Feature comparisons
- Market share estimates

#### Step 2.3: Regulatory Environment
Research:
- Industry-specific regulations (SOC2, GDPR, HIPAA, etc.)
- Compliance requirements
- Certification pathways
- Legal considerations

#### Step 2.4: Market Trends & Valuation
Research:
- Recent VC investments in sector
- M&A activity
- Valuation multiples
- Investor preferences
- Exit opportunities

### Phase 3: Deliverable Generation

#### Document 1: Executive Business Plan
- Executive Summary
- Company & Product Overview
- Market & Industry Analysis
- Go-to-Market Strategy
- Operational Plan
- Financial Model & Projections
- Risk Management Matrix

#### Document 2: Pitch Deck Outline
- Slide 1: Title & Elevator Pitch
- Slide 2: The Problem
- Slide 3: The Solution
- Slide 4: Market Opportunity
- Slide 5: Technology & Secret Sauce
- Slide 6: Business Model
- Slide 7: Go-to-Market Strategy
- Slide 8: Competitive Landscape
- Slide 9: Product Roadmap
- Slide 10: Financial Projections
- Slide 11: The Team
- Slide 12: The Ask & Use of Funds

#### Document 3: Investment Prospectus
- Offering Overview
- Investment Thesis
- Capitalization Table (Cap Table Pro-Forma)
- Use of Proceeds Breakdown
- Exit Strategy Analysis

#### Document 4: Supporting Artifacts
- Technical Whitepaper / One-Pager
- Security & Compliance Brief
- Financial Sensitivity Analysis

## Output Structure
All deliverables go to: `docs/PICAS/{project-name}/`

```
docs/PICAS/
├── project-name/
│   ├── Business_Plan.md
│   ├── Pitch_Deck_Slide_Deck.md
│   ├── Investment_Prospectus.md
│   ├── Technical_Whitepaper.md
│   ├── Security_Compliance_Brief.md
│   ├── Financial_Sensitivity_Analysis.md
│   └── attachments/
│       ├── competitive_matrix.png
│       └── market_trends_chart.png
```

## Constraints
- Anchor all product capabilities in scanned system specs
- Ground all financial/market projections in verifiable data
- Use professional Markdown formatting
- Produce thorough, articulated documents (no placeholders)
- Include source citations for all external data

## Dependencies
- Web fetch capability for market research
- File system access for codebase analysis
- Markdown generation capability

## Quality Checks
- [ ] All key files scanned and analyzed
- [ ] Mission statement derived from codebase
- [ ] TAM/SAM/SOM calculated with sources
- [ ] Competitors identified and analyzed
- [ ] Regulatory requirements mapped
- [ ] Financial projections include assumptions
- [ ] All documents use professional formatting
