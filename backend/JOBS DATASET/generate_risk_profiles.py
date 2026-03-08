import json
import os
from collections import defaultdict, Counter

INPUT_FILE = r"d:\India-Aware Recruitment Fraud Intelligence System\Gathered_Job_Data_2021_2025.json"
OUTPUT_FILE = r"d:\India-Aware Recruitment Fraud Intelligence System\Gathered_Job_Data_2021_2025.json"

class DomainRiskProfiler:
    def __init__(self):
        self.enriched_data = []
        self.risk_patterns = {
            'HIGH_IMPACT': {
                'whatsapp': 25,
                'call': 15,
                'registration fee': 40,
                'security deposit': 40,
                'daily pay': 35,
                'weekly pay': 30,
                'urgent': 10,
                'hiring now': 10,
                'no interview': 30,
                'no experience': 15
            },
            'DOMAINS_SUSCEPTIBLE': {
                'data entry': 20,
                'wfh': 15,
                'part time': 10,
                'back office': 15,
                'fresher': 10
            }
        }

    def infer_job_type(self, title, company):
        text = (str(title) + " " + str(company)).lower()
        if any(w in text for w in ['remote', 'wfh', 'work from home', 'stay at home', 'virtual']):
            return 'Remote'
        if any(w in text for w in ['hybrid', 'flexible', 'partial remote', 'work from office']):
            if 'hybrid' in text: return 'Hybrid'
        return 'Onsite' # Default to onsite for traditional archive entries

    def calculate_risk(self, job):
        score = 0
        title = str(job.get('title', '')).lower()
        company = str(job.get('company', '')).lower()
        source = str(job.get('source', '')).lower()
        
        # 1. Keywords check
        for kw, val in self.risk_patterns['HIGH_IMPACT'].items():
            if kw in title:
                score += val
        
        # 2. Domain specific check
        for kw, val in self.risk_patterns['DOMAINS_SUSCEPTIBLE'].items():
            if kw in title:
                score += val

        # 3. Company genericness
        if any(w in company for w in ['unspecified', 'reputed', 'major client', 'confidential']):
            score += 15
            
        # 4. Source Risk
        if 'olx' in source or 'quikr' in source:
            score += 20
            
        # 5. Remote + Data Entry Correction (High risk combo)
        if 'remote' in title and 'data entry' in title:
            score += 20

        return min(score, 100)

    def process(self):
        if not os.path.exists(INPUT_FILE):
            print("[!] Input file not found.")
            return

        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        profile_stats = defaultdict(lambda: {
            'count': 0, 
            'total_risk': 0, 
            'types': Counter(),
            'flagged_count': 0
        })

        for item in data:
            job_type = self.infer_job_type(item.get('title'), item.get('company'))
            risk_score = self.calculate_risk(item)
            domain = item.get('domain', 'Unknown')
            
            # Enrich item
            item['job_type'] = job_type
            item['risk_score'] = risk_score
            item['is_high_risk'] = risk_score > 50
            
            self.enriched_data.append(item)

            # Update stats
            stats = profile_stats[domain]
            stats['count'] += 1
            stats['total_risk'] += risk_score
            stats['types'][job_type] += 1
            if item['is_high_risk']:
                stats['flagged_count'] += 1

        # Save enriched data
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.enriched_data, f, indent=4)

        self.print_summary(profile_stats)

    def print_summary(self, stats):
        print("\n" + "="*100)
        print(f"{'DOMAIN':<25} | {'AVG RISK':<10} | {'ONSITE %':<10} | {'REMOTE %':<10} | {'HIGH RISK %'}")
        print("-" * 100)
        
        sorted_stats = sorted(stats.items(), key=lambda x: (x[1]['total_risk']/x[1]['count']), reverse=True)
        
        for domain, s in sorted_stats[:20]:
            count = s['count']
            avg_risk = s['total_risk'] / count
            onsite_p = (s['types']['Onsite'] / count) * 100
            remote_p = (s['types']['Remote'] / count) * 100
            high_risk_p = (s['flagged_count'] / count) * 100
            
            print(f"{domain[:25]:<25} | {avg_risk:<10.1f} | {onsite_p:<10.1f} | {remote_p:<10.1f} | {high_risk_p:<10.1f}")
        
        # New: Highest Risk Roles Table
        print("\n" + "="*100)
        print(f"{'HIGHEST RISK JOB TITLES (FLAGGED FOR INVESTIGATION)':<60} | {'RISK SCORE'}")
        print("-" * 100)
        high_risk_jobs = sorted([j for j in self.enriched_data if j['risk_score'] > 0], key=lambda x: x['risk_score'], reverse=True)
        for job in high_risk_jobs[:15]:
            title = str(job['title'])[:58]
            print(f"{title:<60} | {job['risk_score']}")
            
        print("="*100)
        print(f"[*] Enriched intelligence saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    profiler = DomainRiskProfiler()
    profiler.process()
