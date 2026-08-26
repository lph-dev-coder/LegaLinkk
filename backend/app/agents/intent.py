"""Keyword-based intent detection for agent routing."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IntentMatch:
    """Detected domains for a user question."""

    domains: tuple[str, ...]
    keywords_hit: tuple[str, ...]
    #: Number of keyword hits per domain (only domains with hits > 0).
    domain_scores: dict[str, int]


# Domain → trigger keywords (matched as whole words / phrases, case-insensitive).
DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "legal": (
        "clause",
        "clauses",
        "obligation",
        "obligations",
        "liability",
        "liabilities",
        "contract",
        "contracts",
        "warranty",
        "warranties",
        "indemnity",
        "termination",
        "breach",
        "legal",
        "law",
        "rights",
        "duty",
        "duties",
        "contrat",
        "contrats",
        "juridique",
        "juridiques",
        "juridiquement",
        "loi",
        "droit",
        "droits",
        "légal",
        "légale",
        "legale",
        "légaux",
        "legaux",
        "résiliation",
        "resiliation",
        "résilier",
        "resilier",
        "préavis",
        "preavis",
        "responsabilité",
        "responsabilite",
        "validité",
        "validite",
        "valable",
        "nul",
        "nulle",
        "nullité",
        "nullite",
        "ordre public",
        "juridiction",
        "tribunal",
        "litige",
        "litiges",
        "contentieux",
        "avocat",
        "avenant",
        "signataire",
        "cession",
        "article",
        "articles",
        "unilatéral",
        "unilateral",
        "unilatéralement",
        "unilateralement",
        "indemnisation",
        "garantie",
        "garanties",
        "force majeure",
        "propriété intellectuelle",
        "propriete intellectuelle",
    ),
    "finance": (
        "payment",
        "payments",
        "invoice",
        "invoices",
        "penalty",
        "penalties",
        "pricing",
        "price",
        "fee",
        "fees",
        "cost",
        "costs",
        "amount",
        "amounts",
        "interest",
        "finance",
        "financial",
        "financier",
        "financière",
        "financiere",
        "financiers",
        "financières",
        "financieres",
        "fiscal",
        "fiscale",
        "rentabilité",
        "rentabilite",
        "marge",
        "budget",
        "refund",
        "paiement",
        "paiements",
        "facture",
        "factures",
        "montant",
        "montants",
        "prix",
        "tarif",
        "tarifs",
        "coût",
        "cout",
        "coûts",
        "couts",
        "pénalité",
        "penalite",
        "pénalités",
        "penalites",
        "intérêt",
        "interet",
        "intérêts",
        "interets",
        "échéance",
        "echeance",
        "échéancier",
        "echeancier",
        "devise",
        "remboursement",
        "honoraires",
        "indexation",
        "révision des prix",
        "revision des prix",
        "plafond",
        "plafonds",
        "cap",
        "liability cap",
    ),
    "compliance": (
        "gdpr",
        "compliance",
        "regulation",
        "regulations",
        "iso",
        "privacy",
        "rgpd",
        "regulatory",
        "audit",
        "policy",
        "policies",
        "standard",
        "standards",
        "data protection",
        "conformité",
        "conformite",
        "réglementation",
        "reglementation",
        "réglementaire",
        "reglementaire",
        "données personnelles",
        "donnees personnelles",
        "protection des données",
        "protection des donnees",
        "traitement des données",
        "traitement des donnees",
        "sous-traitant",
        "confidentialité",
        "confidentialite",
        "sécurité",
        "securite",
        "autorité de contrôle",
        "autorite de controle",
        "cnil",
        "cnpd",
        "certification",
    ),
}

DOMAIN_TO_AGENT: dict[str, str] = {
    "legal": "LegalAgent",
    "finance": "FinanceAgent",
    "compliance": "ComplianceAgent",
}


class IntentRouter:
    """Detect which agent domains a query touches."""

    def detect(self, query: str) -> IntentMatch:
        text = (query or "").strip().lower()
        if not text:
            return IntentMatch(domains=(), keywords_hit=(), domain_scores={})

        scores: dict[str, int] = {}
        hits: list[str] = []

        for domain, keywords in DOMAIN_KEYWORDS.items():
            matched = [kw for kw in keywords if self._contains(text, kw)]
            if matched:
                scores[domain] = len(matched)
                hits.extend(matched)

        # Stable order: highest score first, then name for ties.
        ordered = tuple(
            domain
            for domain, _ in sorted(
                scores.items(), key=lambda item: (-item[1], item[0])
            )
        )
        return IntentMatch(
            domains=ordered,
            keywords_hit=tuple(hits),
            domain_scores=scores,
        )

    def agent_names_for(self, query: str) -> list[str]:
        """Map detected domains to agent class names."""
        match = self.detect(query)
        return [DOMAIN_TO_AGENT[d] for d in match.domains if d in DOMAIN_TO_AGENT]

    @staticmethod
    def _contains(text: str, keyword: str) -> bool:
        if " " in keyword:
            return keyword in text
        return re.search(rf"\b{re.escape(keyword)}\b", text) is not None
