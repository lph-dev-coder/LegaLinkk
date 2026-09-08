# ScanLink Security Audit Findings Report

> Generated for AI Agent Remediation for **lph-dev-coder/LegaLinkk** on 2026-09-08 10:46:21 UTC

- **Total Issues:** 180
- **Filter Scope:** All

---

## Instructions for AI Agent
Please review the security findings listed below and generate precise code fixes for each issue.
Focus on the affected file locations, line numbers, rule IDs, and code snippets provided.

---

### Issue 1: [CRITICAL] CVE-2025-68664 in langchain-core 0.3.76
- **Category:** Dependency
- **Severity:** critical
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2025-68664`
- **CWE:** CWE-502
- **CVE:** CVE-2025-68664
- **Dependency:** langchain-core (0.3.76 → 1.2.5, 0.3.81)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
langchain-core 0.3.76 is affected by CVE-2025-68664; fixed in 1.2.5, 0.3.81. Detected in backend/poetry.lock. | langchain-core 0.3.76 (PyPI) is affected by CVE-2025-68664; fixed in 0.3.81. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
langchain-core: LangChain: Arbitrary code execution via serialization injection

#### Remediation Guidance
Upgrade langchain-core to 1.2.5, 0.3.81 or later.

---

### Issue 2: [HIGH] CVE-2025-65106 in langchain-core 0.3.76
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2025-65106`
- **CWE:** CWE-1336
- **CVE:** CVE-2025-65106
- **Dependency:** langchain-core (0.3.76 → 1.0.7, 0.3.80)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
langchain-core 0.3.76 is affected by CVE-2025-65106; fixed in 1.0.7, 0.3.80. Detected in backend/poetry.lock. | langchain-core 0.3.76 (PyPI) is affected by CVE-2025-65106; fixed in 0.3.80. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
langchain-core: LangChain Vulnerable to Template Injection via Attribute Access in Prompt Templates

#### Remediation Guidance
Upgrade langchain-core to 1.0.7, 0.3.80 or later.

---

### Issue 3: [HIGH] CVE-2026-44843 in langchain-core 0.3.76
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-44843`
- **CWE:** CWE-502
- **CVE:** CVE-2026-44843
- **Dependency:** langchain-core (0.3.76 → 1.3.3, 0.3.85)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
langchain-core 0.3.76 is affected by CVE-2026-44843; fixed in 1.3.3, 0.3.85. Detected in backend/poetry.lock. | langchain-core 0.3.76 (PyPI) is affected by CVE-2026-44843; fixed in 0.3.85. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
langchain: LangChain: Information disclosure and data integrity compromise via insecure deserialization

#### Remediation Guidance
Upgrade langchain-core to 1.3.3, 0.3.85 or later.

---

### Issue 4: [HIGH] Misconfiguration: Image user should not be 'root'
- **Category:** Misconfiguration
- **Severity:** high
- **Affected:** `backend/Dockerfile` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `DS-0002`
- **Confidence:** medium
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
DS-0002: Image user should not be 'root'

#### Impact
Running containers with 'root' user can lead to a container escape situation. It is a best practice to run containers as non-root users, which can be done by adding a 'USER' statement to the Dockerfile.

#### Remediation Guidance
Add 'USER <non root user name>' line to the Dockerfile

---

### Issue 5: [HIGH] CVE-2026-34070 in langchain-core 0.3.76
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-34070`
- **CWE:** CWE-22
- **CVE:** CVE-2026-34070
- **Dependency:** langchain-core (0.3.76 → 1.2.22)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
langchain-core 0.3.76 is affected by CVE-2026-34070; fixed in 1.2.22. Detected in backend/poetry.lock. | langchain-core 0.3.76 (PyPI) is affected by CVE-2026-34070; fixed in 1.2.22. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
langchain: path traversal in legacy load_prompt functions in langchain-core

#### Remediation Guidance
Upgrade langchain-core to 1.2.22 or later.

---

### Issue 6: [HIGH] CVE-2025-64439 in langgraph-checkpoint 2.1.2
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2025-64439`
- **CWE:** CWE-502
- **CVE:** CVE-2025-64439
- **Dependency:** langgraph-checkpoint (2.1.2 → 3.0.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
langgraph-checkpoint 2.1.2 is affected by CVE-2025-64439; fixed in 3.0.0. Detected in backend/poetry.lock. | langgraph-checkpoint 2.1.2 (PyPI) is affected by CVE-2025-64439; fixed in 3.0.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
LangGraph Checkpoint affected by RCE in "json" mode of JsonPlusSerializer

#### Remediation Guidance
Upgrade langgraph-checkpoint to 3.0.0 or later.

---

### Issue 7: [HIGH] CVE-2026-40192 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-40192`
- **CWE:** CWE-400, CWE-409, CWE-770
- **CVE:** CVE-2026-40192
- **Dependency:** pillow (11.3.0 → 12.2.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-40192; fixed in 12.2.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-40192; fixed in 12.2.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Pillow: Pillow: Denial of Service via decompression bomb in FITS image processing

#### Remediation Guidance
Upgrade pillow to 12.2.0 or later.

---

### Issue 8: [HIGH] CVE-2026-25990 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-25990`
- **CWE:** CWE-787
- **CVE:** CVE-2026-25990
- **Dependency:** pillow (11.3.0 → 12.1.1)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-25990; fixed in 12.1.1. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-25990; fixed in 12.1.1. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
pillow: Pillow: Out-of-bounds Write via Specially Crafted PSD Image

#### Remediation Guidance
Upgrade pillow to 12.1.1 or later.

---

### Issue 9: [HIGH] CVE-2026-42311 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-42311`
- **CWE:** CWE-190, CWE-787
- **CVE:** CVE-2026-42311
- **Dependency:** pillow (11.3.0 → 12.2.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-42311; fixed in 12.2.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-42311; fixed in 12.2.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Pillow: python-pillow: Pillow: Arbitrary code execution via malicious PSD file processing

#### Remediation Guidance
Upgrade pillow to 12.2.0 or later.

---

### Issue 10: [HIGH] CVE-2026-54059 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-54059`
- **CWE:** CWE-789
- **CVE:** CVE-2026-54059
- **Dependency:** pillow (11.3.0 → 12.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-54059; fixed in 12.3.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-54059; fixed in 12.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
python-pillow: Pillow: Denial of Service via crafted PCF font data

#### Remediation Guidance
Upgrade pillow to 12.3.0 or later.

---

### Issue 11: [HIGH] CVE-2026-55379 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-55379`
- **CWE:** CWE-789
- **CVE:** CVE-2026-55379
- **Dependency:** pillow (11.3.0 → 12.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-55379; fixed in 12.3.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-55379; fixed in 12.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
python-pillow: Pillow: Denial of Service via crafted BDF font file

#### Remediation Guidance
Upgrade pillow to 12.3.0 or later.

---

### Issue 12: [HIGH] CVE-2026-54058 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-54058`
- **CWE:** CWE-125
- **CVE:** CVE-2026-54058
- **Dependency:** pillow (11.3.0 → 12.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-54058; fixed in 12.3.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-54058; fixed in 12.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Pillow: Pillow: Memory disclosure or denial of service via crafted McIdas AREA image

#### Remediation Guidance
Upgrade pillow to 12.3.0 or later.

---

### Issue 13: [HIGH] CVE-2026-54060 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-54060`
- **CWE:** CWE-789
- **CVE:** CVE-2026-54060
- **Dependency:** pillow (11.3.0 → 12.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-54060; fixed in 12.3.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-54060; fixed in 12.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
python-pillow: Pillow: Denial of Service via excessive memory allocation when processing font files

#### Remediation Guidance
Upgrade pillow to 12.3.0 or later.

---

### Issue 14: [HIGH] CVE-2026-55380 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-55380`
- **CWE:** CWE-789
- **CVE:** CVE-2026-55380
- **Dependency:** pillow (11.3.0 → 12.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-55380; fixed in 12.3.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-55380; fixed in 12.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
python-pillow: Pillow: Denial of Service via crafted GD 2.x image file

#### Remediation Guidance
Upgrade pillow to 12.3.0 or later.

---

### Issue 15: [HIGH] CVE-2026-59197 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-59197`
- **CWE:** CWE-190, CWE-787
- **CVE:** CVE-2026-59197
- **Dependency:** pillow (11.3.0 → 12.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-59197; fixed in 12.3.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-59197; fixed in 12.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Pillow: Pillow: Native heap out-of-bounds write

#### Remediation Guidance
Upgrade pillow to 12.3.0 or later.

---

### Issue 16: [HIGH] CVE-2026-59200 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-59200`
- **CWE:** CWE-400, CWE-770
- **CVE:** CVE-2026-59200
- **Dependency:** pillow (11.3.0 → 12.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-59200; fixed in 12.3.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-59200; fixed in 12.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Pillow: Pillow: Denial of service via crafted PDF stream

#### Remediation Guidance
Upgrade pillow to 12.3.0 or later.

---

### Issue 17: [HIGH] CVE-2026-59205 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-59205`
- **CWE:** CWE-787
- **CVE:** CVE-2026-59205
- **Dependency:** pillow (11.3.0 → 12.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-59205; fixed in 12.3.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-59205; fixed in 12.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Pillow: Pillow: Controlled native heap corruption in ImageCms.ImageCmsTransform.apply API

#### Remediation Guidance
Upgrade pillow to 12.3.0 or later.

---

### Issue 18: [HIGH] CVE-2026-24486 in python-multipart 0.0.17
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-24486`
- **CWE:** CWE-22
- **CVE:** CVE-2026-24486
- **Dependency:** python-multipart (0.0.17 → 0.0.22)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
python-multipart 0.0.17 is affected by CVE-2026-24486; fixed in 0.0.22. Detected in backend/poetry.lock. | python-multipart 0.0.17 (PyPI) is affected by CVE-2026-24486; fixed in 0.0.22. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
python-multipart: Python-Multipart: Arbitrary file write via path traversal vulnerability

#### Remediation Guidance
Upgrade python-multipart to 0.0.22 or later.

---

### Issue 19: [HIGH] CVE-2026-59199 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-59199`
- **CWE:** CWE-190, CWE-787
- **CVE:** CVE-2026-59199
- **Dependency:** pillow (11.3.0 → 12.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-59199; fixed in 12.3.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-59199; fixed in 12.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Pillow: Pillow: Denial of Service via out-of-bounds write in image processing

#### Remediation Guidance
Upgrade pillow to 12.3.0 or later.

---

### Issue 20: [HIGH] CVE-2026-59204 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-59204`
- **CWE:** CWE-770, CWE-789
- **CVE:** CVE-2026-59204
- **Dependency:** pillow (11.3.0 → 12.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-59204; fixed in 12.3.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-59204; fixed in 12.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Pillow: Pillow: Denial of Service via crafted JPEG2000 image

#### Remediation Guidance
Upgrade pillow to 12.3.0 or later.

---

### Issue 21: [HIGH] CVE-2024-53981 in python-multipart 0.0.17
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2024-53981`
- **CWE:** CWE-770
- **CVE:** CVE-2024-53981
- **Dependency:** python-multipart (0.0.17 → 0.0.18)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
python-multipart 0.0.17 is affected by CVE-2024-53981; fixed in 0.0.18. Detected in backend/poetry.lock. | python-multipart 0.0.17 (PyPI) is affected by CVE-2024-53981; fixed in 0.0.18. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
python-multipart: python-multipart has a DoS via deformation `multipart/form-data` boundary

#### Remediation Guidance
Upgrade python-multipart to 0.0.18 or later.

---

### Issue 22: [HIGH] CVE-2026-42561 in python-multipart 0.0.17
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-42561`
- **CWE:** CWE-606, CWE-770
- **CVE:** CVE-2026-42561
- **Dependency:** python-multipart (0.0.17 → 0.0.27)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
python-multipart 0.0.17 is affected by CVE-2026-42561; fixed in 0.0.27. Detected in backend/poetry.lock. | python-multipart 0.0.17 (PyPI) is affected by CVE-2026-42561; fixed in 0.0.27. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
python-multipart: python-multipart: Denial of Service via excessive multipart part headers

#### Remediation Guidance
Upgrade python-multipart to 0.0.27 or later.

---

### Issue 23: [HIGH] CVE-2026-53539 in python-multipart 0.0.17
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-53539`
- **CWE:** CWE-400, CWE-407
- **CVE:** CVE-2026-53539
- **Dependency:** python-multipart (0.0.17 → 0.0.30)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
python-multipart 0.0.17 is affected by CVE-2026-53539; fixed in 0.0.30. Detected in backend/poetry.lock. | python-multipart 0.0.17 (PyPI) is affected by CVE-2026-53539; fixed in 0.0.30. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
python-multipart: Python-Multipart: Denial of Service via crafted form-urlencoded bodies

#### Remediation Guidance
Upgrade python-multipart to 0.0.30 or later.

---

### Issue 24: [HIGH] CVE-2026-48818 in starlette 0.46.2
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-48818`
- **CWE:** CWE-918
- **CVE:** CVE-2026-48818
- **Dependency:** starlette (0.46.2 → 1.1.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
starlette 0.46.2 is affected by CVE-2026-48818; fixed in 1.1.0. Detected in backend/poetry.lock. | starlette 0.46.2 (PyPI) is affected by CVE-2026-48818; fixed in 1.1.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
starlette: Starlette: SSRF and NTLM credential theft via UNC paths in StaticFiles on Windows

#### Remediation Guidance
Upgrade starlette to 1.1.0 or later.

---

### Issue 25: [HIGH] CVE-2025-68616 in weasyprint 63.1
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2025-68616`
- **CWE:** CWE-601, CWE-918
- **CVE:** CVE-2025-68616
- **Dependency:** weasyprint (63.1 → 68.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
weasyprint 63.1 is affected by CVE-2025-68616; fixed in 68.0. Detected in backend/poetry.lock. | weasyprint 63.1 (PyPI) is affected by CVE-2025-68616; fixed in 68.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
WeasyPrint: WeasyPrint Server-Side Request Forgery (SSRF)

#### Remediation Guidance
Upgrade weasyprint to 68.0 or later.

---

### Issue 26: [HIGH] CVE-2026-22029 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-22029`
- **CWE:** CWE-79
- **CVE:** CVE-2026-22029
- **Dependency:** react-router (7.11.0 → 7.12.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-22029; fixed in 7.12.0. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-22029; fixed in 7.12.0. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
@remix-run/router: react-router: React Router vulnerable to XSS via Open Redirects

#### Remediation Guidance
Upgrade react-router to 7.12.0 or later.

---

### Issue 27: [HIGH] CVE-2026-34077 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-34077`
- **CWE:** CWE-770
- **CVE:** CVE-2026-34077
- **Dependency:** react-router (7.11.0 → 7.14.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-34077; fixed in 7.14.0. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-34077; fixed in 7.14.0. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: React Router: Denial of Service via client-side Cross-Site Scripting in RSC redirect handling

#### Remediation Guidance
Upgrade react-router to 7.14.0 or later.

---

### Issue 28: [HIGH] CVE-2026-42342 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-42342`
- **CWE:** CWE-400
- **CVE:** CVE-2026-42342
- **Dependency:** react-router (7.11.0 → 7.15.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-42342; fixed in 7.15.0. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-42342; fixed in 7.15.0. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: @remix-run/server-runtime: React Router / Remix: Denial of Service via unbounded path expansion in __manifest endpoint

#### Remediation Guidance
Upgrade react-router to 7.15.0 or later.

---

### Issue 29: [HIGH] CVE-2025-62727 in starlette 0.46.2
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2025-62727`
- **CWE:** CWE-407
- **CVE:** CVE-2025-62727
- **Dependency:** starlette (0.46.2 → 0.49.1)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
starlette 0.46.2 is affected by CVE-2025-62727; fixed in 0.49.1. Detected in backend/poetry.lock. | starlette 0.46.2 (PyPI) is affected by CVE-2025-62727; fixed in 0.49.1. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
starlette: Starlette DoS via Range header merging

#### Remediation Guidance
Upgrade starlette to 0.49.1 or later.

---

### Issue 30: [HIGH] CVE-2026-54283 in starlette 0.46.2
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-54283`
- **CWE:** CWE-770
- **CVE:** CVE-2026-54283
- **Dependency:** starlette (0.46.2 → 1.3.1)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
starlette 0.46.2 is affected by CVE-2026-54283; fixed in 1.3.1. Detected in backend/poetry.lock. | starlette 0.46.2 (PyPI) is affected by CVE-2026-54283; fixed in 1.3.1. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
starlette: Starlette: request.form() limits silently ignored for application/x-www-form-urlencoded enable DoS

#### Remediation Guidance
Upgrade starlette to 1.3.1 or later.

---

### Issue 31: [HIGH] CVE-2026-21884 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-21884`
- **CWE:** CWE-79
- **CVE:** CVE-2026-21884
- **Dependency:** react-router (7.11.0 → 7.12.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-21884; fixed in 7.12.0. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-21884; fixed in 7.12.0. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: @remix-run/react: React Router SSR XSS in ScrollRestoration

#### Remediation Guidance
Upgrade react-router to 7.12.0 or later.

---

### Issue 32: [HIGH] CVE-2026-33245 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-33245`
- **CWE:** CWE-79
- **CVE:** CVE-2026-33245
- **Dependency:** react-router (7.11.0 → 7.13.2)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-33245; fixed in 7.13.2. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-33245; fixed in 7.13.2. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: React Router: Cross-Site Scripting vulnerability via untrusted React Server Component redirects

#### Remediation Guidance
Upgrade react-router to 7.13.2 or later.

---

### Issue 33: [HIGH] CVE-2026-42211 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-42211`
- **CWE:** CWE-502
- **CVE:** CVE-2026-42211
- **Dependency:** react-router (7.11.0 → 7.14.2)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-42211; fixed in 7.14.2. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-42211; fixed in 7.14.2. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: React Router: Remote Code Execution via prototype pollution in Framework Mode

#### Remediation Guidance
Upgrade react-router to 7.14.2 or later.

---

### Issue 34: [HIGH] CVE-2026-55685 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** high
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-55685`
- **CWE:** CWE-400, CWE-407
- **CVE:** CVE-2026-55685
- **Dependency:** react-router (7.11.0 → 7.18.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-55685; fixed in 7.18.0. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-55685; fixed in 7.18.0. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: @remix-run/server-runtime: React Router: Denial of Service via unauthenticated manifest endpoint requests

#### Remediation Guidance
Upgrade react-router to 7.18.0 or later.

---

### Issue 35: [HIGH] CVE-2026-28277 in langgraph 0.3.34
- **Category:** Dependency
- **Severity:** high
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-28277`
- **CWE:** CWE-502
- **CVE:** CVE-2026-28277
- **Dependency:** langgraph (0.3.34 → 1.0.10rc1)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
langgraph 0.3.34 is affected by CVE-2026-28277; fixed in 1.0.10. Detected in backend/poetry.lock. | langgraph 0.3.34 (PyPI) is affected by CVE-2026-28277; fixed in 1.0.10rc1. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Known vulnerability in a dependency (OSV.dev advisory).

#### Remediation Guidance
Upgrade langgraph to 1.0.10rc1 or later.

---

### Issue 36: [HIGH] CVE-2026-67213 in nanoid 3.3.16
- **Category:** Dependency
- **Severity:** high
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-67213`
- **CVE:** CVE-2026-67213
- **Dependency:** nanoid (3.3.16 → 3.3.18)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
nanoid 3.3.16 (npm) is affected by CVE-2026-67213; fixed in 3.3.18. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one.

#### Impact
nanoid: custom generators can loop indefinitely when size is zero

#### Remediation Guidance
nanoid is not declared in frontend/package.json, so adding or editing an entry there is not the fix. Find the declared dependency that pulls it in (`npm ls nanoid`) and upgrade that until it resolves nanoid 3.3.18 or later, or force the version directly with an "overrides" entry in package.json.

---

### Issue 37: [MEDIUM] CVE-2026-40087 in langchain-core 0.3.76
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-40087`
- **CWE:** CWE-1336
- **CVE:** CVE-2026-40087
- **Dependency:** langchain-core (0.3.76 → 0.3.84, 1.2.28)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
langchain-core 0.3.76 is affected by CVE-2026-40087; fixed in 0.3.84, 1.2.28. Detected in backend/poetry.lock. | langchain-core 0.3.76 (PyPI) is affected by CVE-2026-40087; fixed in 0.3.84. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
langchain: incomplete f-string validation in prompt templates

#### Remediation Guidance
Upgrade langchain-core to 0.3.84, 1.2.28 or later.

---

### Issue 38: [MEDIUM] CVE-2026-27794 in langgraph-checkpoint 2.1.2
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-27794`
- **CWE:** CWE-502
- **CVE:** CVE-2026-27794
- **Dependency:** langgraph-checkpoint (2.1.2 → 4.0.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
langgraph-checkpoint 2.1.2 is affected by CVE-2026-27794; fixed in 4.0.0. Detected in backend/poetry.lock. | langgraph-checkpoint 2.1.2 (PyPI) is affected by CVE-2026-27794; fixed in 4.0.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
langgraph-checkpoint: LangGraph Checkpoint: Remote Code Execution via insecure deserialization in caching layer

#### Remediation Guidance
Upgrade langgraph-checkpoint to 4.0.0 or later.

---

### Issue 39: [MEDIUM] CVE-2026-48775 in langgraph-checkpoint 2.1.2
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-48775`
- **CWE:** CWE-502, CWE-913
- **CVE:** CVE-2026-48775
- **Dependency:** langgraph-checkpoint (2.1.2 → 4.1.1)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
langgraph-checkpoint 2.1.2 is affected by CVE-2026-48775; fixed in 4.1.1. Detected in backend/poetry.lock. | langgraph-checkpoint 2.1.2 (PyPI) is affected by CVE-2026-48775; fixed in 4.1.1. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
langgraph: langgraph-checkpoint: LangGraph: Arbitrary code execution via insecure deserialization of modified checkpoint bytes

#### Remediation Guidance
Upgrade langgraph-checkpoint to 4.1.1 or later.

---

### Issue 40: [MEDIUM] CVE-2026-48776 in langgraph-sdk 0.1.74
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-48776`
- **CWE:** CWE-22, CWE-863
- **CVE:** CVE-2026-48776
- **Dependency:** langgraph-sdk (0.1.74 → 0.3.15)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
langgraph-sdk 0.1.74 is affected by CVE-2026-48776; fixed in 0.3.15. Detected in backend/poetry.lock. | langgraph-sdk 0.1.74 (PyPI) is affected by CVE-2026-48776; fixed in 0.3.15. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
langgraph: langgraph-sdk: LangGraph Python SDK: Unsafe URL path construction leads to unauthorized resource access

#### Remediation Guidance
Upgrade langgraph-sdk to 0.3.15 or later.

---

### Issue 41: [MEDIUM] CVE-2026-42309 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-42309`
- **CWE:** CWE-122
- **CVE:** CVE-2026-42309
- **Dependency:** pillow (11.3.0 → 12.2.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-42309; fixed in 12.2.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-42309; fixed in 12.2.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Pillow: Pillow: Denial of Service via specially crafted coordinate input

#### Remediation Guidance
Upgrade pillow to 12.2.0 or later.

---

### Issue 42: [MEDIUM] CVE-2026-55798 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-55798`
- **CWE:** CWE-78
- **CVE:** CVE-2026-55798
- **Dependency:** pillow (11.3.0 → 12.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-55798; fixed in 12.3.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-55798; fixed in 12.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
python-pillow: Pillow: Arbitrary command injection via shell metacharacters in file paths

#### Remediation Guidance
Upgrade pillow to 12.3.0 or later.

---

### Issue 43: [MEDIUM] CVE-2026-40347 in python-multipart 0.0.17
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-40347`
- **CWE:** CWE-400, CWE-834
- **CVE:** CVE-2026-40347
- **Dependency:** python-multipart (0.0.17 → 0.0.26)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
python-multipart 0.0.17 is affected by CVE-2026-40347; fixed in 0.0.26. Detected in backend/poetry.lock. | python-multipart 0.0.17 (PyPI) is affected by CVE-2026-40347; fixed in 0.0.26. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
python-multipart: Python-Multipart: Denial of Service via crafted multipart/form-data requests

#### Remediation Guidance
Upgrade python-multipart to 0.0.26 or later.

---

### Issue 44: [MEDIUM] CVE-2026-42308 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-42308`
- **CWE:** CWE-190
- **CVE:** CVE-2026-42308
- **Dependency:** pillow (11.3.0 → 12.2.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-42308; fixed in 12.2.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-42308; fixed in 12.2.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Pillow: python: Pillow: Denial of Service via integer overflow in font processing

#### Remediation Guidance
Upgrade pillow to 12.2.0 or later.

---

### Issue 45: [MEDIUM] CVE-2026-42310 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-42310`
- **CWE:** CWE-835
- **CVE:** CVE-2026-42310
- **Dependency:** pillow (11.3.0 → 12.2.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-42310; fixed in 12.2.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-42310; fixed in 12.2.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Pillow: Pillow: Denial of Service via malicious PDF processing

#### Remediation Guidance
Upgrade pillow to 12.2.0 or later.

---

### Issue 46: [MEDIUM] CVE-2026-59198 in pillow 11.3.0
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-59198`
- **CWE:** CWE-125
- **CVE:** CVE-2026-59198
- **Dependency:** pillow (11.3.0 → 12.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pillow 11.3.0 is affected by CVE-2026-59198; fixed in 12.3.0. Detected in backend/poetry.lock. | pillow 11.3.0 (PyPI) is affected by CVE-2026-59198; fixed in 12.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Pillow: Pillow: Information disclosure via TGA RLE encoder out-of-bounds read

#### Remediation Guidance
Upgrade pillow to 12.3.0 or later.

---

### Issue 47: [MEDIUM] CVE-2025-54121 in starlette 0.46.2
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2025-54121`
- **CWE:** CWE-770
- **CVE:** CVE-2025-54121
- **Dependency:** starlette (0.46.2 → 0.47.2)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
starlette 0.46.2 is affected by CVE-2025-54121; fixed in 0.47.2. Detected in backend/poetry.lock. | starlette 0.46.2 (PyPI) is affected by CVE-2025-54121; fixed in 0.47.2. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
starlette: Starlette denial-of-service

#### Remediation Guidance
Upgrade starlette to 0.47.2 or later.

---

### Issue 48: [MEDIUM] CVE-2026-48817 in starlette 0.46.2
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-48817`
- **CWE:** CWE-470
- **CVE:** CVE-2026-48817
- **Dependency:** starlette (0.46.2 → 1.1.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
starlette 0.46.2 is affected by CVE-2026-48817; fixed in 1.1.0. Detected in backend/poetry.lock. | starlette 0.46.2 (PyPI) is affected by CVE-2026-48817; fixed in 1.1.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
starlette: Starlette: Information disclosure and unintended method execution via non-standard HTTP methods

#### Remediation Guidance
Upgrade starlette to 1.1.0 or later.

---

### Issue 49: [MEDIUM] CVE-2026-48710 in starlette 0.46.2
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-48710`
- **CWE:** CWE-444, CWE-1289
- **CVE:** CVE-2026-48710
- **Dependency:** starlette (0.46.2 → 1.0.1)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
starlette 0.46.2 is affected by CVE-2026-48710; fixed in 1.0.1. Detected in backend/poetry.lock. | starlette 0.46.2 (PyPI) is affected by CVE-2026-48710; fixed in 1.0.1. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
starlette: Starlette: Security restriction bypass via malformed HTTP Host header

#### Remediation Guidance
Upgrade starlette to 1.0.1 or later.

---

### Issue 50: [MEDIUM] CVE-2026-49452 in weasyprint 63.1
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-49452`
- **CWE:** CWE-74
- **CVE:** CVE-2026-49452
- **Dependency:** weasyprint (63.1)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
weasyprint 63.1 is affected by CVE-2026-49452. Detected in backend/poetry.lock. | weasyprint 63.1 (PyPI) is affected by CVE-2026-49452. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
weasyprint: WeasyPrint: CSS Injection via Presentational Hints

#### Remediation Guidance
No fixed version available yet; consider mitigation or an alternative.

---

### Issue 51: [MEDIUM] CVE-2026-33244 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-33244`
- **CWE:** CWE-79
- **CVE:** CVE-2026-33244
- **Dependency:** react-router (7.11.0 → 7.13.2)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-33244; fixed in 7.13.2. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-33244; fixed in 7.13.2. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: React Router: Cross-Site Scripting (XSS) via improper HTTP Location header neutralization

#### Remediation Guidance
Upgrade react-router to 7.13.2 or later.

---

### Issue 52: [MEDIUM] CVE-2026-53666 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-53666`
- **CWE:** CWE-470
- **CVE:** CVE-2026-53666
- **Dependency:** react-router (7.11.0 → 7.18.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-53666; fixed in 7.18.0. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-53666; fixed in 7.18.0. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: React Router: Information disclosure via client-side constructor execution

#### Remediation Guidance
Upgrade react-router to 7.18.0 or later.

---

### Issue 53: [MEDIUM] CVE-2026-22030 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-22030`
- **CWE:** CWE-346, CWE-352
- **CVE:** CVE-2026-22030
- **Dependency:** react-router (7.11.0 → 7.12.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-22030; fixed in 7.12.0. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-22030; fixed in 7.12.0. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: React Router CSRF in Action/Server Action Request Processing

#### Remediation Guidance
Upgrade react-router to 7.12.0 or later.

---

### Issue 54: [MEDIUM] CVE-2026-40181 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-40181`
- **CWE:** CWE-601
- **CVE:** CVE-2026-40181
- **Dependency:** react-router (7.11.0 → 7.14.1, 6.30.4)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-40181; fixed in 7.14.1, 6.30.4. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-40181; fixed in 7.14.1. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: React Router: Open redirect vulnerability via specially crafted URLs

#### Remediation Guidance
Upgrade react-router to 7.14.1, 6.30.4 or later.

---

### Issue 55: [MEDIUM] CVE-2026-53667 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-53667`
- **CWE:** CWE-79
- **CVE:** CVE-2026-53667
- **Dependency:** react-router (7.11.0 → 7.18.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-53667; fixed in 7.18.0. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-53667; fixed in 7.18.0. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: React Router: Untrusted redirects due to missing protocol validation

#### Remediation Guidance
Upgrade react-router to 7.18.0 or later.

---

### Issue 56: [MEDIUM] CVE-2026-53669 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-53669`
- **CWE:** CWE-601
- **CVE:** CVE-2026-53669
- **Dependency:** react-router (7.11.0 → 7.18.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-53669; fixed in 7.18.0. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-53669; fixed in 7.18.0. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: React Router: Open Redirect vulnerability via backslashes in navigation components

#### Remediation Guidance
Upgrade react-router to 7.18.0 or later.

---

### Issue 57: [MEDIUM] CVE-2026-53668 in react-router 7.11.0
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-53668`
- **CWE:** CWE-79, CWE-601
- **CVE:** CVE-2026-53668
- **Dependency:** react-router (7.11.0 → 7.13.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
react-router 7.11.0 is affected by CVE-2026-53668; fixed in 7.13.0. Detected in frontend/package-lock.json. | react-router 7.11.0 (npm) is affected by CVE-2026-53668; fixed in 7.13.0. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one. (corroborated by osv, repo)

#### Impact
react-router: react-router-dom: React Router: Cross-Site Scripting (XSS) via open redirects

#### Remediation Guidance
Upgrade react-router to 7.13.0 or later.

---

### Issue 58: [MEDIUM] CVE-2026-54282 in starlette 0.46.2
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-54282`
- **CWE:** CWE-706
- **CVE:** CVE-2026-54282
- **Dependency:** starlette (0.46.2 → 1.3.0)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
starlette 0.46.2 is affected by CVE-2026-54282; fixed in 1.3.0. Detected in backend/poetry.lock. | starlette 0.46.2 (PyPI) is affected by CVE-2026-54282; fixed in 1.3.0. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
Known vulnerability in a dependency (OSV.dev advisory).

#### Remediation Guidance
Upgrade starlette to 1.3.0 or later.

---

### Issue 59: [MEDIUM] Verified live secret: Lob
- **Category:** Secrets
- **Severity:** medium
- **Affected:** `backend/tests/test_chunker.py:18 @ commit 8d2df969cc` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `trufflehog:Lob`
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
TruffleHog Lob detector matched  in backend/tests/test_chunker.py (commit 8d2df969cc). The credential was confirmed still ACTIVE. This location is the file as of commit 8d2df969cc in the repository's history — the current HEAD may no longer contain it, but a committed credential stays extractable from history until it is rotated.

#### Impact
A live, committed credential can be used by anyone with repo (or history) access right now. Located in test/fixture code, so it is not reachable in production — capped at medium. Still worth fixing: test credentials leak, and a test that disables a security control often mirrors a real one.

#### Remediation Guidance
Rotate the credential immediately — that is what actually revokes it. Then purge it from the code and rewrite the git history, since deleting it in a later commit leaves it readable in every earlier one.

---

### Issue 60: [MEDIUM] Code issue: hardcoded-credential-python
- **Category:** Code
- **Severity:** medium
- **Affected:** `backend/app/core/config.py:36` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `rules.common.hardcoded-credential-python`
- **CWE:** CWE-798
- **OWASP:** OWASP A07:2021
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Hardcoded credential in Python source: a literal password/secret/token/key assigned in code. Read it from os.environ, a settings object backed by the environment, or a secrets manager.

Code:
postgres_password: str = "legallink" | Possible hardcoded password assigned to: "postgres_password" (ruff S105) at backend/app/core/config.py:36. (corroborated by code, ruff-security)

#### Impact
Static analysis rule "rules.common.hardcoded-credential-python" flagged a code-level security issue. CWE: CWE-798: Use of Hard-coded Credentials. OWASP: A07:2021 - Identification and Authentication Failures.

#### Remediation Guidance
Apply the rule's guidance. References: https://cwe.mitre.org/data/definitions/798.html

#### Code Snippet
```python
postgres_password: str = "legallink"
```

---

### Issue 61: [MEDIUM] Verified live secret: Lob
- **Category:** Secrets
- **Severity:** medium
- **Affected:** `backend/tests/test_health.py:10 @ commit 62ae2f0be2` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `trufflehog:Lob`
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
TruffleHog Lob detector matched  in backend/tests/test_health.py (commit 62ae2f0be2). The credential was confirmed still ACTIVE. This location is the file as of commit 62ae2f0be2 in the repository's history — the current HEAD may no longer contain it, but a committed credential stays extractable from history until it is rotated.

#### Impact
A live, committed credential can be used by anyone with repo (or history) access right now. Located in test/fixture code, so it is not reachable in production — capped at medium. Still worth fixing: test credentials leak, and a test that disables a security control often mirrors a real one.

#### Remediation Guidance
Rotate the credential immediately — that is what actually revokes it. Then purge it from the code and rewrite the git history, since deleting it in a later commit leaves it readable in every earlier one.

---

### Issue 62: [MEDIUM] Potential secret: Dockerhub
- **Category:** Secrets
- **Severity:** medium
- **Affected:** `backend/app/services/generator.py:37 @ commit 2121fafd28` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `trufflehog:Dockerhub`
- **Confidence:** low
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
TruffleHog Dockerhub detector matched  in backend/app/services/generator.py (commit 2121fafd28). Not verified as live. This location is the file as of commit 2121fafd28 in the repository's history — the current HEAD may no longer contain it, but a committed credential stays extractable from history until it is rotated.

#### Impact
A credential-shaped string is committed; if real it can be used by anyone with repo access.

#### Remediation Guidance
Rotate the credential immediately — that is what actually revokes it. Then purge it from the code and rewrite the git history, since deleting it in a later commit leaves it readable in every earlier one.

---

### Issue 63: [MEDIUM] CVE-2025-71176 in pytest 8.4.2
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2025-71176`
- **CVE:** CVE-2025-71176
- **Dependency:** pytest (8.4.2 → 9.0.3)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
pytest 8.4.2 (PyPI) is affected by CVE-2025-71176; fixed in 9.0.3. Detected in backend/poetry.lock via OSV.dev.

#### Impact
pytest has vulnerable tmpdir handling

#### Remediation Guidance
Upgrade pytest to 9.0.3 or later.

---

### Issue 64: [MEDIUM] Python security issue: S105 hardcoded password string
- **Category:** Code
- **Severity:** medium
- **Affected:** `backend/app/core/config.py:173` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:S105`
- **CWE:** CWE-798
- **Estimated Effort:** 30min
- **Confidence:** medium
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
Possible hardcoded password assigned to: "jwt_secret" (ruff S105) at backend/app/core/config.py:173.

#### Impact
flake8-bandit flags source patterns behind real vulnerability classes — injection, weak crypto, hardcoded credentials, unsafe deserialization. Ruff has no dataflow analysis, so treat this as a lead to confirm rather than a proven exploit. CWE: CWE-798.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/hardcoded-password-string

---

### Issue 65: [MEDIUM] CVE-2026-69153 in postcss 8.5.19
- **Category:** Dependency
- **Severity:** medium
- **Affected:** `frontend/package.json` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-69153`
- **CVE:** CVE-2026-69153
- **Dependency:** postcss (8.5.19 → 8.5.23)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
postcss 8.5.19 (npm) is affected by CVE-2026-69153; fixed in 8.5.23. Detected in frontend/package-lock.json via OSV.dev. It is not declared in frontend/package.json — a dependency that is declared there pulls it in transitively. This scan does not resolve which one.

#### Impact
PostCSS: incomplete fix of GHSA-6g55-p6wh-862q — attacker-controlled sourceMappingURL reads arbitrary .map files when `from` is unset

#### Remediation Guidance
postcss is not declared in frontend/package.json, so adding or editing an entry there is not the fix. Find the declared dependency that pulls it in (`npm ls postcss`) and upgrade that until it resolves postcss 8.5.23 or later, or force the version directly with an "overrides" entry in package.json.

---

### Issue 66: [MEDIUM] High cyclomatic complexity (31)
- **Category:** Maintainability
- **Severity:** medium
- **Affected:** `backend/app/tasks/chat.py:55 _generate()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _generate() has cyclomatic complexity 31 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 67: [MEDIUM] High cyclomatic complexity (28)
- **Category:** Maintainability
- **Severity:** medium
- **Affected:** `backend/app/services/task_center.py:291 _normalize()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _normalize() has cyclomatic complexity 28 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 68: [LOW] CVE-2026-26013 in langchain-core 0.3.76
- **Category:** Dependency
- **Severity:** low
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-26013`
- **CWE:** CWE-918
- **CVE:** CVE-2026-26013
- **Dependency:** langchain-core (0.3.76 → 1.2.11)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
langchain-core 0.3.76 is affected by CVE-2026-26013; fixed in 1.2.11. Detected in backend/poetry.lock. | langchain-core 0.3.76 (PyPI) is affected by CVE-2026-26013; fixed in 1.2.11. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
langchain: SSRF via image_url token counting in ChatOpenAI.get_num_tokens_from_messages

#### Remediation Guidance
Upgrade langchain-core to 1.2.11 or later.

---

### Issue 69: [LOW] CVE-2026-53538 in python-multipart 0.0.17
- **Category:** Dependency
- **Severity:** low
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-53538`
- **CWE:** CWE-436, CWE-444
- **CVE:** CVE-2026-53538
- **Dependency:** python-multipart (0.0.17 → 0.0.30)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
python-multipart 0.0.17 is affected by CVE-2026-53538; fixed in 0.0.30. Detected in backend/poetry.lock. | python-multipart 0.0.17 (PyPI) is affected by CVE-2026-53538; fixed in 0.0.30. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
python-multipart: Python-Multipart: Information disclosure due to parser differential in form data handling

#### Remediation Guidance
Upgrade python-multipart to 0.0.30 or later.

---

### Issue 70: [LOW] CVE-2026-53537 in python-multipart 0.0.17
- **Category:** Dependency
- **Severity:** low
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-53537`
- **CWE:** CWE-20, CWE-436
- **CVE:** CVE-2026-53537
- **Dependency:** python-multipart (0.0.17 → 0.0.30)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
python-multipart 0.0.17 is affected by CVE-2026-53537; fixed in 0.0.30. Detected in backend/poetry.lock. | python-multipart 0.0.17 (PyPI) is affected by CVE-2026-53537; fixed in 0.0.30. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
multipart: Python-Multipart: Information disclosure via header parsing discrepancy

#### Remediation Guidance
Upgrade python-multipart to 0.0.30 or later.

---

### Issue 71: [LOW] CVE-2026-53540 in python-multipart 0.0.17
- **Category:** Dependency
- **Severity:** low
- **Affected:** `backend/pyproject.toml` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `CVE-2026-53540`
- **CWE:** CWE-1284
- **CVE:** CVE-2026-53540
- **Dependency:** python-multipart (0.0.17 → 0.0.31)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
python-multipart 0.0.17 is affected by CVE-2026-53540; fixed in 0.0.31. Detected in backend/poetry.lock. | python-multipart 0.0.17 (PyPI) is affected by CVE-2026-53540; fixed in 0.0.31. Detected in backend/poetry.lock via OSV.dev. (corroborated by osv, repo)

#### Impact
python-multipart: Python-Multipart: Negative Content-Length in parse_form buffers the entire body in memory

#### Remediation Guidance
Upgrade python-multipart to 0.0.31 or later.

---

### Issue 72: [LOW] subprocess without shell equals true
- **Category:** Code
- **Severity:** low
- **Affected:** `backend/app/ocr/subprocess_runner.py:98` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `bandit:B603`
- **CWE:** CWE-78
- **Confidence:** medium
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
subprocess call - check for execution of untrusted input.

97         try:
98             completed = subprocess.run(
99                 cmd,
100                 capture_output=True,
101                 text=True,
102                 timeout=timeout_seconds,
103                 check=False,
104                 env={
105                     **os.environ,
106                     "OMP_NUM_THREADS": "1",
107                     "MKL_NUM_THREADS": "1",
108

#### Impact
See the rule's description — bandit reports the pattern, not a traced exploit path.

#### Remediation Guidance
Guidance: https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html

#### Code Snippet
```python
97         try:
98             completed = subprocess.run(
99                 cmd,
100                 capture_output=True,
101                 text=True,
102                 timeout=timeout_seconds,
103                 check=False,
104                 env={
105                     **os.environ,
106                     "OMP_NUM_THREADS": "1",
107                     "MKL_NUM_THREADS": "1",
108
```

---

### Issue 73: [LOW] Too many parameters (8)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `frontend/src/components/ui/Input.tsx:11 Input()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function Input() takes 8 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 74: [LOW] High cyclomatic complexity (approx. 25)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `frontend/src/pages/Tasks.tsx:49 TasksPage()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** low
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
Function TasksPage() is estimated at cyclomatic complexity 25 (recommended ≤ 15). The analyzer's JavaScript/TypeScript reader mis-parses regular-expression literals, so this figure is approximate — measured against the TypeScript AST it flags the right function ~71% of the time. Confirm before refactoring.

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 75: [LOW] High cyclomatic complexity (approx. 21)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `frontend/src/pages/Consultation.tsx:861 maybeResumePendingJob()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** low
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
Function maybeResumePendingJob() is estimated at cyclomatic complexity 21 (recommended ≤ 15). The analyzer's JavaScript/TypeScript reader mis-parses regular-expression literals, so this figure is approximate — measured against the TypeScript AST it flags the right function ~71% of the time. Confirm before refactoring.

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 76: [LOW] High cyclomatic complexity (approx. 16)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `frontend/src/pages/Dashboard.tsx:49 DashboardPage()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** low
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
Function DashboardPage() is estimated at cyclomatic complexity 16 (recommended ≤ 15). The analyzer's JavaScript/TypeScript reader mis-parses regular-expression literals, so this figure is approximate — measured against the TypeScript AST it flags the right function ~71% of the time. Confirm before refactoring.

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 77: [LOW] High cyclomatic complexity (approx. 25)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `frontend/src/pages/Settings.tsx:22 SettingsPage()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** low
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
Function SettingsPage() is estimated at cyclomatic complexity 25 (recommended ≤ 15). The analyzer's JavaScript/TypeScript reader mis-parses regular-expression literals, so this figure is approximate — measured against the TypeScript AST it flags the right function ~71% of the time. Confirm before refactoring.

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 78: [LOW] High cyclomatic complexity (20)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/agents/nodes/synthesis_node.py:62 execute()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function execute() has cyclomatic complexity 20 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 79: [LOW] Over-long function (101 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/agents/risk.py:154 classify()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function classify() is 101 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 80: [LOW] High cyclomatic complexity (approx. 22)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `frontend/src/components/IngestionProgress.tsx:75 IngestionProgress()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** low
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
Function IngestionProgress() is estimated at cyclomatic complexity 22 (recommended ≤ 15). The analyzer's JavaScript/TypeScript reader mis-parses regular-expression literals, so this figure is approximate — measured against the TypeScript AST it flags the right function ~71% of the time. Confirm before refactoring.

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 81: [LOW] High cyclomatic complexity (approx. 20)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `frontend/src/pages/Consultation.tsx:573 MessageRow()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** low
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
Function MessageRow() is estimated at cyclomatic complexity 20 (recommended ≤ 15). The analyzer's JavaScript/TypeScript reader mis-parses regular-expression literals, so this figure is approximate — measured against the TypeScript AST it flags the right function ~71% of the time. Confirm before refactoring.

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 82: [LOW] High cyclomatic complexity (approx. 42)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `frontend/src/pages/Consultation.tsx:1179 send()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** low
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
Function send() is estimated at cyclomatic complexity 42 (recommended ≤ 15). The analyzer's JavaScript/TypeScript reader mis-parses regular-expression literals, so this figure is approximate — measured against the TypeScript AST it flags the right function ~71% of the time. Confirm before refactoring.

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 83: [LOW] High cyclomatic complexity (approx. 16)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `frontend/src/pages/Login.tsx:33 LoginPage()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** low
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
Function LoginPage() is estimated at cyclomatic complexity 16 (recommended ≤ 15). The analyzer's JavaScript/TypeScript reader mis-parses regular-expression literals, so this figure is approximate — measured against the TypeScript AST it flags the right function ~71% of the time. Confirm before refactoring.

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 84: [LOW] High cyclomatic complexity (approx. 31)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `frontend/src/services/agents.ts:110 handleEvent()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** low
- **Status:** unconfirmed
- **Lifecycle State:** open

#### Evidence
Function handleEvent() is estimated at cyclomatic complexity 31 (recommended ≤ 15). The analyzer's JavaScript/TypeScript reader mis-parses regular-expression literals, so this figure is approximate — measured against the TypeScript AST it flags the right function ~71% of the time. Confirm before refactoring.

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 85: [LOW] Over-long function (122 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/agents/nodes/synthesis_node.py:62 execute()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function execute() is 122 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 86: [LOW] Over-long function (114 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/agents/legal.py:114 analyze()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function analyze() is 114 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 87: [LOW] Over-long function (169 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/tasks/chat.py:55 _generate()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _generate() is 169 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 88: [LOW] Too many parameters (11)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/llm/base.py:102 __init__()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function __init__() takes 11 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 89: [LOW] High cyclomatic complexity (21)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/chunker.py:145 _split_text()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _split_text() has cyclomatic complexity 21 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 90: [LOW] High cyclomatic complexity (16)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/task_center.py:137 _reap_if_stale()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _reap_if_stale() has cyclomatic complexity 16 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 91: [LOW] High cyclomatic complexity (20)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/contract_analysis.py:42 get_or_analyze()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function get_or_analyze() has cyclomatic complexity 20 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 92: [LOW] Too many parameters (10)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/contract_analysis.py:42 get_or_analyze()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function get_or_analyze() takes 10 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 93: [LOW] Over-long function (125 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generator.py:103 _resolve_answer_chunks()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _resolve_answer_chunks() is 125 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 94: [LOW] High cyclomatic complexity (20)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generator.py:406 stream_answer()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function stream_answer() has cyclomatic complexity 20 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 95: [LOW] Too many parameters (9)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/agents/legal.py:114 analyze()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function analyze() takes 9 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 96: [LOW] Over-long function (139 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/graphs/ingestion_graph.py:125 build_ingestion_graph()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function build_ingestion_graph() is 139 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 97: [LOW] Too many parameters (8)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/report_generation.py:158 generate()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function generate() takes 8 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 98: [LOW] High cyclomatic complexity (17)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/task_center.py:39 list_for_user()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function list_for_user() has cyclomatic complexity 17 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 99: [LOW] Over-long function (101 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/task_center.py:291 _normalize()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _normalize() is 101 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 100: [LOW] Over-long function (143 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/contract_analysis.py:42 get_or_analyze()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function get_or_analyze() is 143 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 101: [LOW] Too many parameters (9)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/contract_analysis.py:186 _compute()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _compute() takes 9 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 102: [LOW] Too many parameters (11)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generator.py:229 answer_question()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function answer_question() takes 11 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 103: [LOW] Over-long function (150 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generator.py:406 stream_answer()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function stream_answer() is 150 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 104: [LOW] Too many parameters (8)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generator.py:557 generate_from_chunks()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function generate_from_chunks() takes 8 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 105: [LOW] Over-long function (145 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generator.py:634 analyze_contract()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function analyze_contract() is 145 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 106: [LOW] Over-long function (136 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generator.py:935 _generate_full_document()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _generate_full_document() is 136 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 107: [LOW] High cyclomatic complexity (16)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generator.py:1336 _normalize_structured_analysis()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _normalize_structured_analysis() has cyclomatic complexity 16 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 108: [LOW] Too many parameters (8)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/agent_stream.py:88 stream()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function stream() takes 8 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 109: [LOW] High cyclomatic complexity (18)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/agent_stream.py:204 _stream_multi()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _stream_multi() has cyclomatic complexity 18 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 110: [LOW] Too many parameters (10)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/agent_stream.py:204 _stream_multi()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _stream_multi() takes 10 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 111: [LOW] High cyclomatic complexity (19)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/contract_synthesis.py:75 get_or_synthesize()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function get_or_synthesize() has cyclomatic complexity 19 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 112: [LOW] Too many parameters (8)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/contract_synthesis.py:75 get_or_synthesize()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function get_or_synthesize() takes 8 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 113: [LOW] High cyclomatic complexity (19)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generator.py:634 analyze_contract()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function analyze_contract() has cyclomatic complexity 19 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 114: [LOW] Over-long function (154 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generator.py:780 generate_document()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function generate_document() is 154 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 115: [LOW] Too many parameters (10)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generator.py:935 _generate_full_document()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _generate_full_document() takes 10 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 116: [LOW] High cyclomatic complexity (18)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/contract_comparison.py:119 get_or_compare()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function get_or_compare() has cyclomatic complexity 18 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 117: [LOW] Too many parameters (11)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/agent_stream.py:144 _stream_single()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _stream_single() takes 11 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 118: [LOW] Over-long function (139 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/agent_stream.py:204 _stream_multi()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _stream_multi() is 139 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 119: [LOW] Too many parameters (9)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/conversation.py:183 send_user_message()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function send_user_message() takes 9 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 120: [LOW] Over-long function (114 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/contract_synthesis.py:75 get_or_synthesize()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function get_or_synthesize() is 114 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 121: [LOW] Too many parameters (8)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/chat_job.py:50 create()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function create() takes 8 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 122: [LOW] Over-long function (116 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/indexing.py:47 index_document()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function index_document() is 116 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 123: [LOW] Over-long function (106 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/document_processing.py:56 process_document()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function process_document() is 106 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 124: [LOW] High cyclomatic complexity (18)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/ocr/paddle_ocr.py:188 _lines_from_result()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _lines_from_result() has cyclomatic complexity 18 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 125: [LOW] Over-long function (111 lines)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/ocr/subprocess_runner.py:59 run_paddle_ocr_subprocess()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:function-length`
- **Estimated Effort:** 20min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function run_paddle_ocr_subprocess() is 111 lines long (recommended ≤ 100).

#### Impact
Long functions are hard to read, review, and maintain.

#### Remediation Guidance
Split into smaller, single-purpose functions.

---

### Issue 126: [LOW] Too many parameters (8)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generated_document.py:41 save_pdf()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:parameter-count`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function save_pdf() takes 8 parameters (recommended ≤ 7).

#### Impact
Long parameter lists are error-prone and hard to call correctly.

#### Remediation Guidance
Group related parameters into an object/struct, or split the function's responsibilities.

---

### Issue 127: [LOW] High cyclomatic complexity (18)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/langfuse_service.py:285 _summarize_state()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function _summarize_state() has cyclomatic complexity 18 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 128: [LOW] High cyclomatic complexity (18)
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/ocr/subprocess_runner.py:59 run_paddle_ocr_subprocess()` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `maintainability:cyclomatic-complexity`
- **Estimated Effort:** 30min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Function run_paddle_ocr_subprocess() has cyclomatic complexity 18 (recommended ≤ 15).

#### Impact
Highly complex functions are hard to test and maintain and are more defect-prone.

#### Remediation Guidance
Refactor into smaller functions; flatten nested branches/loops, extract helpers, use early returns.

---

### Issue 129: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/agents/legal.py:114` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (8 > 5) (ruff PLR0913) at backend/app/agents/legal.py:114.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 130: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/graphs/ingestion_graph.py:125` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (6 > 5) (ruff PLR0913) at backend/app/graphs/ingestion_graph.py:125.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 131: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/ocr/subprocess_runner.py:59` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (6 > 5) (ruff PLR0913) at backend/app/ocr/subprocess_runner.py:59.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 132: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/analysis_job.py:49` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (6 > 5) (ruff PLR0913) at backend/app/services/analysis_job.py:49.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 133: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/contract_analysis.py:42` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (9 > 5) (ruff PLR0913) at backend/app/services/contract_analysis.py:42.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 134: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/contract_synthesis.py:75` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (7 > 5) (ruff PLR0913) at backend/app/services/contract_synthesis.py:75.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 135: [LOW] Python bug risk: ASYNC240 blocking path method in async function
- **Category:** Reliability
- **Severity:** low
- **Affected:** `backend/app/services/document.py:292` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:ASYNC240`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Async functions should not use pathlib.Path methods, use trio.Path or anyio.path (ruff ASYNC240) at backend/app/services/document.py:292.

#### Impact
This pattern is a likely defect, not a style preference: it changes runtime behaviour or hides an error the interpreter will only raise on the unhappy path.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/blocking-path-method-in-async-function

---

### Issue 136: [LOW] Python bug risk: B904 raise without from inside except
- **Category:** Reliability
- **Severity:** low
- **Affected:** `backend/app/api/deps.py:44` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:B904`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling (ruff B904) at backend/app/api/deps.py:44.

#### Impact
This pattern is a likely defect, not a style preference: it changes runtime behaviour or hides an error the interpreter will only raise on the unhappy path.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/raise-without-from-inside-except

---

### Issue 137: [LOW] Python code smell: PLR0915 too many statements
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/graphs/ingestion_graph.py:125` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0915`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many statements (65 > 50) (ruff PLR0915) at backend/app/graphs/ingestion_graph.py:125.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-statements

---

### Issue 138: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/agent_stream.py:88` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (7 > 5) (ruff PLR0913) at backend/app/services/agent_stream.py:88.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 139: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/chat_job.py:50` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (7 > 5) (ruff PLR0913) at backend/app/services/chat_job.py:50.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 140: [LOW] Python bug risk: F841 unused variable
- **Category:** Reliability
- **Severity:** low
- **Affected:** `backend/app/services/contract_comparison.py:157` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:F841`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Local variable `created` is assigned to but never used (ruff F841) at backend/app/services/contract_comparison.py:157.

#### Impact
This pattern is a likely defect, not a style preference: it changes runtime behaviour or hides an error the interpreter will only raise on the unhappy path.

#### Remediation Guidance
Ruff offers an automatic unsafe fix: Remove assignment to unused variable `created`. Run `ruff check --fix` and review the diff.

---

### Issue 141: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/conversation.py:183` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (8 > 5) (ruff PLR0913) at backend/app/services/conversation.py:183.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 142: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/document_processing.py:163` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (6 > 5) (ruff PLR0913) at backend/app/services/document_processing.py:163.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 143: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generated_document.py:41` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (7 > 5) (ruff PLR0913) at backend/app/services/generated_document.py:41.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 144: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/generator.py:53` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (6 > 5) (ruff PLR0913) at backend/app/services/generator.py:53.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 145: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/report_generation.py:158` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (7 > 5) (ruff PLR0913) at backend/app/services/report_generation.py:158.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 146: [LOW] Python code smell: PLR0911 too many return statements
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/task_center.py:196` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0911`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many return statements (8 > 6) (ruff PLR0911) at backend/app/services/task_center.py:196.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-return-statements

---

### Issue 147: [LOW] Python code smell: PLR0915 too many statements
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/tasks/chat.py:55` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0915`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many statements (58 > 50) (ruff PLR0915) at backend/app/tasks/chat.py:55.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-statements

---

### Issue 148: [LOW] Python bug risk: ASYNC240 blocking path method in async function
- **Category:** Reliability
- **Severity:** low
- **Affected:** `backend/app/services/generated_document.py:121` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:ASYNC240`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Async functions should not use pathlib.Path methods, use trio.Path or anyio.path (ruff ASYNC240) at backend/app/services/generated_document.py:121.

#### Impact
This pattern is a likely defect, not a style preference: it changes runtime behaviour or hides an error the interpreter will only raise on the unhappy path.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/blocking-path-method-in-async-function

---

### Issue 149: [LOW] Python code smell: PLR0913 too many arguments
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/llm/base.py:102` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0913`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many arguments in function definition (10 > 5) (ruff PLR0913) at backend/app/services/llm/base.py:102.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-arguments

---

### Issue 150: [LOW] Python code smell: PLR0915 too many statements
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/services/task_center.py:39` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0915`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many statements (51 > 50) (ruff PLR0915) at backend/app/services/task_center.py:39.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-statements

---

### Issue 151: [LOW] Python code smell: PLR0912 too many branches
- **Category:** Maintainability
- **Severity:** low
- **Affected:** `backend/app/tasks/chat.py:55` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PLR0912`
- **Estimated Effort:** 15min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Too many branches (16 > 12) (ruff PLR0912) at backend/app/tasks/chat.py:55.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/too-many-branches

---

### Issue 152: [INFO] Duplicated code block
- **Category:** Duplication
- **Severity:** info
- **Affected:** `frontend/src/services/chat.ts:345` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `duplication:copy-paste`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
17 duplicated lines: frontend/src/services/chat.ts:345-361 is a copy of frontend/src/services/chat.ts:232-246.

#### Impact
Duplicated code must be fixed in every copy; divergence causes bugs and inflates maintenance.

#### Remediation Guidance
Extract the shared logic into a single reusable function/module and call it from both places.

---

### Issue 153: [INFO] Duplicated code block
- **Category:** Duplication
- **Severity:** info
- **Affected:** `backend/app/services/analysis_job.py:136` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `duplication:copy-paste`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
17 duplicated lines: backend/app/services/analysis_job.py:136-152 is a copy of backend/app/services/analysis_job.py:105-119.

#### Impact
Duplicated code must be fixed in every copy; divergence causes bugs and inflates maintenance.

#### Remediation Guidance
Extract the shared logic into a single reusable function/module and call it from both places.

---

### Issue 154: [INFO] Duplicated code block
- **Category:** Duplication
- **Severity:** info
- **Affected:** `backend/app/schemas/agents.py:20` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `duplication:copy-paste`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
8 duplicated lines: backend/app/schemas/agents.py:20-27 is a copy of backend/app/schemas/conversation.py:74-81.

#### Impact
Duplicated code must be fixed in every copy; divergence causes bugs and inflates maintenance.

#### Remediation Guidance
Extract the shared logic into a single reusable function/module and call it from both places.

---

### Issue 155: [INFO] Duplicated code block
- **Category:** Duplication
- **Severity:** info
- **Affected:** `backend/app/models/comparison.py:46` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `duplication:copy-paste`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
13 duplicated lines: backend/app/models/comparison.py:46-58 is a copy of backend/app/models/synthesis.py:48-60.

#### Impact
Duplicated code must be fixed in every copy; divergence causes bugs and inflates maintenance.

#### Remediation Guidance
Extract the shared logic into a single reusable function/module and call it from both places.

---

### Issue 156: [INFO] Duplicated code block
- **Category:** Duplication
- **Severity:** info
- **Affected:** `backend/alembic/versions/011_document_syntheses.py:65` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `duplication:copy-paste`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
17 duplicated lines: backend/alembic/versions/011_document_syntheses.py:65-81 is a copy of backend/alembic/versions/012_contract_comparisons.py:59-75.

#### Impact
Duplicated code must be fixed in every copy; divergence causes bugs and inflates maintenance.

#### Remediation Guidance
Extract the shared logic into a single reusable function/module and call it from both places.

---

### Issue 157: [INFO] Code-quality summary: 1192 functions, avg complexity 2.8
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `https://***@github.com/lph-dev-coder/LegaLinkk.git` (lph-dev-coder/LegaLinkk)
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
1192 functions analyzed by Lizard across .py, .ts, .tsx; 25 exceed complexity 15; average cyclomatic complexity 2.8.

#### Impact
Overall maintainability snapshot of the repository.

#### Remediation Guidance
Address the highest-complexity and longest functions listed above first.

---

### Issue 158: [INFO] Duplicated code block
- **Category:** Duplication
- **Severity:** info
- **Affected:** `frontend/src/services/agents.ts:82` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `duplication:copy-paste`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
16 duplicated lines: frontend/src/services/agents.ts:82-97 is a copy of frontend/src/services/chat.ts:328-344.

#### Impact
Duplicated code must be fixed in every copy; divergence causes bugs and inflates maintenance.

#### Remediation Guidance
Extract the shared logic into a single reusable function/module and call it from both places.

---

### Issue 159: [INFO] Duplicated code block
- **Category:** Duplication
- **Severity:** info
- **Affected:** `backend/app/services/agent_stream.py:205` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `duplication:copy-paste`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
13 duplicated lines: backend/app/services/agent_stream.py:205-217 is a copy of backend/app/services/agent_stream.py:146-158.

#### Impact
Duplicated code must be fixed in every copy; divergence causes bugs and inflates maintenance.

#### Remediation Guidance
Extract the shared logic into a single reusable function/module and call it from both places.

---

### Issue 160: [INFO] Duplicated code block
- **Category:** Duplication
- **Severity:** info
- **Affected:** `backend/app/models/conversation.py:49` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `duplication:copy-paste`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
14 duplicated lines: backend/app/models/conversation.py:49-62 is a copy of backend/app/models/synthesis.py:68-82.

#### Impact
Duplicated code must be fixed in every copy; divergence causes bugs and inflates maintenance.

#### Remediation Guidance
Extract the shared logic into a single reusable function/module and call it from both places.

---

### Issue 161: [INFO] Duplicated code block
- **Category:** Duplication
- **Severity:** info
- **Affected:** `backend/app/models/analysis.py:62` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `duplication:copy-paste`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
19 duplicated lines: backend/app/models/analysis.py:62-80 is a copy of backend/app/models/synthesis.py:64-82.

#### Impact
Duplicated code must be fixed in every copy; divergence causes bugs and inflates maintenance.

#### Remediation Guidance
Extract the shared logic into a single reusable function/module and call it from both places.

---

### Issue 162: [INFO] Duplicated code block
- **Category:** Duplication
- **Severity:** info
- **Affected:** `backend/alembic/versions/008_document_analyses.py:31` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `duplication:copy-paste`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
26 duplicated lines: backend/alembic/versions/008_document_analyses.py:31-56 is a copy of backend/alembic/versions/011_document_syntheses.py:31-56.

#### Impact
Duplicated code must be fixed in every copy; divergence causes bugs and inflates maintenance.

#### Remediation Guidance
Extract the shared logic into a single reusable function/module and call it from both places.

---

### Issue 163: [INFO] Python code smell: RUF022 unsorted dunder all
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/agents/nodes/__init__.py:24` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:RUF022`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`__all__` is not sorted (ruff RUF022) at backend/app/agents/nodes/__init__.py:24.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Ruff offers an automatic unsafe fix: Apply an isort-style sorting to `__all__`. Run `ruff check --fix` and review the diff.

---

### Issue 164: [INFO] Python code smell: RUF022 unsorted dunder all
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/agents/prompt_catalog.py:67` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:RUF022`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`__all__` is not sorted (ruff RUF022) at backend/app/agents/prompt_catalog.py:67.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Ruff offers an automatic safe fix: Apply an isort-style sorting to `__all__`. Run `ruff check --fix` and review the diff.

---

### Issue 165: [INFO] Python code smell: RUF022 unsorted dunder all
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/agents/legal.py:261` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:RUF022`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`__all__` is not sorted (ruff RUF022) at backend/app/agents/legal.py:261.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Ruff offers an automatic safe fix: Apply an isort-style sorting to `__all__`. Run `ruff check --fix` and review the diff.

---

### Issue 166: [INFO] Python code smell: RUF022 unsorted dunder all
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/agents/nodes/agent_prompts.py:127` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:RUF022`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`__all__` is not sorted (ruff RUF022) at backend/app/agents/nodes/agent_prompts.py:127.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Ruff offers an automatic safe fix: Apply an isort-style sorting to `__all__`. Run `ruff check --fix` and review the diff.

---

### Issue 167: [INFO] Python code smell: RUF022 unsorted dunder all
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/models/__init__.py:18` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:RUF022`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`__all__` is not sorted (ruff RUF022) at backend/app/models/__init__.py:18.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Ruff offers an automatic safe fix: Apply an isort-style sorting to `__all__`. Run `ruff check --fix` and review the diff.

---

### Issue 168: [INFO] Python code smell: PERF401 manual list comprehension
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/schemas/conversation.py:56` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PERF401`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Use `list.extend` to create a transformed list (ruff PERF401) at backend/app/schemas/conversation.py:56.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/manual-list-comprehension

---

### Issue 169: [INFO] Python code smell: PERF203 try except in loop
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/services/chat_job.py:173` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PERF203`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`try`-`except` within a loop incurs performance overhead (ruff PERF203) at backend/app/services/chat_job.py:173.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/try-except-in-loop

---

### Issue 170: [INFO] Python code smell: PERF401 manual list comprehension
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/services/conversation.py:175` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PERF401`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Use a list comprehension to create a transformed list (ruff PERF401) at backend/app/services/conversation.py:175.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/manual-list-comprehension

---

### Issue 171: [INFO] Python code smell: RUF022 unsorted dunder all
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/services/generator.py:1451` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:RUF022`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`__all__` is not sorted (ruff RUF022) at backend/app/services/generator.py:1451.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Ruff offers an automatic safe fix: Apply an isort-style sorting to `__all__`. Run `ruff check --fix` and review the diff.

---

### Issue 172: [INFO] Python code smell: RUF022 unsorted dunder all
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/services/llm/openai_compatible.py:12` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:RUF022`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`__all__` is not sorted (ruff RUF022) at backend/app/services/llm/openai_compatible.py:12.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Ruff offers an automatic safe fix: Apply an isort-style sorting to `__all__`. Run `ruff check --fix` and review the diff.

---

### Issue 173: [INFO] Python code smell: RUF022 unsorted dunder all
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/services/progress.py:258` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:RUF022`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`__all__` is not sorted (ruff RUF022) at backend/app/services/progress.py:258.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Ruff offers an automatic safe fix: Apply an isort-style sorting to `__all__`. Run `ruff check --fix` and review the diff.

---

### Issue 174: [INFO] Python code smell: E402 module import not at top of file
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/scripts/probe_paddle_import.py:11` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:E402`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Module level import not at top of file (ruff E402) at backend/scripts/probe_paddle_import.py:11.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/module-import-not-at-top-of-file

---

### Issue 175: [INFO] Python code smell: PERF203 try except in loop
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/scripts/dedupe_documents.py:98` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PERF203`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`try`-`except` within a loop incurs performance overhead (ruff PERF203) at backend/app/scripts/dedupe_documents.py:98.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/try-except-in-loop

---

### Issue 176: [INFO] Python code smell: PERF401 manual list comprehension
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/services/chunker.py:176` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PERF401`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Use `list.extend` to create a transformed list (ruff PERF401) at backend/app/services/chunker.py:176.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/manual-list-comprehension

---

### Issue 177: [INFO] Python code smell: RUF005 collection literal concatenation
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/services/generator.py:1152` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:RUF005`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
Consider iterable unpacking instead of concatenation (ruff RUF005) at backend/app/services/generator.py:1152.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Ruff offers an automatic unsafe fix: Replace with iterable unpacking. Run `ruff check --fix` and review the diff.

---

### Issue 178: [INFO] Python code smell: PERF203 try except in loop
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/services/indexing.py:209` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PERF203`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`try`-`except` within a loop incurs performance overhead (ruff PERF203) at backend/app/services/indexing.py:209.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/try-except-in-loop

---

### Issue 179: [INFO] Python code smell: RUF022 unsorted dunder all
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/services/llm/providers.py:43` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:RUF022`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`__all__` is not sorted (ruff RUF022) at backend/app/services/llm/providers.py:43.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Ruff offers an automatic safe fix: Apply an isort-style sorting to `__all__`. Run `ruff check --fix` and review the diff.

---

### Issue 180: [INFO] Python code smell: PERF203 try except in loop
- **Category:** Maintainability
- **Severity:** info
- **Affected:** `backend/app/services/reranker.py:294` (lph-dev-coder/LegaLinkk)
- **Rule ID:** `ruff:PERF203`
- **Estimated Effort:** 5min
- **Confidence:** high
- **Status:** confirmed
- **Lifecycle State:** open

#### Evidence
`try`-`except` within a loop incurs performance overhead (ruff PERF203) at backend/app/services/reranker.py:294.

#### Impact
Code smells accumulate: dead imports, over-long signatures and needlessly complex expressions make the module harder to read, review, and change safely.

#### Remediation Guidance
Apply the rule's guidance: https://docs.astral.sh/ruff/rules/try-except-in-loop

---
