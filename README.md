# monitoring-stack

At my internship I built a monitoring system for a bunch of AIX and RHEL servers using sar, vmstat, and cronjobs that sent metric reports to my manager over email. It did the job but it was pretty manual because someone had to actually read the email and notice something was wrong. I wanted to see what that looks like when you build it properly.

Prometheus scrapes metrics from a FastAPI app, Grafana visualizes them, and Alertmanager fires a Slack notification when CPU or memory spikes past a threshold. Runs locally with docker compose up, and deploys to AWS automatically whenever I push to main.

---

## the stack

- **FastAPI** — exposes system metrics (CPU, memory, disk) at /metrics using psutil and prometheus-client
- **Prometheus** — scrapes that endpoint every 15 seconds, stores the data, evaluates alert rules
- **Grafana** — connects to Prometheus and renders dashboards via PromQL queries
- **Alertmanager** — receives alerts from Prometheus and routes them to Slack
- **Terraform** — provisions the EC2 instance, security group, and Elastic IP on AWS
- **GitHub Actions** — SSHes into the instance and redeploys the stack on every push to main

---

## running locally

```bash
git clone https://github.com/maxmg1187/monitoring-stack.git
cd monitoring-stack
docker compose up --build
```

then hit:
- http://localhost:8000/metrics — raw metrics output
- http://localhost:9090 — Prometheus UI
- http://localhost:3000 — Grafana (admin / admin)
- http://localhost:9093 — Alertmanager

first time in Grafana you'll need to add Prometheus as a data source (use `http://prometheus:9090`) and set up your dashboards. after that it all persists via a Docker volume so you won't lose your setup on restart.

---

## deploying to AWS

```bash
cd terraform
terraform init
terraform apply
```

that spins up a t3.micro EC2 instance with an Elastic IP and the right ports open. from there the GitHub Actions pipeline takes over and every push to main triggers a redeploy automatically.

you'll need these three secrets set in your repo settings:

- `EC2_HOST` — the Elastic IP from Terraform output
- `EC2_SSH_KEY` — your private key (the full thing including header/footer)
- `SLACK_WEBHOOK_URL` — incoming webhook from your Slack app

---

## alerting

two rules set up in `prometheus/alert_rules.yml`:

- CPU > 80% for 1 minute
- memory > 80% for 1 minute

the `for: 1m` part means Prometheus waits for the condition to hold continuously before firing or otherwise you'd get paged every time there's a random spike. learned that one while testing.

Slack webhook URL is stored as a GitHub Secret and injected at deploy time, never hardcoded anywhere. (ty github for never allowing this lol)

---

## stuff I'd improve

- add HTTPS — right now it's all plain HTTP which is fine for a personal project but not for anything real
- move Terraform state to S3 — the state file lives locally right now which works solo but would break in a team
- expand the metrics — currently just system-level stuff, would be cool to instrument the FastAPI app itself (request rate, latency, error rate)
- write runbooks — documentation for what each alert actually means and what to do when it fires
- maybe find something i can build for my personal life using these tools, but idk i just wanted to see what I could do for self-learning, my manager would be proud.
