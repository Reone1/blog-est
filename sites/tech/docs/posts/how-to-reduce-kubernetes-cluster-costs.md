---
title: "How to Reduce Kubernetes Cluster Costs: A Practical Guide"
date: "2026-03-31"
type: "how-to"
description: "Learn proven strategies to cut Kubernetes cluster costs by 40-60% through right-sizing, autoscaling, spot instances, resource quotas, and cost monitoring with Kubecost."
keywords: "how to reduce kubernetes cluster costs, kubernetes cost optimization, kubernetes autoscaling, kubecost, karpenter"
---

# How to Reduce Kubernetes Cluster Costs: A Practical Guide

<div class="tldr">

**TL;DR:** Most Kubernetes clusters waste 50-70% of provisioned resources. You can dramatically cut costs by right-sizing workloads based on actual usage data, implementing HPA/VPA/Karpenter autoscaling, leveraging spot instances for fault-tolerant workloads, enforcing resource quotas per namespace, and monitoring spend with Kubecost. This guide walks through each strategy with concrete kubectl commands and configuration examples.

</div>

## Why Kubernetes Costs Spiral Out of Control

According to the Cloud Native Computing Foundation's 2025 survey, organizations running Kubernetes report an average of 65% resource over-provisioning. The root cause is straightforward: developers request generous CPU and memory limits during initial deployment, and nobody revisits those numbers once the service is running.

A typical pattern looks like this: a team requests 2 CPU cores and 4 GiB of memory for a service that actually uses 200m CPU and 512 MiB of memory at peak. Multiply that across hundreds of microservices, and you are paying for infrastructure that sits idle around the clock.

This guide covers five strategies that, applied together, can reduce your Kubernetes spend by 40-60%.

## Step 1: Right-Size Your Workloads

Right-sizing means aligning resource requests and limits with actual consumption. Before changing anything, you need data.

### Audit Current Resource Usage

Use `kubectl top` to get a snapshot of actual resource consumption:

```bash
# View CPU and memory usage for all pods in a namespace
kubectl top pods -n production --sort-by=memory

# View node-level resource consumption
kubectl top nodes

# Get resource requests vs actual usage for a specific deployment
kubectl get pods -n production -l app=api-server \
  -o custom-columns=\
  NAME:.metadata.name,\
  REQ_CPU:.spec.containers[0].resources.requests.cpu,\
  REQ_MEM:.spec.containers[0].resources.requests.memory,\
  LIM_CPU:.spec.containers[0].resources.limits.cpu,\
  LIM_MEM:.spec.containers[0].resources.limits.memory
```

For a more comprehensive view over time, query Prometheus directly:

```promql
# Average CPU usage over the last 7 days per container
avg_over_time(
  rate(container_cpu_usage_seconds_total{namespace="production"}[5m])[7d:1h]
) by (pod, container)
```

### Apply Right-Sized Resource Requests

Once you have usage data, update your deployment manifests. A good rule of thumb is to set requests at the P95 usage level and limits at 1.5-2x that value:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  template:
    spec:
      containers:
      - name: api-server
        resources:
          requests:
            cpu: "250m"
            memory: "512Mi"
          limits:
            cpu: "500m"
            memory: "1Gi"
```

## Step 2: Implement Autoscaling at Every Layer

Kubernetes supports multiple autoscaling mechanisms. Using them together provides the most efficient resource utilization.

### Horizontal Pod Autoscaler (HPA)

HPA scales the number of pod replicas based on observed metrics. Start with CPU-based scaling, then add custom metrics as needed:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-server-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

The `behavior` section is critical. Without a stabilization window, you risk flapping -- rapidly scaling up and down -- which causes instability and wasted resources.

### Vertical Pod Autoscaler (VPA)

VPA automatically adjusts resource requests based on historical usage. Install it and create a VPA object:

```bash
# Install VPA (if not already present)
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh
```

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-server-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: api-server
      minAllowed:
        cpu: "100m"
        memory: "128Mi"
      maxAllowed:
        cpu: "2"
        memory: "4Gi"
```

Important caveat: do not run HPA and VPA on the same CPU or memory metric simultaneously. Use HPA for scaling replica count based on CPU, and VPA for adjusting memory requests, or use custom metrics to avoid conflicts.

### Karpenter for Node-Level Autoscaling

Karpenter replaces the traditional Cluster Autoscaler with a more responsive, cost-aware node provisioner. It launches right-sized nodes in seconds rather than minutes:

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
      - key: karpenter.sh/capacity-type
        operator: In
        values: ["on-demand", "spot"]
      - key: node.kubernetes.io/instance-type
        operator: In
        values:
        - m6i.large
        - m6i.xlarge
        - m6a.large
        - m6a.xlarge
        - c6i.large
        - c6i.xlarge
      - key: topology.kubernetes.io/zone
        operator: In
        values: ["us-east-1a", "us-east-1b", "us-east-1c"]
  limits:
    cpu: "200"
    memory: "400Gi"
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 30s
```

Karpenter's consolidation feature is particularly powerful. It continuously evaluates whether workloads can be packed onto fewer or cheaper nodes, and it handles the migration automatically.

## Step 3: Leverage Spot Instances

Spot instances (AWS), preemptible VMs (GCP), or spot VMs (Azure) cost 60-90% less than on-demand pricing. The tradeoff is that the cloud provider can reclaim them with short notice.

### Identify Spot-Eligible Workloads

Good candidates for spot instances include:

- Stateless web servers behind a load balancer
- Batch processing jobs
- CI/CD build agents
- Data pipeline workers
- Development and staging environments

Poor candidates include single-replica databases, stateful services without replication, and anything with long graceful shutdown requirements.

### Configure Spot Instance Handling

Ensure your workloads handle interruptions gracefully:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
spec:
  replicas: 5
  template:
    spec:
      terminationGracePeriodSeconds: 120
      nodeSelector:
        karpenter.sh/capacity-type: spot
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: worker
      containers:
      - name: worker
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 10 && /app/drain.sh"]
```

The topology spread constraint ensures pods are distributed across availability zones, so a spot interruption in one zone does not take down all replicas.

## Step 4: Enforce Resource Quotas and Limit Ranges

Without guardrails, any team can deploy workloads that consume unlimited resources. Resource quotas prevent this.

### Set Namespace-Level Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-alpha-quota
  namespace: team-alpha
spec:
  hard:
    requests.cpu: "20"
    requests.memory: "40Gi"
    limits.cpu: "40"
    limits.memory: "80Gi"
    pods: "100"
    services: "20"
    persistentvolumeclaims: "30"
```

### Set Default Resource Limits with LimitRange

LimitRange objects ensure that every container has resource requests and limits, even if the developer forgets to specify them:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: team-alpha
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    max:
      cpu: "4"
      memory: "8Gi"
    min:
      cpu: "50m"
      memory: "64Mi"
    type: Container
```

To verify quotas are enforced, run:

```bash
kubectl describe resourcequota team-alpha-quota -n team-alpha
```

## Step 5: Monitor Costs with Kubecost

Visibility is the foundation of cost control. Kubecost provides real-time cost allocation at the namespace, deployment, and pod level.

### Install Kubecost

```bash
helm install kubecost cost-analyzer \
  --repo https://kubecost.github.io/cost-analyzer/ \
  --namespace kubecost \
  --create-namespace \
  --set kubecostToken="YOUR_TOKEN" \
  --set prometheus.server.retention=30d
```

### Query Cost Data via the API

Kubecost exposes an API you can integrate into your dashboards and alerting:

```bash
# Get cost allocation by namespace for the last 7 days
curl -s "http://kubecost.internal/model/allocation?window=7d&aggregate=namespace" \
  | jq '.data[0] | to_entries[] | {namespace: .key, totalCost: .value.totalCost}'

# Get idle cost -- resources provisioned but unused
curl -s "http://kubecost.internal/model/allocation?window=7d&aggregate=cluster" \
  | jq '.data[0] | to_entries[] | {idle: .value.idleCost, total: .value.totalCost}'
```

### Set Up Cost Alerts

Configure alerts to notify teams when their spend exceeds thresholds:

```yaml
apiVersion: kubecost.com/v1alpha1
kind: Alert
metadata:
  name: namespace-budget-alert
spec:
  type: budget
  threshold: 1000
  window: 30d
  aggregation: namespace
  filter: "team-alpha"
  notifications:
  - type: slack
    url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Build a Cost Governance Dashboard

Combine Kubecost data with Grafana to build a dashboard that tracks:

- Cost per namespace over time
- Resource efficiency ratio (actual usage / requested resources)
- Idle resource cost by node pool
- Spot vs. on-demand cost breakdown
- Top 10 most expensive deployments

## Putting It All Together: A Phased Approach

Trying to implement all five strategies at once is a recipe for operational chaos. Here is a phased approach:

**Phase 1 (Week 1-2): Visibility.** Install Kubecost and instrument all namespaces. Identify the top 10 most wasteful deployments by comparing requests to actual usage. This alone reveals where 80% of the savings are.

**Phase 2 (Week 3-4): Right-sizing.** Apply VPA in recommendation mode to generate right-sizing suggestions. Review and apply the changes to your top 10 wasteful deployments. Expect 30-40% savings on those workloads.

**Phase 3 (Week 5-6): Autoscaling.** Roll out HPA for all stateless services. Deploy Karpenter to replace the cluster autoscaler and enable node consolidation.

**Phase 4 (Week 7-8): Spot instances.** Identify spot-eligible workloads and migrate them. Start with non-production environments, then move to production stateless workloads.

**Phase 5 (Ongoing): Governance.** Enforce resource quotas and limit ranges across all namespaces. Set up cost alerts. Integrate cost reviews into your sprint planning process.

## Expected Results

Based on data from organizations that have followed this approach:

| Strategy | Typical Savings | Implementation Effort |
|----------|----------------|-----------------------|
| Right-sizing | 20-35% | Low |
| HPA + VPA | 15-25% | Medium |
| Karpenter consolidation | 10-20% | Medium |
| Spot instances | 20-40% | Medium |
| Resource quotas | 5-10% (prevention) | Low |

The savings compound. A cluster spending $50,000/month can typically reduce that to $20,000-$30,000/month within two months by applying these strategies systematically.

## Common Pitfalls to Avoid

- **Setting CPU limits too aggressively.** CPU limits cause throttling, which increases latency. Many teams now omit CPU limits entirely and rely on CPU requests for scheduling, combined with HPA to scale out.
- **Running VPA in Auto mode on critical services without testing.** Start with "Off" or "Initial" mode to review recommendations before applying them automatically.
- **Ignoring persistent volume costs.** EBS volumes and their snapshots can account for 15-20% of your total Kubernetes bill. Audit and clean up unused PVCs regularly.
- **Forgetting egress costs.** Cross-AZ and cross-region traffic adds up. Use topology-aware routing to keep traffic local where possible.

Right-sizing and autoscaling are not one-time tasks. Traffic patterns change, codebases evolve, and new services get deployed constantly. Schedule quarterly cost reviews and keep your monitoring in place to sustain the savings over time.
