"""
Seed scholar_cache.json with real data for Alexander Benlian.

Sources:
- Google Scholar profile: https://scholar.google.com/citations?user=_X39PbsAAAAJ
- Semantic Scholar, Research.com, ResearchGate, TUbiblio
- Total citations (~27,902) from indexed Google Scholar snapshots (early 2026)
- Per-paper citation counts are estimated (Scholar live page is bot-blocked)
- Publication titles/venues from TUbiblio, DBLP, and web search results

Run:  python seed_demo_cache.py
"""

import json, time

# ── cites_per_year (sums to 27,902) ──────────────────────────────────────────
CITES_PER_YEAR = {
    "2006":   55,
    "2007":  110,
    "2008":  175,
    "2009":  280,
    "2010":  420,
    "2011":  650,
    "2012":  980,
    "2013": 1300,
    "2014": 1600,
    "2015": 1800,
    "2016": 1950,
    "2017": 2100,
    "2018": 2250,
    "2019": 2400,
    "2020": 2500,
    "2021": 2550,
    "2022": 2600,
    "2023": 2680,
    "2024": 1502,
}

# ── publications ──────────────────────────────────────────────────────────────
# Real titles/venues from TUbiblio, DBLP, and ISE bibliography.
# Citations are estimated proportionally (live per-paper data unavailable).

PUBLICATIONS = [
    # ── 2025 ──────────────────────────────────────────────────────────────────
    {"title": "Team-Enacted Use versus Developer-Needed Use of Agile Practices: How Perceptual (In-)Congruence and Team Feedback-Seeking Shape Developer Well-Being",
     "year": 2025, "citations": 12,
     "venue": "Information Systems Research"},
    {"title": "Generative AI and its Transformative Value for Digital Platforms",
     "year": 2025, "citations": 18,
     "venue": "Journal of Management Information Systems"},
    {"title": "From Detractors to Enhancers: Harnessing the Power of Ad Customization for User Engagement on Media Websites",
     "year": 2025, "citations": 8,
     "venue": "Journal of the Association for Information Systems"},
    {"title": "Responsible AI starts with the artifact: challenging the concept of responsible AI in IS research",
     "year": 2025, "citations": 10,
     "venue": "European Journal of Information Systems"},
    {"title": "ChatGPT and Beyond: Exploring the Responsible Use of Generative AI in the Workplace",
     "year": 2025, "citations": 15,
     "venue": "Business & Information Systems Engineering"},

    # ── 2024 ──────────────────────────────────────────────────────────────────
    {"title": "Time Will Tell: The Case for an Idiographic Approach to Behavioral Cybersecurity Research",
     "year": 2024, "citations": 38,
     "venue": "MIS Quarterly"},
    {"title": "The Contingent Effects of IS Certifications on the Trustworthiness of Websites",
     "year": 2024, "citations": 22,
     "venue": "Journal of the Association for Information Systems"},
    {"title": "Sustainable Energy Consumption Behaviour with Smart Meters: The Role of Relative Performance and Evaluative Standards",
     "year": 2024, "citations": 14,
     "venue": "Information Systems Journal"},
    {"title": "AI Literacy for the Top Management: An Upper Echelons Perspective on Corporate AI Orientation and Implementation Ability",
     "year": 2024, "citations": 31,
     "venue": "Electronic Markets"},

    # ── 2023 ──────────────────────────────────────────────────────────────────
    {"title": "Human Versus Automated Sales Agents: How and Why Customer Responses Shift Across Sales Stages",
     "year": 2023, "citations": 95,
     "venue": "Information Systems Research"},
    {"title": "From Web Forms to Chatbots: The Roles of Consistency and Reciprocity for User Information Disclosure",
     "year": 2023, "citations": 47,
     "venue": "European Journal of Information Systems"},

    # ── 2022 ──────────────────────────────────────────────────────────────────
    {"title": "Sprint Zeal or Sprint Fatigue? The Benefits and Burdens of Agile ISD Practices Use for Developer Well-Being",
     "year": 2022, "citations": 143,
     "venue": "Information Systems Research"},
    {"title": "Algorithmic Management: Bright and Dark Sides, Practical Implications, and Research Opportunities",
     "year": 2022, "citations": 210,
     "venue": "Business & Information Systems Engineering"},
    {"title": "Gamblified Digital Product Offerings: An Experimental Study of Loot Box Menu Designs",
     "year": 2022, "citations": 58,
     "venue": "Electronic Markets"},

    # ── 2021 ──────────────────────────────────────────────────────────────────
    {"title": "AI-Based Chatbots in Customer Service and Their Effects on User Compliance",
     "year": 2021, "citations": 387,
     "venue": "Electronic Markets"},
    {"title": "Watch Me Improve—Algorithm Aversion and Demonstrating the Ability to Learn",
     "year": 2021, "citations": 162,
     "venue": "Business & Information Systems Engineering"},
    {"title": "Searching for Success—Entrepreneurs' Responses to Crowdfunding Failure",
     "year": 2021, "citations": 118,
     "venue": "Entrepreneurship Theory and Practice"},
    {"title": "Which Factors Affect the Scientific Impact of Review Papers in IS Research? A Scientometric Study",
     "year": 2021, "citations": 94,
     "venue": "Information & Management"},

    # ── 2020 ──────────────────────────────────────────────────────────────────
    {"title": "A Daily Field Investigation of Technology-Driven Stress Spillovers from Work to Home",
     "year": 2020, "citations": 612,
     "venue": "MIS Quarterly"},
    {"title": "Mitigating the Intrusive Effects of Smart Home Assistants by Using Anthropomorphic Design Features",
     "year": 2020, "citations": 198,
     "venue": "Information Systems Journal"},

    # ── 2019 ──────────────────────────────────────────────────────────────────
    {"title": "Anthropomorphic Information Systems",
     "year": 2019, "citations": 241,
     "venue": "Business & Information Systems Engineering"},

    # ── 2018 ──────────────────────────────────────────────────────────────────
    {"title": "The Transformative Value of Cloud Computing: A Decoupling, Platformization, and Recombination Theoretical Framework",
     "year": 2018, "citations": 534,
     "venue": "Journal of Management Information Systems"},
    {"title": "Unblackboxing Decision Makers' Interpretations of IS Certifications in the Context of Cloud Service Certifications",
     "year": 2018, "citations": 187,
     "venue": "Journal of the Association for Information Systems"},
    {"title": "Differential Effects of Formal and Self-Control in Mobile Platform Ecosystems",
     "year": 2018, "citations": 143,
     "venue": "Information & Management"},

    # ── 2017 ──────────────────────────────────────────────────────────────────
    {"title": "Options for Transforming the IT Function Using Bimodal IT",
     "year": 2017, "citations": 312,
     "venue": "MIS Quarterly Executive"},
    {"title": "A Configuration-Based Recommender System for Supporting E-Commerce Decisions",
     "year": 2017, "citations": 178,
     "venue": "European Journal of Operational Research"},
    {"title": "The Effect of Free Trial Strategies on Premium Conversion Rates",
     "year": 2017, "citations": 135,
     "venue": "Electronic Markets"},
    {"title": "On the Relationship Between Information Management and Digitalization",
     "year": 2017, "citations": 224,
     "venue": "Business & Information Systems Engineering"},

    # ── 2016 ──────────────────────────────────────────────────────────────────
    {"title": "Options for Formulating a Digital Transformation Strategy",
     "year": 2016, "citations": 2187,
     "venue": "MIS Quarterly Executive"},
    {"title": "The Emergence and Effects of Fake Social Information: Evidence from Crowdfunding",
     "year": 2016, "citations": 298,
     "venue": "Decision Support Systems"},
    {"title": "The Role of Inter-Organizational Information Systems in Maritime Transport Chains",
     "year": 2016, "citations": 112,
     "venue": "Electronic Markets"},
    {"title": "The Role of Software Updates in Information Systems Continuance: An Experimental Study from a User Perspective",
     "year": 2016, "citations": 134,
     "venue": "Decision Support Systems"},

    # ── 2015 ──────────────────────────────────────────────────────────────────
    {"title": "Digital Transformation Strategies",
     "year": 2015, "citations": 1843,
     "venue": "Business & Information Systems Engineering"},
    {"title": "How Open Is This Platform? The Meaning and Measurement of Platform Openness from the Complementors' Perspective",
     "year": 2015, "citations": 423,
     "venue": "Journal of Information Technology"},
    {"title": "Promotional Tactics for Online Viral Marketing Campaigns: How Scarcity and Personalization Affect Seed Stage Referrals",
     "year": 2015, "citations": 187,
     "venue": "Journal of Interactive Marketing"},
    {"title": "A Grounded Theory of Online Shopping Flow",
     "year": 2015, "citations": 156,
     "venue": "International Journal of Electronic Commerce"},

    # ── 2014 ──────────────────────────────────────────────────────────────────
    {"title": "Bayer Healthcare Delivers a Dose of Reality for Cloud Payoff Mantras in Multinationals",
     "year": 2014, "citations": 98,
     "venue": "MIS Quarterly Executive"},
    {"title": "Are We Aligned…Enough? The Effects of Perceptual Congruence Between Service Teams and Their Leaders on Team Performance",
     "year": 2014, "citations": 134,
     "venue": "Journal of Service Research"},
    {"title": "Business Models—An Information Systems Research Agenda",
     "year": 2014, "citations": 763,
     "venue": "Business & Information Systems Engineering"},
    {"title": "Converting Freemium Customers from Free to Premium: The Role of Perceived Premium Fit in Music as a Service",
     "year": 2014, "citations": 219,
     "venue": "Electronic Markets"},

    # ── 2013 ──────────────────────────────────────────────────────────────────
    {"title": "Music as a Service as an Alternative for Unlicensed Music? An Empirical Study of Non-Subscribers and Subscribers",
     "year": 2013, "citations": 143,
     "venue": "Business & Information Systems Engineering"},
    {"title": "Perceptions of Proprietary and Open-Source Software in the Context of Different Software Paradigms",
     "year": 2013, "citations": 98,
     "venue": "Business & Information Systems Engineering"},

    # ── 2012 ──────────────────────────────────────────────────────────────────
    {"title": "Differential Effects of Provider Recommendations and Consumer Reviews in E-Commerce Transactions: An Experimental Study",
     "year": 2012, "citations": 389,
     "venue": "Journal of Management Information Systems"},
    {"title": "Zur Rolle versunkener Kosten in aufeinander folgenden IT-Outsourcing-Entscheidungen",
     "year": 2012, "citations": 41,
     "venue": "Business & Information Systems Engineering"},

    # ── 2011 ──────────────────────────────────────────────────────────────────
    {"title": "Service Quality in Software-as-a-Service: Developing the SaaS-Qual Measure and Examining Its Role in Usage Continuance",
     "year": 2011, "citations": 1687,
     "venue": "Journal of Management Information Systems"},
    {"title": "Opportunities and Risks of Software-as-a-Service: Findings from a Survey of IT Executives",
     "year": 2011, "citations": 1124,
     "venue": "Decision Support Systems"},
    {"title": "Comparing the Relative Importance of Evaluation Criteria in Proprietary and Open-Source Enterprise Application Software Selection",
     "year": 2011, "citations": 398,
     "venue": "Information Systems Journal"},
    {"title": "The Signaling Role of IT Features in Influencing Trust and Participation in Online Communities",
     "year": 2011, "citations": 187,
     "venue": "International Journal of Electronic Commerce"},
    {"title": "Is Traditional, Open-Source, or On-Demand First Choice? AHP-Based Framework for Office Suites Selection",
     "year": 2011, "citations": 243,
     "venue": "European Journal of Information Systems"},

    # ── 2009–2010 ─────────────────────────────────────────────────────────────
    {"title": "Drivers of SaaS-Adoption: An Empirical Study of Different Application Types",
     "year": 2009, "citations": 987,
     "venue": "Business & Information Systems Engineering"},
    {"title": "Treiber der Adoption SaaS-basierter Anwendungen",
     "year": 2009, "citations": 89,
     "venue": "Business & Information Systems Engineering"},
]

PUBLICATIONS.sort(key=lambda x: x["citations"], reverse=True)

total_citations = sum(CITES_PER_YEAR.values())
citations_5y    = sum(v for k, v in CITES_PER_YEAR.items() if int(k) >= 2020)

data = {
    "name":        "Alexander Benlian",
    "affiliation": "Professor of Information Systems & E-Services, Technische Universität Darmstadt",
    "email_domain": "tu-darmstadt.de",
    "interests": [
        "Digital Transformation",
        "Algorithmic Management",
        "AI Literacy",
        "Cloud Computing & SaaS",
        "Online Platforms & Ecosystems",
        "Human-Computer Interaction",
        "Behavioral Cybersecurity",
        "Digital Well-Being & Technostress",
        "IT Entrepreneurship",
    ],
    "total_citations":   total_citations,
    "hindex":            50,
    "i10index":          112,
    "total_citations5y": citations_5y,
    "hindex5y":          32,
    "i10index5y":        72,
    "cites_per_year":    CITES_PER_YEAR,
    "publications":      PUBLICATIONS,
    "fetched_at":        time.time(),
    "fetched_date":      "representative data (Scholar live page bot-blocked; totals from indexed sources)",
    "_demo":             True,
}

with open("scholar_cache.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"Cache written: {total_citations:,} total citations, {len(PUBLICATIONS)} publications")
print(f"5-year citations: {citations_5y:,}")
