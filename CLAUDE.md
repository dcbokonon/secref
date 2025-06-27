# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About Me
- **Name**: Mike DiLalo (handle: Boko)
- **GitHub**: dcbokonon
- **Email**: Personal (mike@mikedilalo.com), Work (mdilalo@rutgers.edu), Hacker (dcbokonon@gmail.com)
- **Organization**: Rutgers University - CABM
- **Location**: Manville, NJ

## Important Git Commit Rules

**NEVER credit Claude in git commits.** All changes should be credited to the user. Do not include:
- "🤖 Generated with Claude Code"
- "Co-Authored-By: Claude <noreply@anthropic.com>"
- Any mention of AI, Claude, or automated generation

Commits should be written as if the user wrote them directly.

## Project Overview

This is a comprehensive cybersecurity resource website project - the ultimate cybersecurity resource hub designed as a one-stop shop where security professionals (from total newbies to seasoned pros) can find everything they need without having to bookmark 500 different sites.

### Main Goals
- **Central Knowledge Base**: Organizing literally everything cybersecurity related into clean categories
- **Community-Driven Content**: Git-based contributions so the community can keep everything fresh
- **Directory-First Design**: Clean, scannable directory structure inspired by OSINT Framework - minimal visual overhead, maximum information density
- **No BS Architecture**: Static site, no user accounts, no tracking, no database - just fast, searchable content
- **Free Resource Focus**: Heavy emphasis on free and open source alternatives

## Comprehensive Architecture

### Dual Architecture Design

The project uses a **dual architecture** approach:
1. **Astro Static Site** - Public-facing directory of resources
2. **Flask Admin Panel** - Protected admin interface for resource management

This intentional split provides:
- Fast, cacheable public site with zero authentication overhead
- Secure admin panel with full authentication and CRUD capabilities
- SQLite database for admin operations with JSON export for static site
- Complete separation of public and administrative concerns

### Technology Stack (Current Implementation)

#### Public Site (Astro)
- **Astro 4.0** (Static Site Generator)
  - Zero JavaScript by default (optimal performance)
  - Progressive enhancement - add JS only where needed
  - File-based routing matches content hierarchy
  - Terminal-inspired design with expandable directory tree
  - Faster builds than Next.js, simpler than Hugo

#### Admin Panel (Flask)
- **Flask 2.3** with security hardening
  - Flask-Login for authentication
  - Flask-WTF for CSRF protection
  - Flask-Limiter for rate limiting
  - SQLAlchemy for database ORM
  - Bleach for input sanitization

#### Database & Content Management
- **SQLite** - Zero-dependency database
  - Chosen over PostgreSQL for simplicity ("rock solid design, not cutting edge")
  - Full referential integrity and constraints
  - Audit logging for all changes
  - Two-way sync with JSON files

- **JSON Files** - Source of truth for static site
  - Git-trackable for community contributions
  - Organized by category/subcategory structure
  - Exported from admin panel after edits

#### Search
- **Pagefind 1.0**
  - Generates static search indexes at build time
  - ~100KB initial download, loads more as needed
  - Sub-10ms search performance
  - Zero runtime dependencies

#### Security Stack
- **Authentication**: Flask-Login with secure session management
- **Input Validation**: Bleach for HTML sanitization, custom validators
- **CSRF Protection**: Flask-WTF with secure tokens
- **Rate Limiting**: Flask-Limiter (100/hour by default)
- **Security Headers**: Implemented via Caddy
- **HTTPS**: Automatic via Caddy with Let's Encrypt

#### Development Tools
- **TypeScript 5** - Type safety for Astro components
- **Python 3.9+** - Admin panel backend
- **ESLint + Prettier** - JavaScript code consistency
- **Black + isort** - Python code formatting
- **Pre-commit hooks** - Security scanning (bandit, safety)
- **GitHub Actions** - CI/CD with security scanning

### Infrastructure

#### Version Control
- GitHub (public repository)
- Branch protection on main
- PR-based contribution workflow

#### Hosting
- Vultr VPS (Ubuntu 22.04 LTS)
- 2GB RAM, 55GB SSD
- $12/month with backups
- **Server IP**: 149.28.63.158
- **Location**: New York (NJ)

#### Domain
- **Domain**: secref.org
- **Registrar**: Porkbun
- **DNS**: Managed via Porkbun

#### Web Server
- Caddy 2.7
- Automatic HTTPS
- Brotli compression
- Security headers

#### CI/CD
- GitHub Actions
- Automated testing and building
- Direct deployment via SSH

## Admin Panel Features

### Security Implementation
The admin panel has been hardened with comprehensive security measures:

1. **Authentication & Authorization**
   - Single admin user with environment-configured password hash
   - Session-based authentication with secure cookies
   - Automatic session expiry and logout functionality
   - Login rate limiting (5 attempts per 15 minutes)

2. **Input Validation & Sanitization**
   - All user inputs sanitized with Bleach
   - URL validation to prevent javascript: and data: URLs
   - SQL injection prevention via parameterized queries
   - XSS protection on all rendered content

3. **CSRF Protection**
   - All forms protected with CSRF tokens
   - Secure token generation and validation
   - Token rotation on each request

4. **Security Headers (via Caddy)**
   - Content-Security-Policy restricting sources
   - X-Frame-Options to prevent clickjacking
   - X-Content-Type-Options to prevent MIME sniffing
   - Strict-Transport-Security for HTTPS enforcement

5. **Audit Logging**
   - All database changes logged with user, timestamp, and details
   - Export/import operations tracked
   - Resource health checks logged

### Admin UI Features
- **Resource Management**: Full CRUD operations with duplicate detection
- **Category Management**: Multi-category assignment with primary designation
- **Bulk Operations**: Mass updates for type, categories, and deletion
- **Health Dashboard**: Resource quality metrics and missing data reports
- **Sync Status**: Real-time database/JSON synchronization monitoring
- **Import/Export**: Bidirectional sync between SQLite and JSON files

## Detailed Project Structure

```
secref/
├── admin/                       # Flask admin panel
│   ├── app.py                  # Main Flask application with security
│   ├── auth.py                 # Authentication system
│   ├── validators.py           # Input validation and sanitization
│   ├── templates/
│   │   ├── login.html         # Login page with CSRF
│   │   └── index.html         # Admin dashboard UI
│   └── requirements.txt        # Python dependencies
├── src/                        # Astro static site
│   ├── pages/
│   │   ├── index.astro        # Homepage with directory tree
│   │   └── [...slug].astro    # Dynamic resource pages
│   ├── components/
│   │   ├── DirectoryTree.astro # Expandable resource tree
│   │   └── ResourceDetail.astro # Resource detail view
│   ├── data/
│   │   └── tools/             # JSON resource files
│   │       ├── reconnaissance.json
│   │       ├── web-security.json
│   │       └── ...
│   └── styles/
│       └── global.css         # Terminal-inspired styling
├── scripts/                    # Database and sync scripts
│   ├── db_config_sqlite.py    # SQLite database configuration
│   ├── import_json_to_sqlite.py # JSON → SQLite importer
│   ├── export_sqlite_to_json.py # SQLite → JSON exporter
│   └── generate_test_api_key.py # API key generator
├── tests/                      # Comprehensive test suite
│   ├── test_database.py       # Database operations (394 lines)
│   ├── test_api.py           # API endpoints (354 lines)
│   ├── test_ui.py            # UI components (313 lines)
│   └── test_integration.py    # End-to-end tests
├── database/                   # SQLite database (gitignored)
│   └── secref.db
├── .github/                    # GitHub configuration
│   ├── workflows/
│   │   ├── ci.yml            # CI/CD pipeline
│   │   └── security.yml      # Security scanning
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   │   ├── bug_report.md
│   │   ├── resource_request.md
│   │   └── broken_link.md
│   ├── pull_request_template.md
│   └── dependabot.yml        # Dependency updates
├── Dockerfile                 # Multi-stage secure build
├── docker-compose.yml        # Container orchestration
├── Caddyfile                 # Web server with security headers
├── supervisord.conf          # Process management
├── Makefile                  # Common development tasks
├── .pre-commit-config.yaml   # Security scanning hooks
├── .env.example              # Environment template
├── .gitignore               # Comprehensive ignore rules
├── .nvmrc                   # Node version (v20)
├── CHANGELOG.md             # Version history
├── CODE_OF_CONDUCT.md       # Community guidelines
├── CONTRIBUTING.md          # Contribution guide
├── CONTRIBUTORS.md          # Contributor list
├── LICENSE                  # MIT License
└── README.md               # Project documentation
```

## Comprehensive Content Domains

### 1. Technical Domains

#### 1.1 Offensive Security
- Web Application Security
- Network Penetration Testing
- Mobile Application Security
- API Security Testing
- Cloud Penetration Testing
- Physical Security Testing
- Social Engineering
- Red Team Operations
- Purple Team Exercises
- Legal Boundaries & Safe Testing

#### 1.2 Defensive Security
- Security Operations Center (SOC)
- Incident Response
- Threat Hunting
- Threat Intelligence
- Security Monitoring
- Log Analysis
- SIEM Management
- Endpoint Security
- Network Defense
- Email Security
- Deception Technology

#### 1.3 Binary Exploitation & Reverse Engineering
- Binary Exploitation (PWN)
- Malware Analysis
- Firmware Analysis
- Mobile Reverse Engineering
- Game Hacking
- Anti-Reversing Techniques

#### 1.4 Digital Forensics
- Disk Forensics
- Memory Forensics
- Network Forensics
- Mobile Device Forensics
- Cloud Forensics
- IoT Forensics
- Vehicle Forensics
- Drone Forensics

#### 1.5 Cryptography & Cryptanalysis
- Applied Cryptography
- Cryptanalysis
- Blockchain Security
- Quantum Cryptography
- Hardware Security Modules
- PKI Management

#### 1.6 Application Security
- Secure Code Review
- SAST/DAST/IAST
- DevSecOps
- Container Security
- Serverless Security
- Supply Chain Security
- Dependency Management

#### 1.7 Infrastructure Security
- Network Security
- Cloud Security (AWS/Azure/GCP)
- Kubernetes Security
- Database Security
- Virtualization Security
- Zero Trust Architecture

### 2. Specialized Domains

#### 2.1 Industrial & Critical Infrastructure
- ICS/SCADA Security
- Building Management Systems
- Energy Grid Security
- Water System Security
- Manufacturing Security
- Nuclear Facility Security

#### 2.2 Transportation & Mobility
- Automotive Security
- Aviation Security
- Maritime Cybersecurity
- Railway Security
- Drone/UAV Security
- Space Systems Security
- Satellite Security

#### 2.3 Healthcare & Life Sciences
- Medical Device Security
- Healthcare IT Security
- Biomedical Equipment Security
- Pharmaceutical Security
- Telemedicine Security

#### 2.4 Financial Services
- Banking Security
- Payment Systems Security
- ATM Security
- Cryptocurrency Security
- Trading Platform Security
- Insurance Tech Security

#### 2.5 Emerging Technologies
- AI/ML Security
- IoT Security
- 5G Security
- Quantum Computing Security
- AR/VR Security
- Metaverse Security

#### 2.6 Physical & Hardware Security
- Hardware Hacking
- RFID/NFC Security
- Lock Picking
- Physical Access Control
- Surveillance Systems
- Alarm Systems

### 3. Business & Governance

#### 3.1 Governance, Risk & Compliance
- Risk Management
- Compliance Frameworks
- Audit & Assurance
- Policy Development
- Third-Party Risk
- Vendor Management

#### 3.2 Privacy & Data Protection
- Privacy Engineering
- GDPR Compliance
- CCPA/CPRA
- Data Loss Prevention
- Data Classification
- Privacy Impact Assessments

#### 3.3 Security Leadership
- CISO Resources
- Security Strategy
- Budget Management
- Board Communication
- Security Metrics
- Team Building

#### 3.4 Business Continuity
- Disaster Recovery
- Crisis Management
- Incident Communication
- Cyber Insurance
- Resilience Planning

## Comprehensive Tool Categories

### 9.1 Network Security Tools
- **Network Scanners**
  - Port Scanners (Nmap, Masscan, Zmap, RustScan)
  - Vulnerability Scanners (OpenVAS, Nessus*, Qualys*, Rapid7*)
  - Network Mappers (Netdiscover, arp-scan, fping)
- **Packet Analysis**
  - Packet Capture (Wireshark, tcpdump, tshark)
  - Network Forensics (NetworkMiner, Xplico)
  - Traffic Generators (hping3, Scapy, Ostinato)
- **Network Defense**
  - IDS/IPS (Snort, Suricata, OSSEC, Zeek/Bro)
  - Firewalls (pfSense, OPNsense, iptables, UFW)
  - Honeypots (Honeyd, Kippo, Cowrie, T-Pot)

### 9.2 Web Application Security Tools
- **Web Scanners**
  - Industry Standard: Burp Suite Pro*
  - Free Alternatives: OWASP ZAP, Burp Community
  - Others: Acunetix*, AppSpider*, w3af
- **Web Exploitation**
  - SQLi Tools (sqlmap, SQLNinja, jSQL)
  - XSS Tools (XSSer, BeEF, XSStrike)
  - Directory Brute Force (Dirb, Dirbuster, Gobuster, feroxbuster, ffuf)
- **API Testing**
  - Postman, Insomnia, SoapUI
  - API Security: OWASP API Security Top 10 tools

### 9.3 Password & Cryptography Tools
- **Password Cracking**
  - Industry Standard: Hashcat
  - CPU-based: John the Ripper
  - Online: CrackStation, HashKiller
  - Rainbow Tables: RainbowCrack, ophcrack
- **Password Management**
  - Enterprise: CyberArk*, Thycotic*, HashiCorp Vault
  - Open Source: Bitwarden, KeePass, pass
- **Cryptography Tools**
  - Analysis: CrypTool, Cryptool-Online
  - Encryption: GnuPG, OpenSSL, VeraCrypt

### 9.4 Exploitation Frameworks
- **General Frameworks**
  - Metasploit (Framework/Pro*)
  - Cobalt Strike* (Industry standard for red teams)
  - Empire, Covenant (C2 frameworks)
  - BeEF (Browser exploitation)
- **Post-Exploitation**
  - PowerShell Empire, PowerSploit
  - Mimikatz (Windows credentials)
  - Impacket (Windows protocols)
  - BloodHound (AD enumeration)

### 9.5 SIEM & Log Management
- **Enterprise SIEM**
  - Industry Standards: Splunk*, QRadar*, ArcSight*
  - Mid-Market: LogRhythm*, Securonix*
- **Open Source SIEM**
  - ELK Stack (Elasticsearch, Logstash, Kibana)
  - Security Onion (Complete NSM platform)
  - Wazuh (HIDS + SIEM)
  - OSSIM/AlienVault
  - Graylog
- **Log Analysis Tools**
  - grep/awk/sed (basics)
  - LogParser, Chainsaw
  - Sigma rules (detection engineering)

### 9.6 Forensics & Incident Response
- **Disk Forensics**
  - Industry Standard: EnCase*, FTK*
  - Open Source: Autopsy, Sleuth Kit
  - Imaging: dd, dc3dd, FTK Imager
- **Memory Forensics**
  - Volatility (Framework 2 & 3)
  - Rekall, Redline
  - DumpIt, LiME (acquisition)
- **Mobile Forensics**
  - Commercial: Cellebrite*, Oxygen*, XRY*
  - Open Source: Andriller, ALEAPP/iLEAPP
- **Incident Response**
  - KAPE, DFIR-ORC
  - Velociraptor, GRR
  - TheHive (case management)

### 9.7 Vulnerability Management
- **Vulnerability Scanners**
  - Enterprise: Tenable Nessus*, Qualys VMDR*, Rapid7 Nexpose*
  - Open Source: OpenVAS/GVM, Nuclei
- **Configuration Scanning**
  - CIS-CAT*, Lynis, OpenSCAP
  - Docker: Docker Bench, Clair
- **Patch Management**
  - WSUS, SCCM* (Windows)
  - Spacewalk, Katello (Linux)

### 9.8 Cloud Security Tools
- **Multi-Cloud Security**
  - Commercial: Prisma Cloud*, Dome9*, Lacework*
  - Open Source: Cloud Custodian, ScoutSuite
- **Cloud-Specific Tools**
  - AWS: Prowler, CloudMapper, Pacu
  - Azure: Azucar, MicroBurst
  - GCP: G-Scout, GCP Scanner
- **Container Security**
  - Image Scanning: Trivy, Clair, Anchore
  - Runtime: Falco, Sysdig*
  - Kubernetes: kube-bench, kube-hunter

### 9.9 Wireless Security Tools
- **WiFi Tools**
  - Aircrack-ng suite
  - Kismet, WiFite2
  - Reaver, Bully (WPS attacks)
  - Evil Twin: Fluxion, Wifiphisher
- **Bluetooth Tools**
  - BlueZ, Blueman
  - BTScanner, Bluesnarfer
  - Ubertooth One (hardware)
- **Radio/SDR Tools**
  - GNU Radio, GQRX
  - RTL-SDR, HackRF
  - Universal Radio Hacker

### 9.10 Mobile Security Tools
- **Android Tools**
  - Static: APKTool, JADX, MobSF
  - Dynamic: Frida, Objection
  - Network: Android Debug Bridge (ADB)
- **iOS Tools**
  - Jailbreaking: checkra1n, unc0ver
  - Analysis: Needle, idb
  - Runtime: Cycript, Frida

### 9.11 OSINT Tools
- **Search & Reconnaissance**
  - Google Dorking, Shodan, Censys
  - theHarvester, SpiderFoot
  - Maltego*, OSINT Framework
- **Social Media OSINT**
  - Sherlock, Social Searcher
  - TweetDeck, Twint
  - Instagram-scraper, fb-sleep
- **Domain/DNS Intel**
  - DNSrecon, DNSenum
  - Fierce, Amass
  - Sublist3r, Subfinder

### 9.12 Hardware & Physical Security Tools
- **USB Attacks**
  - Rubber Ducky, Bash Bunny*
  - P4wnP1, Poisontap
  - USBKill, USBGuard
- **RFID/NFC Tools**
  - Proxmark3, ChameleonMini
  - ACR122U, MFCUK
  - NFCpy, LibNFC
- **Hardware Analysis**
  - Logic Analyzers: Saleae*, PulseView
  - JTAG/Debug: OpenOCD, J-Link*
  - Chip-off: FlashcatUSB, CH341A

### 9.13 Binary Analysis & RE Tools
- **Disassemblers/Decompilers**
  - Industry Standard: IDA Pro*
  - Free: Ghidra, Radare2/Cutter
  - x64dbg, OllyDbg (Windows)
- **Binary Analysis**
  - Static: PEiD, Detect It Easy
  - Dynamic: Process Monitor, API Monitor
  - Packing: UPX, VMProtect*
- **Malware Analysis**
  - Sandboxes: Cuckoo, CAPE
  - Online: VirusTotal, Hybrid Analysis
  - Memory: Volatility, YARA

### 9.14 Development Security Tools
- **SAST (Static Analysis)**
  - Commercial: Checkmarx*, Fortify*, Veracode*
  - Open Source: SonarQube, Semgrep
  - Language-specific: Bandit (Python), Brakeman (Ruby)
- **DAST (Dynamic Analysis)**
  - OWASP ZAP, Arachni
  - Nikto, Wapiti
- **Dependency Scanning**
  - Snyk*, WhiteSource*
  - OWASP Dependency Check
  - npm audit, pip-audit

### 9.15 Privacy & Anonymity Tools
- **Anonymity Networks**
  - Tor Browser, Whonix
  - I2P, Freenet
  - VPN comparison tools
- **Privacy Tools**
  - Tails OS, Qubes OS
  - VeraCrypt, GnuPG
  - Signal, Element (messaging)

### 9.16 Security Distributions
- **Offensive Distributions**
  - Kali Linux (standard)
  - Parrot Security OS
  - BlackArch, Pentoo
- **Defensive Distributions**
  - Security Onion (NSM)
  - SANS SIFT (Forensics)
  - REMnux (Malware analysis)
- **Privacy Distributions**
  - Tails, Whonix
  - Kodachi, Qubes OS

### 9.17 Knowledge Resources
- **News & Threat Intelligence**
  - Breaking News: Krebs on Security, The Register, BleepingComputer
  - Threat Intel: Threatpost, Dark Reading, SecurityWeek
  - Vendor Blogs: Talos (Cisco), Unit42 (Palo Alto), X-Force (IBM)
  - Research Teams: Google Project Zero, Trail of Bits
- **Technical Blogs**
  - Offensive: Pentester's Blog, HackTricks, PayloadsAllTheThings
  - Defensive: SANS ISC, Windows Security Blog
  - Malware: Malware Traffic Analysis, VX-Underground
  - General: Troy Hunt, Daniel Miessler, Graham Cluley
- **Podcasts**
  - Story-driven: Darknet Diaries, Malicious Life
  - News: Security Now!, Risky Business
  - Technical: Paul's Security Weekly, SANS podcasts
  - Industry: CyberWire Daily, Smashing Security
- **YouTube Channels**
  - Beginner: NetworkChuck, Professor Messer
  - Offensive: IppSec, John Hammond, The Cyber Mentor
  - Binary/RE: LiveOverflow, OALabs, Guided Hacking
  - General: Computerphile, Hak5
- **Documentation & References**
  - MITRE ATT&CK, NIST Frameworks
  - OWASP Guides, CIS Benchmarks
  - RFC Documents, CVE Database
  - Exploit-DB, SecLists
- **Books & Publications**
  - Foundational: The Web Application Hacker's Handbook
  - Offensive: Red Team Field Manual, Hacking: The Art of Exploitation
  - Defensive: Blue Team Handbook, Applied Network Security Monitoring
  - Specialized: Practical Malware Analysis, The Hardware Hacking Handbook

### 9.18 Reference Materials
- **Cheat Sheets**
  - SANS Cheat Sheets (free PDFs)
  - Penetration Testing Cheat Sheets
  - Reverse Engineering Cheat Sheets
  - Forensics Quick Reference Guides
- **Methodology Guides**
  - PTES (Penetration Testing Execution Standard)
  - OWASP Testing Guide
  - NIST Incident Response Guide
  - MITRE ATT&CK Navigator
- **Standards & Frameworks**
  - ISO 27001/27002
  - NIST Cybersecurity Framework
  - CIS Controls
  - PCI-DSS Requirements
- **Tool Documentation**
  - Official Tool Wikis
  - Community Guides
  - Video Tutorials
  - Example Use Cases

### 9.19 Career Resources
- **Job Boards**
  - General: Indeed, LinkedIn, Dice
  - Security-Specific: CyberSeek, CyberSecJobs, InfoSec-Jobs
  - Clearance Required: ClearanceJobs
  - Remote: Remote.co, We Work Remotely
- **Resume & Portfolio**
  - Resume Templates
  - GitHub Portfolio Examples
  - LinkedIn Optimization
  - Cover Letter Guides
- **Interview Preparation**
  - Common Security Questions
  - Technical Challenges
  - Behavioral Questions
  - Salary Negotiation
- **Career Development**
  - Career Roadmaps
  - Skill Gap Analysis
  - Mentorship Programs
  - Performance Reviews
- **Freelancing & Consulting**
  - Bug Bounty Platforms (HackerOne, Bugcrowd)
  - Consulting Guides
  - Rate Setting
  - Client Management
- **Salary Intelligence**
  - Real Salary Data by Role/Region
  - Compensation Surveys
  - Negotiation Strategies
  - Total Comp Calculators
- **Company Profiles**
  - Security Team Structures (FAANG, Banks, etc.)
  - "Day in the Life" Content
  - Interview Processes
  - Culture & Work-Life Balance

## 4. Certifications

### 4.1 Entry Level
- CompTIA (Security+, Network+, A+)
- (ISC)² CC
- Google Cybersecurity Certificate
- Microsoft Security Fundamentals

### 4.2 Vendor-Specific
- Cisco (CCNA Security, CyberOps)
- Palo Alto (PCNSA, PCNSE)
- Fortinet (NSE)
- Check Point (CCSA, CCSE)
- Splunk Certifications
- AWS Security
- Azure Security
- GCP Security

### 4.3 Offensive Security
- Offensive Security (OSCP, OSEP, OSWE)
- SANS Offensive (GPEN, GWAPT, GXPN)
- EC-Council (CEH, LPT)
- eLearnSecurity (eJPT, eCPPT)

### 4.4 Defensive Security
- SANS Defensive (GSEC, GCIH, GNFA)
- CySA+
- Blue Team Certifications
- SOC Analyst Certifications

### 4.5 Management & Governance
- CISSP
- CISM
- CISA
- CRISC
- CGRC

### 4.6 Specialized Certifications
- Cloud Security (CCSP, CCSK)
- ICS/SCADA (GICSP, ICS410)
- Privacy (CIPP, CIPM, CIPT)
- Forensics (GCFA, GNFA, CCE)

## 5. Learning Platforms

### 5.1 General Platforms
- Multi-Domain Training
- Certification Prep
- Virtual Labs
- Video Courses

### 5.2 Offensive Security Platforms
- CTF Platforms
- Vulnerable Apps/VMs
- Bug Bounty Training
- Exploit Development

### 5.3 Defensive Security Platforms
- Blue Team Labs
- SOC Simulations
- Incident Response
- Threat Hunting

### 5.4 Specialized Training
- Cloud Security Labs
- ICS/SCADA Simulators
- Mobile Security
- IoT Security

## 6. Communities

### 6.1 Geographic Communities
- 2600 Meetings (Worldwide)
- DEF CON Groups
- OWASP Chapters
- ISC2 Chapters
- ISACA Chapters
- InfraGard
- Hackerspaces

### 6.2 Online Communities
- Forums
- Discord Servers
- Slack Workspaces
- Reddit Communities
- IRC Channels
- Matrix Rooms
- Telegram Groups

### 6.3 Professional Associations
- Information Security
- Digital Forensics
- Privacy Professionals
- Audit & Compliance

### 6.4 Special Interest Groups
- Women in Cybersecurity
- Minorities in Cybersecurity
- Veterans in Security
- Students Groups
- LGBTQ+ in Tech

### 6.5 International Communities
- Language-Specific
- Region-Specific
- Country-Specific

## 7. Conferences & Events

### 7.1 Major Conferences
- DEF CON
- Black Hat
- RSA Conference
- ShmooCon
- CanSecWest

### 7.2 Regional Conferences
- BSides (All Cities)
- Regional Security Cons
- University Conferences

### 7.3 Specialized Conferences
- AppSec Conferences
- ICS Security
- Cloud Security
- Privacy Conferences

### 7.4 Virtual Events
- Online Conferences
- Webinar Series
- Virtual Villages

### 7.5 Competitions
- CTF Calendar
- Bug Bounty Events
- Hackathons
- Cyber Ranges

## 8. Formal Education

### 8.1 University Programs
- Bachelor's Degrees
- Master's Programs
- PhD Programs
- Certificate Programs

### 8.2 Online Degrees
- WGU Programs
- SANS Degrees
- Other Online Programs

### 8.3 Bootcamps
- Intensive Programs
- Part-Time Options
- Career Change Programs

### 8.4 Scholarships & Funding
- Scholarship Programs
- Grants
- Employer Funding
- Government Programs

## 11. Site Features & Functionality

### 11.1 Interactive Features
- **Community Map**
  - Geographic location of all physical communities
  - Address search and proximity finder
  - Meeting schedules and access requirements
  - Virtual meeting links
- **Dynamic Event Calendar**
  - Conference dates and CFPs
  - Local meetup schedules
  - Training course dates
  - Competition deadlines
- **Resource Rating System**
  - 5-star rating system
  - User comments/reviews
  - Difficulty ratings (Beginner to Expert)
  - Time investment indicators
- **Personalized Learning Paths**
  - Skill assessment quiz
  - Custom roadmap generator
  - Progress tracking
  - Certificate tracker

### 11.2 Search & Filter Functions
- **Advanced Search**
  - By domain/subdomain
  - By skill level
  - By cost (Free/Paid/Freemium)
  - By resource type
  - By update frequency
- **Smart Filters**
  - "Show only free resources"
  - "Beginner-friendly only"
  - "Recently updated"
  - "Highly rated (4+ stars)"
  - "Near me" (for physical resources)

### 11.3 User Features
- **User Accounts**
  - Save favorites
  - Track progress
  - Custom learning paths
  - Achievement badges
- **Community Contributions**
  - Submit new resources
  - Update existing entries
  - Report broken links
  - Suggest categories

## Resource Notation Key

### Simplified Notation System
The site uses a clear notation system to indicate pricing and access requirements:

**Core Notations (mutually exclusive):**
- **No symbol** = Completely free and open source (no registration, no limits)
- **(F)** = Freemium (has free tier + paid upgrades)
- **($)** = Paid only (no free option)
- **(E)** = Enterprise pricing (contact sales)

**Status Modifiers (can combine):**
- **†** = Registration required (even for free tier)
- **[BETA]** = Beta/preview status
- **[EOL]** = End of life/deprecated

### Examples
- `Nmap` - Fully free and open source
- `Burp Suite (F)†` - Freemium with registration required
- `Nessus ($)` - Paid only, no free version
- `Qualys VMDR (E)` - Enterprise pricing

### Implementation
All resources in JSON files should include:
```json
{
  "name": "Tool Name",
  "type": "freemium",
  "notation": "(F)†",
  "pricingNote": "Free tier: 100 scans/month, Pro: $49/month",
  "description": "Tool description"
}
```

### Contributor Guidelines
When adding resources, determine notation by:
1. Is it completely free with no registration? → No symbol
2. Does it have both free and paid tiers? → (F)
3. Does the free tier require registration? → (F)†
4. Is it paid only with no free option? → ($)
5. Is it enterprise/custom pricing only? → (E)

## Organizational Structure

### Security Tools Organization
The Security Tools section is organized following the MITRE ATT&CK framework phases:
- **Assessment & Testing**: Reconnaissance, Vulnerability Scanning, Web Testing, Network Testing, Penetration Testing, OSINT, API Security
- **Monitoring & Detection**: SIEM Platforms, Network Monitoring, Endpoint Detection, Threat Intelligence
- **Response & Analysis**: Incident Response, Digital Forensics, Malware Analysis, Log Analysis
- **Specialized Domains**: Cloud, Mobile, ICS/SCADA, Wireless, Hardware, Cryptography, DevSecOps, Container Security, Supply Chain, Zero Trust, AI/ML Security

### Additional Top-Level Sections
- **Compliance & Standards**: PCI-DSS, HIPAA, GDPR, ISO 27001, SOC 2
- **Vulnerability Intelligence**: CVE Databases, Exploit Databases, Vulnerability Feeds, Bug Bounty Platforms
- **Security Distributions**: Offensive Security, Defensive Security, Privacy Focused

## Terminal Aesthetic Implementation

### CSS Variables
```css
:root {
  /* Terminal colors based on Dracula theme */
  --term-bg: #282a36;
  --term-current-line: #44475a;
  --term-selection: #44475a;
  --term-fg: #f8f8f2;
  --term-comment: #6272a4;
  --term-cyan: #8be9fd;
  --term-green: #50fa7b;
  --term-orange: #ffb86c;
  --term-pink: #ff79c6;
  --term-purple: #bd93f9;
  --term-red: #ff5555;
  --term-yellow: #f1fa8c;
  
  /* Functional colors */
  --bg-primary: var(--term-bg);
  --text-primary: var(--term-fg);
  --text-muted: var(--term-comment);
  --accent: var(--term-green);
  --danger: var(--term-red);
  --warning: var(--term-yellow);
  
  /* Typography */
  --font-mono: 'Fira Code', 'JetBrains Mono', monospace;
  
  /* Effects */
  --glow-green: 0 0 10px var(--term-green);
  --scanline-opacity: 0.03;
}
```

## Development Phases

### Phase 1: Static Foundation (v1.0)
- Pure static site with Astro
- All content in Markdown files  
- Client-side search with Pagefind
- Zero JavaScript except for search
- Community contributions via GitHub PRs

### Phase 2: Enhanced Interactivity (v2.0)
- Add user ratings and reviews
- Implement API routes in Astro
- Integrate Supabase for review storage
- Progressive enhancement (site works without JS)
- Real-time statistics and popular resources

### Phase 3: Community Features (v3.0)
- User accounts (optional)
- Bookmarking and progress tracking
- Personalized learning paths
- Community-submitted resources with moderation
- Advanced filtering and recommendations

## Configuration Files

### astro.config.mjs
```javascript
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import mdx from '@astrojs/mdx';
import react from '@astrojs/react';

export default defineConfig({
  integrations: [
    tailwind(),
    mdx(),
    react(), // For interactive islands only
  ],
  markdown: {
    shikiConfig: {
      theme: 'dracula',
      wrap: true
    }
  },
  output: 'static', // Phase 1
  // output: 'hybrid', // Phase 2+ for API routes
});
```

## Development Workflow

### Setup & Installation

```bash
# Clone repository
git clone https://github.com/dcbokonon/secref.git
cd secref

# Set up Python environment for admin panel
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r admin/requirements.txt

# Set up Node environment for Astro site
nvm use  # Uses .nvmrc (Node v20)
npm install

# Copy and configure environment
cp .env.example .env
# Edit .env with your secret key and admin password hash

# Initialize database
python scripts/db_config_sqlite.py
python scripts/import_json_to_sqlite.py
```

### Development Commands

```bash
# Astro site development
npm run dev              # Start Astro dev server
npm run build           # Build static site
npm run preview         # Preview production build

# Admin panel development
cd admin && flask run   # Start Flask admin panel

# Database operations
python scripts/import_json_to_sqlite.py  # Import JSON → SQLite
python scripts/export_sqlite_to_json.py  # Export SQLite → JSON

# Testing
python -m pytest tests/  # Run all tests
python -m pytest tests/test_database.py -v  # Run specific test

# Docker operations
docker-compose up -d    # Start all services
docker-compose down     # Stop services
docker-compose logs -f  # View logs

# Make commands
make dev               # Start development servers
make test              # Run all tests
make lint              # Run linters
make format            # Format code
make security-check    # Run security scans
```

### Git Workflow

1. **Never commit directly to main** - Use feature branches
2. **Run pre-commit hooks** - Automatically checks security and formatting
3. **Test before pushing** - Ensure all tests pass
4. **Use conventional commits** - feat:, fix:, docs:, etc.
5. **PR workflow** - All changes via pull requests

## Content Structure

### MDX Frontmatter Schema
```typescript
interface ResourceFrontmatter {
  title: string
  description: string
  category: string
  subcategory: string
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  tags: string[]
  tools?: {
    name: string
    url: string
    type: 'free' | 'paid' | 'freemium'
  }[]
  updated: string // ISO date
  contributors: string[] // GitHub usernames
}
```

## Performance Targets
- Page load time: <2 seconds
- Search response: <100ms
- Build time: <5 minutes
- Deployment time: <2 minutes
- Monthly hosting cost: <$15
- Lighthouse scores: 95+ across all metrics

## Future Expansion Options

With Next.js, these features can be added without restructuring:

1. **User Features** (if needed later)
   - Authentication via NextAuth
   - Personal resource collections
   - Progress tracking

2. **Dynamic Content**
   - API routes for tool status
   - Real-time vulnerability feeds
   - Community voting system

3. **Interactive Tools**
   - Encoding/decoding utilities
   - Hash calculators
   - Subnet calculators

4. **Advanced Search**
   - Faceted search
   - Search analytics
   - AI-powered recommendations

## Security Considerations
- No database = no SQL injection
- No server-side code = minimal attack surface
- All user input sanitized by React
- Content Security Policy headers
- Regular dependency audits
- Signed commits required

## Security Implementation

### Security Measures Implemented

1. **Authentication System**
   - Flask-Login with secure session management
   - Werkzeug password hashing (pbkdf2:sha256)
   - Environment-based credential configuration
   - No default credentials

2. **Input Protection**
   - Bleach HTML sanitization on all text inputs
   - URL validation preventing javascript: and data: URLs
   - Parameterized SQL queries (no string concatenation)
   - File upload restrictions

3. **Session Security**
   - Secure session cookies (httponly, samesite=lax)
   - CSRF tokens on all forms
   - Session timeout and forced re-authentication
   - Rate limiting on login attempts

4. **Infrastructure Security**
   - HTTPS enforced via Caddy
   - Security headers (CSP, HSTS, X-Frame-Options)
   - Docker containers run as non-root user
   - No sensitive data in version control

5. **Monitoring & Audit**
   - All database changes logged
   - Failed login attempts tracked
   - Export/import operations audited
   - Resource health monitoring

### Recent Security Updates (2024)

- Complete security audit and hardening of admin panel
- Implementation of CSRF protection across all forms
- Addition of input validation and sanitization layer
- Rate limiting on all API endpoints
- Secure session management with Flask-Login
- Pre-commit hooks for security scanning (bandit, safety)
- Removal of all test/debug code from production
- Enhanced .gitignore to prevent credential leaks

## Framework Decision Rationale

### Why SQLite Over PostgreSQL:
- **Zero Dependencies**: No separate database server required
- **Simplicity**: "Rock solid design, not cutting edge niche bullshit"
- **Portability**: Single file database, easy backups
- **Performance**: More than adequate for admin operations
- **Git Workflow**: JSON files remain source of truth for contributions

### Why Dual Architecture (Astro + Flask):
1. **Separation of Concerns**: Public site has zero auth overhead
2. **Performance**: Static site can be heavily cached
3. **Security**: Admin panel completely isolated from public
4. **Flexibility**: Can scale each component independently
5. **Developer Experience**: Frontend devs work on Astro, backend on Flask

### Why Astro Over Next.js:
1. **Performance**: Zero JavaScript by default - only loads JS where needed
2. **Simplicity**: Contributors write plain Markdown, no React knowledge required
3. **Build Speed**: Faster than Next.js for thousands of content pages
4. **Progressive Enhancement**: Can start 100% static, add dynamic features later
5. **Best of Both Worlds**: Static site performance with dynamic capabilities when needed

### Why Astro Over Hugo:
1. **Future Flexibility**: Easy to add user reviews, ratings, and API routes
2. **Modern Ecosystem**: Access to npm packages and React components when needed
3. **No Migration Required**: Can evolve from static to dynamic within same framework
4. **Familiar to JavaScript Developers**: Easier to find contributors

## Current State

### Implemented Features

**Public Site (Astro)**
- Homepage with expandable directory tree structure
- Terminal-inspired design with monospace fonts
- Resource categorization by purpose (Assessment, Monitoring, Response, etc.)
- Inline tool previews showing top resources per category
- Community favorite and industry standard badges
- Static JSON-based content management

**Admin Panel (Flask)**
- Secure authentication with session management
- Full CRUD operations for resources
- Multi-category assignment with primary designation
- Bulk operations (type updates, category changes, deletion)
- Resource health dashboard showing quality metrics
- Database/JSON synchronization with conflict detection
- Audit logging for all changes
- CSRF protection on all forms
- Input validation and sanitization

**Infrastructure**
- Docker containerization with multi-stage builds
- Caddy web server with automatic HTTPS
- Comprehensive security headers
- GitHub Actions CI/CD pipeline
- Pre-commit hooks for code quality
- Comprehensive test suite (database, API, UI)

### Next Steps

1. Complete Astro site implementation with all categories
2. Implement search functionality with Pagefind
3. Add resource detail pages
4. Deploy to production server
5. Open for community contributions

## Repository Information

- **Repository**: https://github.com/dcbokonon/secref/
- **Domain**: secref.org
- **Server**: 149.28.63.158 (Vultr VPS)
- **Contact**: 
  - security@secref.org → dcbokonon@gmail.com
  - api@secref.org → dcbokonon@gmail.com
  - support@secref.org → dcbokonon@gmail.com
  - contribute@secref.org → dcbokonon@gmail.com

### Implemented Features:
- **Homepage** with terminal-inspired design (green text on black background)
- **Navigation** simplified to 5 main sections: home, tools, learn, events, groups  
- **Industry-Standard Organization** - Tools organized using MITRE ATT&CK and NIST frameworks
- **Collapsible Sections** - Security tools and learning resources start collapsed for better UX
- **Upcoming Events** section with conferences, CFPs, competitions, and training deadlines (expanded by default)
- **Local Groups** section for finding cybersecurity meetups and communities (expanded by default)
- **No Search Box** - users can use browser's Ctrl+F for finding content
- **Framework References** - MITRE tactics/techniques and NIST functions labeled throughout

### Recent Changes:
- Replaced generic "phases" with proper industry frameworks
- Offensive tools now organized by MITRE ATT&CK tactics (TA0043 for Reconnaissance, TA0001 for Initial Access, etc.)
- Defensive tools organized by NIST Cybersecurity Framework functions (ID, PR, DE, RS, RC)
- Added technique-level detail with MITRE IDs (T1595 for Active Scanning, T1596 for Search Open Technical Databases, etc.)
- Specialized domains organized by common industry categories (Cloud Security, Application Security, Mobile Security, etc.)
- All categorization now aligns with how security professionals actually reference and use these tools

## Homepage Hierarchical Structure

The homepage uses a natural, hierarchical organization that reflects how security professionals categorize tools and resources.

### Security Tools (892 tools)

#### Reconnaissance & Information Gathering
- **Network Discovery**
  - Port Scanners (12)
  - Host Discovery (8)
  - Service Enumeration (15)
  - OS Fingerprinting (7)
- **OSINT (Open Source Intelligence)**
  - Search Engines & Dorking (14)
  - Social Media Analysis (22)
  - People & Identity (18)
  - Domain & DNS Intel (16)
  - Metadata Analysis (9)
  - Dark Web Monitoring (7)

#### Vulnerability Assessment
- **Vulnerability Scanners**
  - Network Vuln Scanners (11)
  - Web App Scanners (19)
  - Database Scanners (8)
  - Container Scanners (12)
- **Configuration & Compliance**
  - Configuration Auditing (14)
  - Security Benchmarks (9)
  - Compliance Scanning (11)

#### Exploitation & Penetration Testing
- **Exploitation Frameworks**
  - General Frameworks (8)
  - Web Exploitation (24)
  - Network Exploitation (16)
  - Wireless Exploitation (13)
- **Post-Exploitation**
  - Command & Control (C2) (15)
  - Persistence Tools (11)
  - Lateral Movement (9)
  - Privilege Escalation (18)
  - Data Exfiltration (7)
- **Platform-Specific**
  - Windows Tools (32)
  - Linux Tools (28)
  - macOS Tools (14)
  - Mobile Tools (26)
  - Cloud Tools (23)

#### Defense & Monitoring
- **Network Defense**
  - Firewalls (16)
  - IDS/IPS Systems (14)
  - Honeypots & Deception (12)
  - Network Access Control (8)
- **Security Monitoring**
  - SIEM Platforms (15)
  - Log Management (19)
  - Network Flow Analysis (11)
  - Endpoint Detection (EDR) (13)
- **Threat Intelligence**
  - TI Platforms (12)
  - Threat Feeds (18)
  - IOC Management (9)
  - Threat Hunting (11)

#### Forensics & Incident Response
- **Digital Forensics**
  - Disk Forensics (16)
  - Memory Forensics (12)
  - Network Forensics (14)
  - Mobile Forensics (11)
  - Cloud Forensics (8)
- **Incident Response**
  - Evidence Collection (15)
  - Incident Analysis (13)
  - Case Management (7)
  - IR Orchestration (9)

#### Cryptography & Privacy
- **Cryptography Tools**
  - Encryption Tools (18)
  - Password Tools (22)
  - Certificate Management (11)
  - Crypto Analysis (9)
- **Privacy & Anonymity**
  - Anonymity Networks (8)
  - VPN Tools (14)
  - Secure Messaging (12)
  - Data Sanitization (10)

#### Binary Analysis & Reverse Engineering
- **Static Analysis**
  - Disassemblers (11)
  - Decompilers (9)
  - Hex Editors (8)
  - PE Analysis (12)
- **Dynamic Analysis**
  - Debuggers (14)
  - Malware Sandboxes (10)
  - Behavior Analysis (11)
  - Unpackers (7)

#### Development Security
- **Code Analysis**
  - SAST Tools (21)
  - DAST Tools (16)
  - IAST Tools (8)
  - Software Composition (14)
- **DevSecOps**
  - CI/CD Security (13)
  - Secret Scanning (11)
  - Container Security (17)
  - IaC Security (9)

#### Physical & Hardware Security
- **Hardware Hacking**
  - USB Tools (12)
  - RFID/NFC Tools (14)
  - Software Defined Radio (11)
  - JTAG/Debug Tools (8)
- **Physical Security**
  - Lock Picking (9)
  - Access Control (11)
  - Surveillance Systems (13)

#### Security Distributions & Platforms
- **Penetration Testing**
  - Kali Linux
  - Parrot Security
  - BlackArch
  - Pentoo
- **Defensive & Forensics**
  - Security Onion
  - SANS SIFT
  - REMnux
  - CAINE
- **Privacy Focused**
  - Tails
  - Whonix
  - Qubes OS
  - Kodachi

### Learning Resources (1,247 resources)

Organized with natural depth based on content availability:

#### Certifications
- Entry Level
- Offensive Security
- Defensive Security
- Management & Governance
- Specialized Certifications

#### Training Platforms
- Hands-On Labs
- CTF Platforms
- Video Courses
- Interactive Learning

#### Documentation & References
- Methodology Guides
- Cheat Sheets
- Standards & Frameworks
- Best Practices

### Upcoming Events (87 events)

Real-time updated calendar:
- Conferences
- CFP Deadlines
- Competitions
- Training Deadlines

### Local Groups (342 groups)

Community resources:
- Physical Meetups
- Online Communities
- Professional Associations
- Special Interest Groups

### Practice Resources (418 resources)

Hands-on learning:
- Vulnerable Applications
- CTF Challenges
- Virtual Labs
- Capture The Flag

### Career Resources (298 resources)

Professional development:
- Job Boards
- Interview Preparation
- Career Paths
- Salary Intelligence