import json
import os
import pandas as pd
from collections import Counter, defaultdict
from typing import List, Dict, Optional, Any
import re

class HistoricalMarketData:
    def __init__(self):
        self.base_path = "/home/vinay/Desktop/Projects/Edunovas-main/backend/JOBS DATASET"
        self._data: List[Dict[str, Any]] = []
        self._load_all_datasets()

    def _load_all_datasets(self):
        print("🔍 Loading Global Job Datasets...")
        
        # 1. Main JSON Archives
        self._load_json(os.path.join(self.base_path, "Gathered_Job_Data_2021_2025.json"), "Archive (Indeed India 21-25)")
        self._load_json(os.path.join(self.base_path, "Enriched_Fraud_Intelligence.json"), "Archive (Risk Data)")
        
        # 2. LDJSON (Indeed India)
        self._load_ldjson(os.path.join(self.base_path, "Job Dataset Indeed India.ldjson"), "Indeed India")
        
        # 3. Naukri CSVs (in folder)
        naukri_dir = os.path.join(self.base_path, "Job Postings Dataset from Naukri.com")
        if os.path.exists(naukri_dir):
            for f in os.listdir(naukri_dir):
                if f.endswith(".csv"):
                    self._load_naukri_csv(os.path.join(naukri_dir, f))

        print(f"✅ Total Historical Pool: {len(self._data)} records across 2021-2025.")

    def _load_json(self, path: str, source: str):
        if not os.path.exists(path): return
        try:
            with open(path, 'r') as f:
                raw_data = json.load(f)
                for r in raw_data:
                    title = str(r.get('title', r.get('job_title', ''))).strip()
                    if not title: continue
                    
                    year = "2021"
                    d = r.get('date', r.get('post_date', ''))
                    if d and '-' in d:
                        year = d.split('-')[0]
                    else:
                        y_raw = str(r.get('year', ''))
                        if y_raw and '-' in y_raw: year = y_raw.split('-')[0]
                        elif y_raw.isdigit(): year = y_raw
                    
                    self._data.append({
                        'title': title,
                        'company': str(r.get('company', r.get('company_name', 'Unknown'))),
                        'domain': str(r.get('domain', r.get('category', 'Technology'))),
                        'year_val': year if (year and year.isdigit()) else '2021',
                        'source': source
                    })
        except Exception as e: print(f"Error loading {path}: {e}")

    def _load_ldjson(self, path: str, source: str):
        if not os.path.exists(path): return
        try:
            with open(path, 'r') as f:
                for line in f:
                    if not line.strip(): continue
                    r = json.loads(line)
                    title = r.get('job_title', '')
                    if not title: continue
                    
                    year = "2021"
                    d = r.get('post_date', r.get('crawl_timestamp', ''))
                    if d and '-' in d: year = d.split('-')[0]
                    
                    self._data.append({
                        'title': title,
                        'company': r.get('company_name', 'Unknown'),
                        'domain': r.get('category', 'Technology'),
                        'year_val': year if (year and year.isdigit()) else '2021',
                        'source': source
                    })
        except Exception as e: print(f"Error loading {path}: {e}")

    def _load_naukri_csv(self, path: str):
        if not os.path.exists(path): return
        try:
            df = pd.read_csv(path)
            # Naukri data doesn't have explicit year in the samples I saw, assuming 2023 for this set
            for _, row in df.iterrows():
                self._data.append({
                    'title': str(row.get('Job_Titles', '')),
                    'company': str(row.get('Company_Names', 'Naukri.com')),
                    'domain': 'Data Science' if 'Science' in path else 'Analytics',
                    'year_val': '2023',
                    'source': 'Naukri Archive'
                })
        except Exception as e: print(f"Error loading {path}: {e}")

    def get_role_trends(self, role: str, domain: Optional[str] = None) -> Dict[str, Any]:
        if not self._data: return {"trend_line": [], "top_historical_companies": [], "total_historical_records": 0}
        
        role_q = (role or "").lower()
        dom_q = (domain or "").lower()
        matches = []
        
        for record in self._data:
            title = record['title'].lower()
            rec_dom = record['domain'].lower()
            if (role_q and role_q in title) or (dom_q and dom_q in rec_dom):
                matches.append(record)
        
        # Broaden if too sparse
        if len(matches) < 10 and dom_q:
            matches = [r for r in self._data if dom_q in r['domain'].lower()]

        yearly_counts = Counter()
        for m in matches:
            yearly_counts[m['year_val']] += 1
        
        trend_line = []
        for year in ['2021', '2022', '2023', '2024', '2025']:
            trend_line.append({"year": year, "count": yearly_counts.get(year, 0)})

        companies = Counter(m['company'] for m in matches if m['company'] != 'nan').most_common(5)
        
        return {
            "trend_line": trend_line,
            "top_historical_companies": [{"name": c, "count": n} for c, n in companies],
            "total_historical_records": len(matches)
        }

    def get_market_overview(self) -> Dict[str, Any]:
        if not self._data: return {"top_historical_domains": [], "top_historical_roles": [], "overall_trend": []}
        
        domains = Counter(r['domain'] for r in self._data).most_common(10)
        roles = Counter(r['title'] for r in self._data).most_common(10)
        
        year_counts = Counter(r['year_val'] for r in self._data)
        trend = []
        for y in ['2021', '2022', '2023', '2024', '2025']:
            trend.append({"year": y, "count": year_counts.get(y, 0)})

        return {
            "top_historical_domains": [{"name": d, "count": c} for d, c in domains if d != 'nan'],
            "top_historical_roles": [{"name": r, "count": c} for r, c in roles if r != 'nan'],
            "overall_trend": trend
        }

class JobRiskService:
    def __init__(self, csv_path: str = "/home/vinay/Desktop/Projects/Edunovas-main/backend/JOBS DATASET/fake_job_postings.csv"):
        self.csv_path = csv_path
        self._df: Optional[pd.DataFrame] = None
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.csv_path): return
        try:
            self._df = pd.read_csv(self.csv_path)
        except: pass

    def analyze_risk(self, title: str, description: str = "") -> Dict[str, Any]:
        if self._df is None: return {"score": 0, "level": "Low", "reasons": []}
        tq = title.lower()
        fraudulent = self._df[self._df['fraudulent'] == 1]
        matches = fraudulent[fraudulent['title'].str.contains(tq, case=False, na=False)]
        
        score = 0
        reasons = []
        if len(matches) > 2:
            score += 48
            reasons.append(f"Matching historical profile: {len(matches)} recruitment fraud cases share this job title.")
        
        flags = ["payment", "transfer", "bank account", "processing fee", "whatsapp", "telegram", "easy money", "investment", "work from home"]
        desc_l = (description.lower() + " " + title.lower())
        found = [f for f in flags if f in desc_l]
        if found:
            score += len(found) * 12
            reasons.append(f"Fraudulent indicators detected: {', '.join(found)}")
            
        score = min(score, 100)
        lvl = "High" if score > 68 else ("Moderate" if score > 35 else "Low")
        return {"score": score, "level": lvl, "reasons": reasons if reasons else ["Role appears historically stable with no major recruitment risk flags."]}

    def get_fraud_overview(self) -> Dict[str, Any]:
        if self._df is None: return {"top_risk_industries": [], "top_risk_roles": [], "total_fraud_cases": 0}
        fraudulent = self._df[self._df['fraudulent'] == 1]
        ind = fraudulent['industry'].value_counts().head(5).to_dict()
        tls = fraudulent['title'].value_counts().head(5).to_dict()
        return {
            "top_risk_industries": [{"name": str(k), "count": int(v)} for k, v in ind.items()],
            "top_risk_roles": [{"name": str(k), "count": int(v)} for k, v in tls.items()],
            "total_fraud_cases": len(fraudulent)
        }

# Global instances
historical_service = HistoricalMarketData()
risk_service = JobRiskService()
