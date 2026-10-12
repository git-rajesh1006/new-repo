import json
P = [
("Phase 1 — DevOps fundamentals", [
"What is DevOps? Explained with a real-world example","DevOps engineer: roles and responsibilities",
"DevOps lifecycle: Plan, Code, Build, Test, Release, Deploy, Operate, Monitor","Traditional IT vs DevOps",
"What is Agile and how does it connect to DevOps?","SDLC explained in 60 seconds","CI vs CD vs Continuous Deployment",
"DevOps tools roadmap for beginners","DevOps engineer skills and career path","Build your first DevOps learning roadmap"]),
("Phase 2 — Linux and shell scripting", [
"What is Linux and why DevOps uses it","Install Linux using a virtual machine or WSL","Essential Linux commands: pwd, ls, cd",
"File operations: touch, cp, mv, rm","File permissions: chmod and chown","Users, groups and sudo","Processes: ps, top and kill",
"Networking commands: curl, ping, ss","Bash scripting: variables, conditions and loops","Automate a backup with a Bash script"]),
("Phase 3 — Git and GitHub", [
"What is Git and why do developers need it?","Git installation and configuration","git init, git add and git commit",
"Push your first project to GitHub","Git branches and merging","Pull requests and code reviews","Resolve Git merge conflicts",
"Git workflow used by real teams"]),
("Phase 4 — CI/CD and Jenkins", [
"What is CI/CD?","How a CI/CD pipeline works","What is Jenkins?","Install Jenkins and explore its dashboard",
"Create your first Jenkins job","Jenkins pipelines and Jenkinsfile","Build and test code automatically",
"Webhooks: trigger builds on every Git push","Jenkins credentials and secrets","Build a GitHub-to-Jenkins pipeline"]),
("Phase 5 — Docker and containers", [
"What is Docker and why use containers?","Containers vs virtual machines","Docker architecture explained",
"Install Docker and run your first container","Docker images vs containers","Write your first Dockerfile",
"Docker volumes and persistent data","Docker networks","Docker Compose for multi-container apps",
"Build and publish an image to a container registry"]),
("Phase 6 — Cloud and AWS", [
"What is cloud computing?","IaaS vs PaaS vs SaaS","AWS global infrastructure: Regions and Availability Zones",
"IAM users, roles and policies","EC2: launch a virtual server","S3: cloud object storage","VPC, subnets and security groups",
"Load balancers and Auto Scaling","Route 53, DNS and domain routing","Deploy a web application on AWS"]),
("Phase 7 — Kubernetes", [
"What is Kubernetes?","Docker vs Kubernetes","Kubernetes architecture: control plane and worker nodes","Pods and containers",
"Deployments and ReplicaSets","Services: ClusterIP, NodePort and LoadBalancer","ConfigMaps and Secrets",
"Namespaces and resource limits","Persistent Volumes and Persistent Volume Claims","Liveness, readiness and startup probes",
"Rolling updates and rollbacks","Deploy a complete application to Kubernetes"]),
("Phase 8 — Infrastructure as Code", [
"What is Infrastructure as Code (IaC)?","Terraform vs Ansible","Terraform installation and providers",
"Resources, variables and outputs","terraform init, plan and apply","Terraform state and remote backends",
"Terraform modules and reusable code","Provision AWS infrastructure with Terraform"]),
("Phase 9 — Configuration management", [
"What is Ansible?","Ansible inventory and ad hoc commands","Playbooks, tasks and modules",
"Roles, variables and templates","Automate server setup using Ansible","Terraform + Ansible in one workflow"]),
("Phase 10 — Monitoring and observability", [
"Monitoring vs logging vs observability","Prometheus architecture and metrics","Grafana dashboards and visualizations",
"Centralized logging with the ELK/Elastic Stack","Alerts, SLI, SLO and SLA","Monitor an application and configure alerts"]),
("Phase 11 — DevSecOps and production skills", [
"What is DevSecOps?","SAST, DAST and dependency scanning","Container image scanning and vulnerability management",
"Secrets management and least privilege","Blue-green vs canary deployments","Troubleshooting failed deployments and rollbacks"]),
("Phase 12 — Real-world projects and career", [
"Build an end-to-end CI/CD pipeline","Deploy a containerized application to Kubernetes on AWS",
"DevOps interview questions and scenario-based answers","Build your DevOps portfolio and resume project"]),
]
days, n = [], 0
for phase, topics in P:
    for t in topics:
        n += 1; days.append({"day": n, "phase": phase, "title": t})
assert n == 100, n
json.dump({"reel_format": [
 {"name":"Hook","start":0,"end":3,"note":"Question, surprising fact or common problem"},
 {"name":"Explain","start":3,"end":15,"note":"Simple definition in everyday language"},
 {"name":"Demonstrate","start":15,"end":40,"note":"Terminal command, diagram, tool or real-world example"},
 {"name":"Recap + CTA","start":40,"end":60,"note":"Summarize and invite viewers to follow for the next day"}],
 "days": days}, open("syllabus.json","w"), indent=1, ensure_ascii=False)
print(n)
