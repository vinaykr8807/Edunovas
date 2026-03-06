export interface Milestone {
    title: string;
    description: string;
    skills: string[];
}

export interface Roadmap {
    id: string;
    title: string;
    icon: string;
    color: string;
    description: string;
    difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
    duration: string;
    phases: {
        name: string;
        milestones: Milestone[];
    }[];
}

export const CURRICULUM_DATA: Roadmap[] = [
    {
        id: 'cs-dsa',
        title: 'Core CS & Algorithms',
        icon: '💻',
        color: '#6366f1',
        description: 'Master the mathematical foundations, system architectures, and complex data structures that power modern computing.',
        difficulty: 'Intermediate',
        duration: '9 Months',
        phases: [
            {
                name: 'CS Foundations & Logic',
                milestones: [
                    {
                        title: 'Discrete Math & Digital Logic',
                        description: 'Set theory, Graph theory, and Logic gates combined with CPU Organization and Memory Hierarchy.',
                        skills: ['Discrete Math', 'Digital Logic', 'Architecture', 'Boolean Algebra']
                    },
                    {
                        title: 'Modern OS & Networking',
                        description: 'Process management, Paging, and the OSI model from Physical to Application layers.',
                        skills: ['OS', 'Linux Kernel', 'TCP/IP', 'Networking']
                    }
                ]
            },
            {
                name: 'Data Structures & Complexity',
                milestones: [
                    {
                        title: 'Linear & Hierarchical Structures',
                        description: 'Implementation of Arrays, Linked Lists, Stacks/Queues, and advanced Trees (BST, AVL, Segment).',
                        skills: ['Arrays', 'Linked Lists', 'Trees', 'Heaps']
                    },
                    {
                        title: 'Algorithmic Complexity',
                        description: 'Big-O notation, Master Theorem, and analysis of Search/Sort algorithms.',
                        skills: ['Complexity', 'Big-O', 'Sorting', 'Searching']
                    }
                ]
            },
            {
                name: 'Advanced Algorithms',
                milestones: [
                    {
                        title: 'Dynamic Programming & Greedy',
                        description: 'Solving complex optimization problems using memoization and greedy strategies.',
                        skills: ['DP', 'Greedy', 'Recursion', 'Optimization']
                    },
                    {
                        title: 'Graph Theory & Network Flow',
                        description: 'Shortest paths (Dijkstra/Bellman), MSTs (Prim/Kruskal), and Ford-Fulkerson network flow.',
                        skills: ['Graphs', 'BFS/DFS', 'Dijkstra', 'Network Flow']
                    }
                ]
            },
            {
                name: 'Software Theory & Career',
                milestones: [
                    {
                        title: 'Theory of Computation',
                        description: 'Automata Theory (DFA/NFA), Regular Expressions, and Complexity Classes (P vs NP).',
                        skills: ['Automata', 'Context-free Grammar', 'Turing Machines', 'Parsing']
                    },
                    {
                        title: 'Competitive Programming',
                        description: 'Pattern matching, sliding windows, and high-performance problem solving for FAANG interviews.',
                        skills: ['LeetCode', 'Optimization', 'String Matching', 'Patterns']
                    }
                ]
            }
        ]
    },
    {
        id: 'data-mlops',
        title: 'Data Engineering & MLOps',
        icon: '📊',
        color: '#0ea5e9',
        description: 'Build robust data pipelines and production ML platforms, bridging the gap between data science and reliable engineering.',
        difficulty: 'Advanced',
        duration: '8 Months',
        phases: [
            {
                name: 'Big Data Foundations',
                milestones: [
                    {
                        title: 'Distributed Systems Core',
                        description: 'Mastering Hadoop/HDFS, Spark DataFrames, and Cloud Data Warehouses (BigQuery/Snowflake).',
                        skills: ['Spark', 'HDFS', 'Snowflake', 'BigQuery']
                    },
                    {
                        title: 'Advanced SQL & NoSQL',
                        description: 'Complex transformations, Star/Snowflake schemas, and Document/Key-Value data modeling.',
                        skills: ['PostgreSQL', 'MongoDB', 'Data Modeling', 'ETL']
                    }
                ]
            },
            {
                name: 'Pipeline Engineering',
                milestones: [
                    {
                        title: 'Ingestion & ETL/ELT',
                        description: 'Streaming (Kafka/Kinesis) vs Batch ingestion and Change Data Capture (CDC) patterns.',
                        skills: ['Kafka', 'Kinesis', 'CDC', 'Apache Flink']
                    },
                    {
                        title: 'Workflow Orchestration',
                        description: 'Designing data lineages and dependency graphs using Airflow, Prefect, or Dagster.',
                        skills: ['Airflow', 'Orchestration', 'Lineage', 'Metadata']
                    }
                ]
            },
            {
                name: 'ML Production Systems',
                milestones: [
                    {
                        title: 'Experiment & Feature Stores',
                        description: 'Versioning data with DVC, tracking experiments with MLflow, and building feature stores.',
                        skills: ['DVC', 'MLflow', 'Feature Stores', 'Versioning']
                    },
                    {
                        title: 'Model Serving & IaC',
                        description: 'Deploying Model-as-a-Service (gRPC/REST) using Docker/Kubernetes and monitoring drift.',
                        skills: ['Model Serving', 'Kubernetes', 'Drift Monitoring', 'gRPC']
                    }
                ]
            }
        ]
    },
    {
        id: 'fsd',
        title: 'Full Stack Development',
        icon: '🌐',
        color: '#3b82f6',
        description: 'Master modern web architecture from semantic frontend design to scalable backend systems and DevOps pipelines.',
        difficulty: 'Intermediate',
        duration: '6 Months',
        phases: [
            {
                name: 'Web Foundations & Frontend Mastery',
                milestones: [
                    {
                        title: 'Internet & Core Web Tech',
                        description: 'How the web works, DNS, SSL, and mastery of Semantic HTML5, CSS3/Tailwind, and Responsive Design.',
                        skills: ['HTML5', 'CSS3', 'Tailwind', 'Accessibility']
                    },
                    {
                        title: 'JavaScript & React Ecosystem',
                        description: 'ES6+ Foundations, Async JS, and deep dive into React Hooks, Context API, and State Management (Redux/Zustand).',
                        skills: ['JavaScript', 'React', 'Hooks', 'State Management']
                    }
                ]
            },
            {
                name: 'Backend Architecture & Data',
                milestones: [
                    {
                        title: 'Node.js & Express Systems',
                        description: 'Building production-grade REST APIs, Middleware design, Authentication (JWT/OAuth), and RBAC.',
                        skills: ['Node.js', 'Express', 'Auth', 'Security']
                    },
                    {
                        title: 'Database Persistence Layers',
                        description: 'Schema design & migrations for SQL (PostgreSQL/MySQL) and NoSQL (MongoDB), using ORMs like Prisma/Mongoose.',
                        skills: ['PostgreSQL', 'MongoDB', 'Prisma', 'Redis']
                    }
                ]
            },
            {
                name: 'DevOps, Operations & Scaling',
                milestones: [
                    {
                        title: 'Containers & CI/CD Pipelines',
                        description: 'Dockerization, Multi-service orchestration with Compose, and automated pipelines with GitHub Actions.',
                        skills: ['Docker', 'CI/CD', 'GitHub Actions', 'Vercel']
                    },
                    {
                        title: 'System Design & Performance',
                        description: 'Monolith vs Microservices, Load balancing, Caching strategies, and Database Sharding/Replication.',
                        skills: ['System Design', 'Microservices', 'Scalability', 'Lighthouse']
                    }
                ]
            },
            {
                name: 'Advanced Systems & Career Engineering',
                milestones: [
                    {
                        title: 'Real-time & Security Mastery',
                        description: 'Implement WebSockets, GraphQL, and Event-driven architectures while ensuring OWASP Top 10 compliance.',
                        skills: ['WebSockets', 'GraphQL', 'Security', 'Testing']
                    },
                    {
                        title: 'Professional Engineering & Portfolio',
                        description: 'Agile methodologies, Technical Documentation, and high-impact portfolio building for Senior interviews.',
                        skills: ['Agile', 'Documentation', 'Interview Prep', 'Ethics']
                    }
                ]
            }
        ]
    },
    {
        id: 'aiml',
        title: 'Generative AI & Machine Learning',
        icon: '🧠',
        color: '#8b5cf6',
        description: 'From statistical foundations to building specialized Large Language Models and Agentic AI systems.',
        difficulty: 'Advanced',
        duration: '12 Months',
        phases: [
            {
                name: 'Foundations of AI & ML',
                milestones: [
                    {
                        title: 'Mathematics & Programming',
                        description: 'Master Linear Algebra, Multi-variable Calculus, and Probability Theory while mastering Python, NumPy, and PyTorch.',
                        skills: ['Linear Algebra', 'Calculus', 'PyTorch', 'JAX']
                    },
                    {
                        title: 'Classical Machine Learning',
                        description: 'Build the ML Lifecycle: Data cleaning, feature engineering, and training algorithms like SVMs and Random Forests.',
                        skills: ['Scikit-Learn', 'Feature Engineering', 'Optimization', 'Statistics']
                    }
                ]
            },
            {
                name: 'Deep Learning Mastery',
                milestones: [
                    {
                        title: 'Neural Network Architectures',
                        description: 'Implementation of MLPs, CNNs (ResNet, EfficientNet), and Sequential models like LSTMs/GRUs from scratch.',
                        skills: ['Backpropagation', 'CNNs', 'RNNs', 'Activation Functions']
                    },
                    {
                        title: 'Optimization & Regularization',
                        description: 'Master Adam variants, Weight Initialization (Xavier/He), and preventing Vanishing Gradients.',
                        skills: ['SGD', 'Dropout', 'Batch Norm', 'Entropy']
                    }
                ]
            },
            {
                name: 'The Generative AI Core',
                milestones: [
                    {
                        title: 'Transformers & Self-Attention',
                        description: 'Detailed study of the Attention mechanism, Multi-head attention, and Transformer architectures (BERT, GPT, T5).',
                        skills: ['Attention', 'Transformers', 'Positional Encoding', 'BERT']
                    },
                    {
                        title: 'LLM Training & Tuning',
                        description: 'End-to-end LLM lifecycle: Pretraining, Fine-tuning (PEFT, LoRA), and RLHF (Reinforcement Learning from Human Feedback).',
                        skills: ['LLMs', 'LoRA', 'PEFT', 'RLHF', 'Fine-Tuning']
                    },
                    {
                        title: 'Diffusion & Image Gen',
                        description: 'Math behind Denoising Diffusion Probabilistic Models (DDPM) and Latent Diffusion (Stable Diffusion).',
                        skills: ['Diffusion', 'DDPM', 'Stable Diffusion', 'CLIP']
                    }
                ]
            },
            {
                name: 'Agentic AI & Advanced Systems',
                milestones: [
                    {
                        title: 'Agentic Architectures',
                        description: 'Building autonomous agents using loops (ReAct), planning mechanisms, and self-correction (Reflection).',
                        skills: ['ReAct', 'AutoGPT', 'Cognitive Architectures', 'Reflexion']
                    },
                    {
                        title: 'RAG & Industry Infrastructure',
                        description: 'Designing Retrieval-Augmented Generation systems with Vector Databases and Mixture of Experts (MoE).',
                        skills: ['RAG', 'Vector DBs', 'MoE', 'FAISS', 'Pinecone']
                    },
                    {
                        title: 'AI Safety & Future Frontiers',
                        description: 'Implementing Explainability, ethics, and exploring research into Quantum Machine Learning and AGI.',
                        skills: ['Explainability', 'Ethics', 'Governance', 'Quantum AI']
                    }
                ]
            }
        ]
    },
    {
        id: 'cyber',
        title: 'Cyber Security',
        icon: '🛡️',
        color: '#ef4444',
        description: 'Master the art of digital defense and ethical hacking, from network hardening to advanced incident response and cloud security.',
        difficulty: 'Intermediate',
        duration: '8 Months',
        phases: [
            {
                name: 'Foundations & Network Hardening',
                milestones: [
                    {
                        title: 'Core Architecture & Networking',
                        description: 'CIA Triad, TCP/IP, OSI Model, and securing network devices like Firewalls and IDS/IPS.',
                        skills: ['Networking', 'TCP/IP', 'Linux', 'Firewalls']
                    },
                    {
                        title: 'OS Security & Endpoint Defense',
                        description: 'Hardening Windows/Linux, managing permissions, GPOs, and implementing EDR/Antivirus solutions.',
                        skills: ['Windows Security', 'Permissions', 'Hardening', 'EDR']
                    }
                ]
            },
            {
                name: 'Application Security & Cryptography',
                milestones: [
                    {
                        title: 'Cryptography & PKI',
                        description: 'Symmetric/Asymmetric encryption, Hashing, Digital Signatures, and TLS/SSL handshake mechanics.',
                        skills: ['Encryption', 'AES/RSA', 'Hashing', 'TLS']
                    },
                    {
                        title: 'Web Security & DevSecOps',
                        description: 'OWASP Top 10 (SQLi, XSS, CSRF), Secure Coding, and shifting security left with SAST/DAST.',
                        skills: ['OWASP', 'Burp Suite', 'DevSecOps', 'Threat Modeling']
                    }
                ]
            },
            {
                name: 'Offensive & Defensive Operations',
                milestones: [
                    {
                        title: 'Ethical Hacking (Red Team)',
                        description: 'Pentesting lifecycle: Reconnaissance, Vulnerability Scanning (Nmap), Exploitation (Metasploit), and Post-Exploitation.',
                        skills: ['Nmap', 'Metasploit', 'Kali Linux', 'Social Engineering']
                    },
                    {
                        title: 'SOC & Incident Response (Blue Team)',
                        description: 'SOC operations, SIEM (Splunk/Sentinel), Log analysis, and Digital Forensics/Incident lifecycle.',
                        skills: ['SIEM', 'Logs', 'Wireshark', 'Forensics']
                    }
                ]
            },
            {
                name: 'Cloud, GRC & Professional Engineering',
                milestones: [
                    {
                        title: 'Cloud Security & Governance',
                        description: 'Shared Responsibility, IAM, Cloud WAF, and GRC frameworks like NIST, ISO 27001, and GDPR.',
                        skills: ['Cloud Security', 'IAM', 'Compliance', 'Risk Management']
                    },
                    {
                        title: 'Career & Incident Readiness',
                        description: 'Building IR Playbooks, Home Labs (HTB/THM), Certification pathways (Security+/OSCP), and Ethical Disclosure.',
                        skills: ['IR Playbooks', 'Ethics', 'Certs', 'Zero Trust']
                    }
                ]
            }
        ]
    },
    {
        id: 'devops',
        title: 'DevOps & Cloud Engineering',
        icon: '♾️',
        color: '#10b981',
        description: 'Complete lifecycle automation: from Linux foundations and CI/CD to Kubernetes orchestration and SRE reliability.',
        difficulty: 'Intermediate',
        duration: '7 Months',
        phases: [
            {
                name: 'Systems & Automation Foundations',
                milestones: [
                    {
                        title: 'Linux & Scripting',
                        description: 'Mastering the Linux filesystem, permissions, and automation using Bash/Shell scripting.',
                        skills: ['Linux', 'Bash', 'Networking', 'Git']
                    },
                    {
                        title: 'CI/CD & Config Management',
                        description: 'Implementing automated pipelines with GitHub Actions and managing environments with Ansible.',
                        skills: ['CI/CD', 'GitHub Actions', 'Ansible', 'Jenkins']
                    }
                ]
            },
            {
                name: 'Cloud-Native & Containers',
                milestones: [
                    {
                        title: 'Docker & Containerization',
                        description: 'Building optimized images, multi-container orchestration, and image security best practices.',
                        skills: ['Docker', 'Docker Compose', 'Security', 'Registry']
                    },
                    {
                        title: 'Kubernetes Orchestration',
                        description: 'Managing production clusters: Pods, Deployments, Services, and Helm package management.',
                        skills: ['Kubernetes', 'Helm', 'Ingress', 'K8s Architecture']
                    }
                ]
            },
            {
                name: 'Infrastructure as Code (IaC)',
                milestones: [
                    {
                        title: 'Terraform & Cloud Core',
                        description: 'Provisioning multi-cloud infrastructure (AWS/Azure/GCP) using declarative Terraform modules.',
                        skills: ['Terraform', 'AWS/Azure', 'IaC', 'VPC/IAM']
                    },
                    {
                        title: 'GitOps & Advanced Delivery',
                        description: 'Continuous deployment using GitOps patterns with ArgoCD and progressive delivery (Canary/Blue-Green).',
                        skills: ['ArgoCD', 'GitOps', 'Canary', 'Service Mesh']
                    }
                ]
            },
            {
                name: 'SRE & Observability',
                milestones: [
                    {
                        title: 'Monitoring & Logging',
                        description: 'Implementing the 3 pillars of observability: Prometheus metrics, Grafana dashboards, and ELK logging.',
                        skills: ['Prometheus', 'Grafana', 'ELK Stack', 'Tracing']
                    },
                    {
                        title: 'SRE & Incident Management',
                        description: 'Reliability engineering: SLOs, Error Budgets, Toil reduction, and Post-incident analysis.',
                        skills: ['SRE', 'Incident Response', 'SLOs', 'Postmortems']
                    }
                ]
            }
        ]
    },
    {
        id: 'cloud',
        title: 'Cloud Solutions Architecture',
        icon: '☁️',
        color: '#06b6d4',
        description: 'Design resilient, highly-available, and cost-effective distributed systems on global cloud providers.',
        difficulty: 'Advanced',
        duration: '6 Months',
        phases: [
            {
                name: 'Cloud Architecture Core',
                milestones: [
                    {
                        title: 'Compute & Storage Design',
                        description: 'Architecting scalable workloads using EC2/VMs, S3/Blob storage, and managed Database systems.',
                        skills: ['AWS S3', 'EBS', 'Auto-scaling', 'High Availability']
                    },
                    {
                        title: 'Identity & Network Security',
                        description: 'Designing secure VPCs, Subnets, and complex IAM permission boundaries.',
                        skills: ['VPC Architecture', 'IAM', 'Security Groups', 'Cloud Networking']
                    }
                ]
            },
            {
                name: 'Serverless & Modern Apps',
                milestones: [
                    {
                        title: 'Event-Driven Serverless',
                        description: 'Building FaaS based applications using AWS Lambda, API Gateway, and managed Message Brokers.',
                        skills: ['Lambda', 'Serverless', 'EventBridge', 'DynamoDB']
                    },
                    {
                        title: 'Cloud Migration & FinOps',
                        description: 'Strategies for data migration and optimizing cloud spend through FinOps best practices.',
                        skills: ['Migration', 'FinOps', 'Cost Management', 'Gov Cloud']
                    }
                ]
            }
        ]
    },
    {
        id: 'quantum',
        title: 'Quantum Computing',
        icon: '⚛️',
        color: '#f59e0b',
        description: 'Step into the future of computation with qubits, entanglement, and quantum algorithms for a post-classical world.',
        difficulty: 'Advanced',
        duration: '12 Months',
        phases: [
            {
                name: 'Quantum Foundations',
                milestones: [
                    {
                        title: 'Linear Algebra & Dirac Notation',
                        description: 'Complex vector spaces, Hermitian operators, and Bra-Ket notation for quantum states.',
                        skills: ['Bra-Ket', 'Unitary Matrices', 'Operators', 'Complex Numbers']
                    },
                    {
                        title: 'Qubit Mechanics',
                        description: 'Superposition, Entanglement, Bloch Sphere, and Multi-qubit measurement probabilities.',
                        skills: ['Bloch Sphere', 'Qubits', 'Entanglement', 'Measurement']
                    }
                ]
            },
            {
                name: 'Gates & Circuit Theory',
                milestones: [
                    {
                        title: 'Quantum Gate Sets',
                        description: 'Mastering Single-qubit (Hadamard, Pauli) and Multi-qubit (CNOT, Toffoli) universal gate sets.',
                        skills: ['Hadamard', 'CNOT', 'Toffoli', 'Reversibility']
                    },
                    {
                        title: 'Circuit Composition',
                        description: 'Building and simulating quantum circuits, understanding decoherence, and noise models.',
                        skills: ['Circuit Design', 'Noise Models', 'Simulators', 'Unitary Ops']
                    }
                ]
            },
            {
                name: 'Algorithms & QML',
                milestones: [
                    {
                        title: 'Classic Quantum Algorithms',
                        description: "Implementation of Shor's integer factorization, Grover's search, and Quantum Fourier Transforms (QFT).",
                        skills: ['Shor', 'Grover', 'QFT', 'Factorization']
                    },
                    {
                        title: 'Variational & Hybrid AI',
                        description: 'VQE, QAOA, and Parameterized Quantum Circuits for hybrid classical-quantum machine learning.',
                        skills: ['VQE', 'QAOA', 'QML', 'Parameterized Circuits']
                    }
                ]
            },
            {
                name: 'Industry & Future Frontiers',
                milestones: [
                    {
                        title: 'Qiskit & Real Hardware',
                        description: 'Programming for IBM Quantum machines using Qiskit, Cirq, and cloud-based quantum backends.',
                        skills: ['Qiskit', 'Cirq', 'Cloud Quantum', 'Hardware']
                    },
                    {
                        title: 'Error Correction & Cryptography',
                        description: 'Fault-tolerant computing, Error correcting codes, and Post-Quantum Cryptographic impact.',
                        skills: ['Error Correction', 'Decoherence', 'Post-Quantum Crypto', 'Fault Tolerance']
                    }
                ]
            }
        ]
    },
    {
        id: 'uiux',
        title: 'UI/UX Design',
        icon: '🎨',
        color: '#ec4899',
        description: 'Design research-backed interfaces and human-centered user experiences from wireframes to high-fidelity prototypes.',
        difficulty: 'Beginner',
        duration: '5 Months',
        phases: [
            {
                name: 'UX Foundations & User Research',
                milestones: [
                    {
                        title: 'Design Principles & Research',
                        description: 'Visual laws (Contrast, Alignment) and qualitative/quantitative research methods like user interviews/surveys.',
                        skills: ['Color Theory', 'Typography', 'Heuristics', 'User Research']
                    },
                    {
                        title: 'Information Architecture',
                        description: 'Organizing content with Site Maps, Card Sorting, and defining complex Task/User flows.',
                        skills: ['IA', 'Sitemaps', 'User Flow', 'Task Analysis']
                    }
                ]
            },
            {
                name: 'Interaction Design & Prototyping',
                milestones: [
                    {
                        title: 'Figma & Components',
                        description: 'Mastering Auto-Layout, Atomic Design (Atoms to Organisms), and multi-state variant components.',
                        skills: ['Figma', 'Auto Layout', 'Atomic Design', 'Design Systems']
                    },
                    {
                        title: 'High-Fidelity Prototyping',
                        description: 'Creating interactive clickable flows, micro-interactions, and motion design for user feedback.',
                        skills: ['Prototyping', 'Interactions', 'Motion Design', 'Animation']
                    }
                ]
            },
            {
                name: 'Accessibility & Content Strategy',
                milestones: [
                    {
                        title: 'Inclusive Design (WCAG)',
                        description: 'Designing for accessibility: POUR principles, color contrast, and keyboard navigation focus states.',
                        skills: ['WCAG', 'Accessibility', 'Inclusive Design', 'ARIA']
                    },
                    {
                        title: 'UX Writing & Copy',
                        description: 'Crafting clear, empathetic microcopy for buttons, error states, and guided onboarding flows.',
                        skills: ['UX Writing', 'Content Strategy', 'Microcopy', 'Onboarding']
                    }
                ]
            },
            {
                name: 'Product Strategy & Quality',
                milestones: [
                    {
                        title: 'Data-Informed Iteration',
                        description: 'Using A/B testing, heatmaps, and usability testing to validate design hypotheses and improve metrics.',
                        skills: ['A/B Testing', 'Usability Testing', 'Analytics', 'Handoff']
                    },
                    {
                        title: 'Portfolio & Professionalism',
                        description: 'Writing deep-dive case studies (Process to Impact) and preparing high-impact designers portfolios.',
                        skills: ['Case Studies', 'Portfolio', 'Agile/Scrum', 'Stakeholder Comms']
                    }
                ]
            }
        ]
    }
];
